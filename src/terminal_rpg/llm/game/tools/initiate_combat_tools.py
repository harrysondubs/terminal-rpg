"""
Initiate combat tool for DM - handles transitioning into battle mode.
"""

import random

from rich.console import Console

from ....storage.database import Database
from ....storage.models import GameState

console = Console()

# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "initiate_combat",
    "description": "Start a combat encounter. Use this when enemies appear or the player enters battle. This will transition the game into combat mode and generate the battle with NPCs.",
    "input_schema": {
        "type": "object",
        "properties": {
            "context": {
                "type": "string",
                "description": "Description of the battle context and setting (e.g., 'The player is ambushed by bandits on the forest road')",
            },
            "opponents": {
                "type": "string",
                "description": "Description of the enemy combatants (e.g., '3 goblin warriors and 1 goblin shaman')",
            },
            "allies": {
                "type": "string",
                "description": "Optional description of any allies fighting alongside the player (e.g., 'a friendly guard captain')",
            },
        },
        "required": ["context", "opponents"],
    },
}


def execute(
    context: str,
    opponents: str,
    game_state: GameState,
    db: Database,
    allies: str | None = None,
    status=None,
) -> str:
    """
    Execute combat initiation - generate battle and NPCs, then display battle start.

    Args:
        context: Description of the battle context/setting
        opponents: Description of enemy combatants
        game_state: Current game state
        db: Database connection
        allies: Optional description of allied combatants
        status: Optional Rich Status object to pause during interactive display

    Returns:
        Result message for the DM
    """
    # Import here to avoid circular imports
    from ....ui.battle_display import display_battle_start
    from ...combat.generate_battle import (
        generate_battle_from_context,
        generate_battle_npcs_from_context,
        get_battle_npcs,
    )

    # Pause the "DM is thinking..." spinner during battle generation and display
    if status:
        status.stop()

    try:
        # Step 1: Generate the battle
        console.print("[dim]Generating battle...[/dim]")
        battle_id = generate_battle_from_context(context, opponents, allies, game_state, db)

        if battle_id is None:
            error_msg = "Error: Failed to generate battle."
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

        # Step 2: Generate NPCs for the battle
        console.print("[dim]Generating combatants...[/dim]")
        success = generate_battle_npcs_from_context(
            battle_id, context, opponents, allies, game_state, db
        )

        if not success:
            error_msg = "Error: Failed to generate battle NPCs."
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

        # Step 3: Retrieve the battle and NPCs
        from ....storage.repositories import BattleRepository

        battle_repo = BattleRepository(db)
        battle = battle_repo.get_by_id(battle_id)

        if not battle:
            error_msg = f"Error: Could not retrieve battle with ID {battle_id}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg

        # Get NPCs separated by disposition
        ally_npcs, opponent_npcs = get_battle_npcs(battle_id, db)

        # Step 4: Update game state with battle
        game_state.battle = battle

        # Step 5: Display battle start
        display_battle_start(battle, ally_npcs, opponent_npcs)

        # Step 6: Add player to battle participants
        from ....storage.repositories import BattleParticipantRepository

        participant_repo = BattleParticipantRepository(db)
        participant_repo.add_participant(
            battle_id=battle_id, player_id=game_state.player.id, is_active=True
        )

        # Step 7: Roll initiative for all participants
        _roll_initiative_for_battle(battle_id, game_state, db, status)

        return f"Combat initiated: '{battle.name}' with {len(opponent_npcs)} opponent(s) and {len(ally_npcs)} ally/allies. Turn order established."

    except Exception as e:
        error_msg = f"Error initiating combat: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

    finally:
        # Resume the "DM is thinking..." spinner
        if status:
            status.start()


def _roll_initiative_for_battle(
    battle_id: int, game_state: GameState, db: Database, status=None
) -> None:
    """
    Roll initiative for all battle participants and assign turn order.

    Args:
        battle_id: ID of the battle
        game_state: Current game state
        db: Database connection
        status: Optional Rich Status object (already stopped)
    """
    from ....storage.repositories import BattleParticipantRepository, NPCRepository
    from ....ui.battle_display import (
        display_initiative_header,
        display_npc_initiative,
        display_player_initiative_prompt,
        display_turn_order,
    )

    participant_repo = BattleParticipantRepository(db)
    npc_repo = NPCRepository(db)

    # Get all participants
    participants = participant_repo.get_by_battle(battle_id)

    # Display header
    display_initiative_header()

    # Roll initiative for NPCs (behind the scenes)
    for participant in participants:
        if participant.npc_id is not None:
            # This is an NPC
            npc = npc_repo.get_by_id(participant.npc_id)
            if npc:
                # Roll d20 + initiative modifier
                initiative_roll = random.randint(1, 20) + npc.initiative_mod

                # Update participant with initiative roll
                participant_repo.update_initiative(
                    battle_id=battle_id,
                    npc_id=participant.npc_id,
                    player_id=None,
                    initiative_roll=initiative_roll,
                )

                # Display NPC initiative
                display_npc_initiative(npc.name, initiative_roll)

    # Player rolls initiative with display
    player = game_state.player
    roll, total = display_player_initiative_prompt(player)

    # Update player participant with initiative roll
    participant_repo.update_initiative(
        battle_id=battle_id, npc_id=None, player_id=player.id, initiative_roll=total
    )

    # Get all participants again (with updated initiative)
    participants = participant_repo.get_by_battle(battle_id)

    # Sort by initiative (highest first)
    participants_with_initiative = []
    for participant in participants:
        if participant.initiative_roll is not None:
            participants_with_initiative.append(participant)

    # Sort by initiative roll descending
    participants_with_initiative.sort(key=lambda p: p.initiative_roll, reverse=True)

    # Assign turn order and prepare display data
    participants_with_npcs = []
    for idx, participant in enumerate(participants_with_initiative, start=1):
        # Update turn order in database
        participant_repo.update_turn_order(
            battle_id=battle_id,
            npc_id=participant.npc_id,
            player_id=participant.player_id,
            turn_order=idx,
        )

        # Fetch NPC data if needed
        npc = None
        if participant.npc_id is not None:
            npc = npc_repo.get_by_id(participant.npc_id)

        participants_with_npcs.append((participant, npc))

    # Display turn order
    display_turn_order(participants_with_npcs, player.name)
