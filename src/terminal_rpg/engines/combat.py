"""
Combat engine - handles turn-based combat loop.
"""

import logging
import sys

from ..llm.combat.dm_combat import DMCombatNPC, DMCombatPlayer
from ..storage.database import Database
from ..storage.models import Disposition, GameState
from ..storage.repositories import (
    BattleParticipantRepository,
    BattleRepository,
    NPCRepository,
    PlayerRepository,
)
from ..ui.battle_display import display_combat_status, display_combat_victory, display_game_over
from ..ui.game_display import GameDisplay

logger = logging.getLogger(__name__)


class CombatEngine:
    """
    Combat engine that coordinates turn-based combat between player and NPCs.
    """

    def __init__(self):
        """Initialize combat engine."""
        pass

    def run_combat_loop(
        self, game_state: GameState, db: Database, display: GameDisplay, status=None
    ) -> None:
        """
        Main combat loop - runs until combat ends.

        Args:
            game_state: Current game state with active battle
            db: Database connection
            display: GameDisplay instance for UI
            status: Optional Rich Status object (not used in combat)
        """
        if game_state.battle is None:
            logger.error("run_combat_loop called with no active battle")
            return

        logger.info(f"Starting combat loop for battle: {game_state.battle.name}")

        # Initialize combat DMs
        npc_dm = DMCombatNPC(db)
        player_dm = DMCombatPlayer(db)

        participant_repo = BattleParticipantRepository(db)
        npc_repo = NPCRepository(db)
        battle_repo = BattleRepository(db)

        # Main combat loop
        while True:
            # Get all active participants sorted by turn order
            participants = participant_repo.get_by_battle(game_state.battle.id)

            # Filter active participants and get NPC data
            active_participants = []
            for participant in participants:
                if not participant.is_active:
                    continue

                if participant.player_id is not None:
                    # Player
                    active_participants.append((participant, None))
                elif participant.npc_id is not None:
                    # NPC - check if still alive
                    npc = npc_repo.get_by_id(participant.npc_id)
                    if npc and npc.hp > 0:
                        active_participants.append((participant, npc))
                    else:
                        # NPC died, mark inactive
                        participant_repo.update_is_active(
                            game_state.battle.id,
                            npc_id=participant.npc_id,
                            player_id=None,
                            is_active=False,
                        )

            # Sort by turn order
            active_participants.sort(key=lambda x: x[0].turn_order or 999)

            # Check if combat should end before starting turns
            end_status = self._check_combat_end(game_state, db)
            if end_status == "player_death":
                self._end_combat_death(game_state)
                return
            elif end_status == "victory":
                self._end_combat_victory(game_state, db)
                return

            # Get starting turn index from battle state
            current_turn_index = game_state.battle.current_turn_index
            num_participants = len(active_participants)

            # If the saved index is out of bounds, reset to 0
            if current_turn_index >= num_participants:
                current_turn_index = 0
                game_state.battle.current_turn_index = 0
                battle_repo.update_turn_index(game_state.battle.id, 0)

            # Process turns starting from the saved index
            for i in range(num_participants):
                # Calculate actual index (wraps around)
                idx = (current_turn_index + i) % num_participants
                participant, npc = active_participants[idx]

                # Re-check if participant is still active (may have been killed during this round)
                fresh_participant = participant_repo.get_by_battle_and_participant(
                    game_state.battle.id, npc_id=participant.npc_id, player_id=participant.player_id
                )
                if fresh_participant is None or not fresh_participant.is_active:
                    # Participant was killed/removed during this round, skip their turn
                    continue

                # Calculate next turn index (for saving after turn completes)
                next_idx = (idx + 1) % num_participants

                if participant.player_id is not None:
                    # Player's turn - update index before turn (player interaction is immediate)
                    game_state.battle.current_turn_index = idx
                    battle_repo.update_turn_index(game_state.battle.id, idx)

                    self._handle_player_turn(
                        active_participants, game_state, db, display, player_dm
                    )

                    # Check if combat ended (escape or victory)
                    if game_state.battle is None:
                        return  # Combat escaped

                    end_status = self._check_combat_end(game_state, db)
                    if end_status == "victory":
                        self._end_combat_victory(game_state, db)
                        return

                    # Advance to next turn after player completes
                    game_state.battle.current_turn_index = next_idx
                    battle_repo.update_turn_index(game_state.battle.id, next_idx)

                elif npc is not None:
                    # NPC's turn - update index before turn starts
                    game_state.battle.current_turn_index = idx
                    battle_repo.update_turn_index(game_state.battle.id, idx)

                    self._handle_npc_turn(npc, active_participants, game_state, db, npc_dm)

                    # Check if combat ended (player death or all enemies dead)
                    end_status = self._check_combat_end(game_state, db)
                    if end_status == "player_death":
                        self._end_combat_death(game_state)
                        return
                    elif end_status == "victory":
                        self._end_combat_victory(game_state, db)
                        return

                    # Advance to next turn AFTER NPC completes but BEFORE the "Press Enter" prompt
                    # This ensures if user reloads during the prompt, the next participant goes
                    game_state.battle.current_turn_index = next_idx
                    battle_repo.update_turn_index(game_state.battle.id, next_idx)

                    # Now wait for player to continue (after turn counter is advanced)
                    from rich.console import Console

                    console = Console()
                    console.print()
                    console.print("[dim]Press Enter to continue...[/dim]")
                    input()

            # Round complete - turn counter already points to first participant via wrap-around

    def _handle_player_turn(
        self,
        active_participants: list,
        game_state: GameState,
        db: Database,
        display: GameDisplay,
        player_dm: DMCombatPlayer,
    ) -> None:
        """
        Handle the player's combat turn.

        Args:
            active_participants: List of (participant, npc_or_none) tuples
            game_state: Current game state
            db: Database connection
            display: GameDisplay instance
            player_dm: Player combat DM
        """
        # Display combat status (with combatants list for player's turn)
        display_combat_status(
            game_state.battle,
            active_participants,
            game_state.player,
            game_state.player.name,
            is_player_turn=True,
        )

        # Get player input
        display.console.print("[bold green]Your turn![/bold green]")
        display.console.print(
            "[dim]Type your action (e.g., 'attack goblin with sword', 'try to escape')[/dim]"
        )
        player_input = display.get_user_input()

        if not player_input:
            display.console.print("[yellow]No action taken.[/yellow]")
            return

        # Get action from player DM
        result, error = player_dm.get_player_action(player_input, game_state, None)

        if error:
            display.console.print(f"[red]Error: {error}[/red]")
            display.console.print("[yellow]Please try again.[/yellow]")
            # Re-try the turn
            self._handle_player_turn(active_participants, game_state, db, display, player_dm)
            return

        # Display result (if it's an error message about invalid weapon, let player retry)
        if result.startswith("Error:"):
            display.console.print(f"[yellow]{result}[/yellow]")
            # Re-try the turn
            self._handle_player_turn(active_participants, game_state, db, display, player_dm)
            return

        # Action succeeded
        logger.info(f"Player action result: {result}")

    def _handle_npc_turn(
        self,
        npc,
        active_participants: list,
        game_state: GameState,
        db: Database,
        npc_dm: DMCombatNPC,
    ) -> None:
        """
        Handle an NPC's combat turn (without waiting for player to continue).

        Args:
            npc: NPC taking the turn
            active_participants: List of (participant, npc_or_none) tuples
            game_state: Current game state
            db: Database connection
            npc_dm: NPC combat DM
        """
        from rich.console import Console

        console = Console()

        # Display combat status (without combatants list for NPC turns - cleaner display)
        display_combat_status(
            game_state.battle,
            active_participants,
            game_state.player,
            npc.name,
            is_player_turn=False,
        )

        # Show whose turn it is
        disposition_color = "cyan" if npc.disposition == Disposition.ALLY else "red"
        console.print(f"[{disposition_color}]{npc.name}'s turn![/{disposition_color}]")
        console.print()

        # Get action from NPC DM
        result, error = npc_dm.get_npc_action(npc, game_state, None)

        if error:
            logger.error(f"NPC turn error: {error}")
            console.print(f"[red]Error during {npc.name}'s turn: {error}[/red]")
            return

        # Action succeeded
        logger.info(f"NPC action result: {result}")

    def _check_combat_end(self, game_state: GameState, db: Database) -> str | None:
        """
        Check if combat should end.

        Args:
            game_state: Current game state
            db: Database connection

        Returns:
            "player_death" if player died
            "victory" if all hostile NPCs defeated
            None if combat continues
        """
        # Check if player died
        if game_state.player.hp <= 0:
            return "player_death"

        # Check if all hostile NPCs are defeated
        participant_repo = BattleParticipantRepository(db)
        npc_repo = NPCRepository(db)

        participants = participant_repo.get_by_battle(game_state.battle.id)

        hostile_alive = False
        for participant in participants:
            if not participant.is_active:
                continue

            if participant.npc_id is not None:
                npc = npc_repo.get_by_id(participant.npc_id)
                if npc and npc.disposition == Disposition.HOSTILE and npc.hp > 0:
                    hostile_alive = True
                    break

        if not hostile_alive:
            return "victory"

        return None

    def _end_combat_victory(self, game_state: GameState, db: Database) -> None:
        """
        Handle combat victory - award XP and gold, display victory screen.

        Args:
            game_state: Current game state
            db: Database connection
        """
        participant_repo = BattleParticipantRepository(db)
        npc_repo = NPCRepository(db)
        player_repo = PlayerRepository(db)

        # Get all defeated hostile NPCs
        participants = participant_repo.get_by_battle(game_state.battle.id)

        defeated_enemies = []
        total_xp = 0
        total_gold = 0

        for participant in participants:
            if participant.npc_id is not None:
                npc = npc_repo.get_by_id(participant.npc_id)
                if npc and npc.disposition == Disposition.HOSTILE and npc.hp <= 0:
                    defeated_enemies.append(npc.name)
                    # XP already awarded during combat, but gold is collected now
                    total_gold += npc.gold

        # Award gold to player
        if total_gold > 0:
            new_gold = game_state.player.gold + total_gold
            game_state.player.gold = new_gold
            player_repo.update_gold(game_state.player.id, new_gold)

        # Display victory screen
        display_combat_victory(defeated_enemies, total_xp, total_gold)

        # End combat
        game_state.battle = None
        logger.info("Combat ended in victory")

    def _end_combat_death(self, game_state: GameState) -> None:
        """
        Handle player death - display game over and exit to main menu.

        Args:
            game_state: Current game state
        """
        # Display game over screen
        display_game_over(game_state.player)

        # Exit to main menu
        logger.info("Player died in combat - game over")
        sys.exit(0)  # Exit the entire program (will return to main menu on restart)
