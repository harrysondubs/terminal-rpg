"""
Combat DM controllers using Claude API.
Handles NPC and player combat actions through AI.
"""

import logging

from anthropic import APIError

from ...storage.database import Database
from ...storage.models import Disposition, GameState
from ...storage.repositories import BattleParticipantRepository, NPCRepository
from ..claude_api import ClaudeModel, create_message
from ..game.message_history import (
    reconstruct_battle_message_history,
    save_assistant_message,
    save_tool_call,
    save_tool_results,
    save_user_message,
)
from .prompts.dm_combat_prompts import create_npc_combat_prompt, create_player_combat_prompt
from .tools.attack_tools import (
    ESCAPE_COMBAT_TOOL,
    NPC_ATTACK_TOOL,
    PLAYER_ATTACK_TOOL,
    escape_combat_execute,
    npc_attack_execute,
    player_attack_execute,
)

logger = logging.getLogger(__name__)


class DMCombatNPC:
    """
    AI controller for NPC combat turns.
    Uses forced tool calling to make NPCs attack intelligently.
    """

    def __init__(self, db: Database):
        """
        Initialize NPC combat DM.

        Args:
            db: Connected Database instance
        """
        self.db = db

    def get_npc_action(self, npc, game_state: GameState, status=None) -> tuple[str, str | None]:
        """
        Get NPC's combat action via AI decision.

        Args:
            npc: NPC object taking the turn
            game_state: Current game state
            status: Optional Rich Status object to pause during attack

        Returns:
            Tuple of (result_message, error_message)
            - result_message: Result of the action (empty string if error)
            - error_message: Error message if failed, None if successful
        """
        # Get available targets (player and ally NPCs)
        available_targets = self._get_available_targets(npc, game_state)

        if not available_targets:
            return "No valid targets available.", None

        # Create system prompt
        system_prompt = create_npc_combat_prompt(npc, available_targets, game_state)

        # Reconstruct message history for this battle
        messages = reconstruct_battle_message_history(game_state.battle.id, self.db)

        # Create user message
        user_message = f"{npc.name}'s turn. Choose a target and attack!"
        messages.append({"role": "user", "content": user_message})

        # Save user message to log
        save_user_message(
            game_state.campaign.id,
            game_state.world.id,
            game_state.location.id,
            user_message,
            self.db,
            battle_id=game_state.battle.id,
        )

        try:
            # Call Claude API with forced tool use
            response = create_message(
                messages=messages,
                model=ClaudeModel.SONNET_4_5,
                system=system_prompt,
                max_tokens=2048,
                temperature=1.0,
                tools=[NPC_ATTACK_TOOL],
                tool_choice={"type": "tool", "name": "attack_target"},
            )

            # Extract tool use block
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

            if not tool_use_blocks:
                logger.error("No tool use block found in NPC combat response")
                return "", "AI did not choose an action"

            tool_block = tool_use_blocks[0]
            tool_input = tool_block.input

            # Save the tool call
            content_blocks = []
            for block in response.content:
                if hasattr(block, "text"):
                    content_blocks.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            save_tool_call(
                game_state.campaign.id,
                game_state.world.id,
                game_state.location.id,
                response.id,
                content_blocks,
                self.db,
                battle_id=game_state.battle.id,
            )

            # Execute the attack
            result = npc_attack_execute(
                npc.id,
                tool_input["target_name"],
                tool_input["attack_action"],
                game_state,
                self.db,
                status,
            )

            # Save tool result
            tool_results = [
                {"type": "tool_result", "tool_use_id": tool_block.id, "content": result}
            ]
            save_tool_results(
                game_state.campaign.id,
                game_state.world.id,
                game_state.location.id,
                tool_results,
                self.db,
                battle_id=game_state.battle.id,
            )

            return result, None

        except APIError as e:
            logger.error(f"API Error during NPC combat: {e}")
            return "", f"API Error: {e}"
        except Exception as e:
            logger.error(f"Error during NPC combat turn: {e}", exc_info=True)
            return "", f"Error: {e}"

    def _get_available_targets(self, attacker_npc, game_state: GameState) -> list:
        """
        Get list of valid targets for an NPC.

        Args:
            attacker_npc: NPC doing the attacking
            game_state: Current game state

        Returns:
            List of target dictionaries with 'is_player' flag and 'npc' object
        """
        participant_repo = BattleParticipantRepository(self.db)
        npc_repo = NPCRepository(self.db)

        targets = []

        # Get all active participants
        participants = participant_repo.get_by_battle(game_state.battle.id)

        for participant in participants:
            if not participant.is_active:
                continue

            if participant.player_id is not None:
                # Player is always a valid target if attacker is hostile
                if attacker_npc.disposition == Disposition.HOSTILE:
                    targets.append({"is_player": True, "npc": None})
            elif participant.npc_id is not None and participant.npc_id != attacker_npc.id:
                # Check if this NPC is a valid target
                target_npc = npc_repo.get_by_id(participant.npc_id)
                if target_npc:
                    # Hostile NPCs attack player and allies
                    # Ally NPCs attack hostile NPCs
                    if attacker_npc.disposition == Disposition.HOSTILE:
                        if target_npc.disposition == Disposition.ALLY:
                            targets.append({"is_player": False, "npc": target_npc})
                    elif (
                        attacker_npc.disposition == Disposition.ALLY
                        and target_npc.disposition == Disposition.HOSTILE
                    ):
                        targets.append({"is_player": False, "npc": target_npc})

        return targets


class DMCombatPlayer:
    """
    AI controller for interpreting player combat actions.
    Uses player input to decide which tool to use.
    """

    def __init__(self, db: Database):
        """
        Initialize player combat DM.

        Args:
            db: Connected Database instance
        """
        self.db = db

    def get_player_action(
        self, player_input: str, game_state: GameState, status=None
    ) -> tuple[str, str | None]:
        """
        Interpret player's combat action via AI.

        Args:
            player_input: Player's text input describing their action
            game_state: Current game state
            status: Optional Rich Status object to pause during attack

        Returns:
            Tuple of (result_message, error_message)
            - result_message: Result of the action (empty string if error)
            - error_message: Error message if failed, None if successful
        """
        # Get available hostile targets
        available_targets = self._get_hostile_npcs(game_state)

        # Create system prompt
        system_prompt = create_player_combat_prompt(game_state, available_targets)

        # Reconstruct message history for this battle
        messages = reconstruct_battle_message_history(game_state.battle.id, self.db)

        # Add player input
        messages.append({"role": "user", "content": player_input})

        # Save user message to log
        save_user_message(
            game_state.campaign.id,
            game_state.world.id,
            game_state.location.id,
            player_input,
            self.db,
            battle_id=game_state.battle.id,
        )

        try:
            # Call Claude API with both tools available
            response = create_message(
                messages=messages,
                model=ClaudeModel.SONNET_4_5,
                system=system_prompt,
                max_tokens=2048,
                temperature=1.0,
                tools=[PLAYER_ATTACK_TOOL, ESCAPE_COMBAT_TOOL],
            )

            # Extract tool use block
            tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

            if not tool_use_blocks:
                # No tool used - AI couldn't interpret action
                text_blocks = [block.text for block in response.content if hasattr(block, "text")]
                response_text = (
                    "\n".join(text_blocks) if text_blocks else "Could not interpret action."
                )

                # Save assistant message
                save_assistant_message(
                    game_state.campaign.id,
                    game_state.world.id,
                    game_state.location.id,
                    response_text,
                    self.db,
                    battle_id=game_state.battle.id,
                )

                return response_text, None

            tool_block = tool_use_blocks[0]
            tool_name = tool_block.name
            tool_input = tool_block.input

            # Save the tool call
            content_blocks = []
            for block in response.content:
                if hasattr(block, "text"):
                    content_blocks.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            save_tool_call(
                game_state.campaign.id,
                game_state.world.id,
                game_state.location.id,
                response.id,
                content_blocks,
                self.db,
                battle_id=game_state.battle.id,
            )

            # Execute the appropriate tool
            if tool_name == "player_attack":
                result = player_attack_execute(
                    tool_input["weapon_name"],
                    tool_input["target_name"],
                    tool_input["attack_action"],
                    game_state,
                    self.db,
                    status,
                )
            elif tool_name == "escape_combat":
                result = escape_combat_execute(
                    tool_input["ability_type"],
                    tool_input["difficulty_class"],
                    tool_input["failure_damage"],
                    game_state,
                    self.db,
                    status,
                )
            else:
                result = f"Unknown tool: {tool_name}"

            # Save tool result
            tool_results = [
                {"type": "tool_result", "tool_use_id": tool_block.id, "content": result}
            ]
            save_tool_results(
                game_state.campaign.id,
                game_state.world.id,
                game_state.location.id,
                tool_results,
                self.db,
                battle_id=game_state.battle.id,
            )

            return result, None

        except APIError as e:
            logger.error(f"API Error during player combat: {e}")
            return "", f"API Error: {e}"
        except Exception as e:
            logger.error(f"Error during player combat turn: {e}", exc_info=True)
            return "", f"Error: {e}"

    def _get_hostile_npcs(self, game_state: GameState) -> list:
        """
        Get list of active hostile NPCs in battle.

        Args:
            game_state: Current game state

        Returns:
            List of hostile NPC objects
        """
        participant_repo = BattleParticipantRepository(self.db)
        npc_repo = NPCRepository(self.db)

        hostile_npcs = []

        # Get all active participants
        participants = participant_repo.get_by_battle(game_state.battle.id)

        for participant in participants:
            if not participant.is_active:
                continue

            if participant.npc_id is not None:
                npc = npc_repo.get_by_id(participant.npc_id)
                if npc and npc.disposition == Disposition.HOSTILE:
                    hostile_npcs.append(npc)

        return hostile_npcs
