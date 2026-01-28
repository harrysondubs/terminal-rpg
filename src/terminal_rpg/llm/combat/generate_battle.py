"""
Battle generation using Claude API with forced tool calls.
Generates battle encounters and NPCs from natural language descriptions.
"""

import logging
import re

from anthropic import APIError

from ...storage.database import Database
from ...storage.models import NPC, Disposition, GameState
from ...storage.repositories import BattleParticipantRepository, NPCRepository
from ..claude_api import ClaudeModel, create_message
from .prompts.generate_battle_prompts import (
    create_generate_battle_prompt,
    create_generate_npcs_prompt,
)
from .tools.generate_battle_tools import GENERATE_BATTLE_NPCS_TOOL, GENERATE_BATTLE_TOOL

logger = logging.getLogger(__name__)


def generate_battle_from_context(
    context: str, opponents: str, allies: str | None, game_state: GameState, db: Database
) -> int | None:
    """
    Generate a battle from natural language context using LLM with forced tool call.

    Args:
        context: Battle context/setting description
        opponents: Description of enemy combatants
        allies: Optional description of allied combatants
        game_state: Current game state
        db: Database connection

    Returns:
        Battle ID if successful, None if failed
    """
    try:
        # Create system prompt
        system_prompt = create_generate_battle_prompt(context, opponents, allies, game_state)

        # Create user message
        user_message = "Create a battle encounter based on the context provided."

        # Call Claude API with forced tool use
        response = create_message(
            messages=[{"role": "user", "content": user_message}],
            model=ClaudeModel.SONNET_4_5,
            system=system_prompt,
            max_tokens=2048,
            temperature=1.0,
            tools=[GENERATE_BATTLE_TOOL],
            tool_choice={"type": "tool", "name": "generate_battle"},
        )

        # Extract tool use block
        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

        if not tool_use_blocks:
            logger.error("No tool use block found in battle generation response")
            return None

        tool_block = tool_use_blocks[0]
        tool_input = tool_block.input

        # Execute the tool manually to create the battle
        from .tools.generate_battle_tools import generate_battle_execute

        result = generate_battle_execute(
            tool_input["name"], tool_input["description"], game_state, db
        )

        # Parse battle_id from result message
        # Result format: "Successfully created battle 'Name' (ID: 123). ..."
        match = re.search(r"ID: (\d+)", result)
        if match:
            battle_id = int(match.group(1))
            logger.info(f"Successfully generated battle with ID: {battle_id}")
            return battle_id
        else:
            logger.error(f"Failed to parse battle_id from result: {result}")
            return None

    except APIError as e:
        logger.error(f"API Error during battle generation: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating battle: {e}", exc_info=True)
        return None


def generate_battle_npcs_from_context(
    battle_id: int,
    context: str,
    opponents: str,
    allies: str | None,
    game_state: GameState,
    db: Database,
) -> bool:
    """
    Generate NPCs for a battle from natural language context using LLM with forced tool call.

    Args:
        battle_id: ID of the battle to add NPCs to
        context: Battle context/setting description
        opponents: Description of enemy combatants
        allies: Optional description of allied combatants
        game_state: Current game state
        db: Database connection

    Returns:
        True if successful, False if failed
    """
    try:
        # Create system prompt (battle_id is managed in code, not passed to LLM)
        system_prompt = create_generate_npcs_prompt(context, opponents, allies, game_state)

        # Create user message
        user_message = (
            "Create NPCs based on the opponents and allies described in the battle context."
        )

        # Call Claude API with forced tool use
        response = create_message(
            messages=[{"role": "user", "content": user_message}],
            model=ClaudeModel.SONNET_4_5,
            system=system_prompt,
            max_tokens=4096,
            temperature=1.0,
            tools=[GENERATE_BATTLE_NPCS_TOOL],
            tool_choice={"type": "tool", "name": "generate_battle_npcs"},
        )

        # Extract tool use block
        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]

        if not tool_use_blocks:
            logger.error("No tool use block found in NPC generation response")
            return False

        tool_block = tool_use_blocks[0]
        tool_input = tool_block.input

        # Execute the tool manually to create the NPCs
        # We inject the battle_id here - the LLM doesn't need to handle it
        from .tools.generate_battle_tools import generate_battle_npcs_execute

        result = generate_battle_npcs_execute(battle_id, tool_input["npcs"], game_state, db)

        # Check if result indicates success
        if "Successfully created" in result:
            logger.info(f"Successfully generated NPCs for battle {battle_id}")
            return True
        else:
            logger.error(f"Failed to generate NPCs: {result}")
            return False

    except APIError as e:
        logger.error(f"API Error during NPC generation: {e}")
        return False
    except Exception as e:
        logger.error(f"Error generating NPCs: {e}", exc_info=True)
        return False


def get_battle_npcs(battle_id: int, db: Database) -> tuple[list[NPC], list[NPC]]:
    """
    Retrieve NPCs for a battle, separated by disposition.

    Args:
        battle_id: ID of the battle
        db: Database connection

    Returns:
        Tuple of (allies, opponents) where each is a list of NPC objects
    """
    participant_repo = BattleParticipantRepository(db)
    npc_repo = NPCRepository(db)

    # Get all participants
    participants = participant_repo.get_by_battle(battle_id)

    allies = []
    opponents = []

    for participant in participants:
        # Skip player participants (they have player_id instead of npc_id)
        if participant.npc_id is None:
            continue

        # Fetch the NPC
        npc = npc_repo.get_by_id(participant.npc_id)
        if npc:
            # Separate by disposition
            if npc.disposition == Disposition.ALLY:
                allies.append(npc)
            else:  # HOSTILE
                opponents.append(npc)

    return allies, opponents
