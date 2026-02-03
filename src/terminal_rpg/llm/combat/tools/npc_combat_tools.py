"""
Combat attack tools for NPC and player actions.
"""

from rich.console import Console

from ....engines.utils import calculate_player_ac, roll_attack, roll_damage
from ....storage.database import Database
from ....storage.models import Disposition, GameState
from ....storage.repositories import (
    BattleParticipantRepository,
    NPCRepository,
    PlayerRepository,
)
from ....ui.battle_display import display_attack_sequence

console = Console()

# ===== NPC ATTACK TOOL =====
NPC_ATTACK_TOOL = {
    "name": "attack_target",
    "description": "Attack a target in combat. Use this to make the NPC attack an opponent (player or player-allied NPC).",
    "input_schema": {
        "type": "object",
        "properties": {
            "target_name": {
                "type": "string",
                "description": "Name of the target to attack (e.g., player name or ally NPC name). Must be an exact match.",
            },
            "attack_action": {
                "type": "string",
                "description": "A vivid, complete description of the attack action as a full sentence. MUST include both the attacker's name and target's name. Make it immersive and descriptive.",
            },
        },
        "required": ["target_name", "attack_action"],
    },
}


def npc_attack_execute(
    attacking_npc_id: int,
    target_name: str,
    attack_action: str,
    game_state: GameState,
    db: Database,
    status=None,
) -> str:
    """
    Execute an NPC attack on a target.

    Args:
        attacking_npc_id: ID of the attacking NPC
        target_name: Name of the target (player or ally NPC)
        attack_action: Descriptive attack action text
        game_state: Current game state
        db: Database connection
        status: Optional Rich Status object to pause during display

    Returns:
        Result message for the DM
    """
    # Pause spinner during display
    if status:
        status.stop()

    try:
        npc_repo = NPCRepository(db)
        player_repo = PlayerRepository(db)
        participant_repo = BattleParticipantRepository(db)

        # Get attacking NPC
        attacker = npc_repo.get_by_id(attacking_npc_id)
        if not attacker:
            return f"Error: Attacking NPC with ID {attacking_npc_id} not found."

        # Find target (check player first, then NPCs)
        target_is_player = False
        target_npc = None
        target_ac = 10

        if (
            target_name.lower() == game_state.player.name.lower()
        ):  # TODO: Add "player" to the comparison
            # Target is player
            target_is_player = True
            target_ac = calculate_player_ac(game_state.player, game_state.equipped_armor)
        else:
            # Search for NPC target in battle
            participants = participant_repo.get_by_battle(game_state.battle.id)
            for participant in participants:
                if participant.npc_id:
                    npc = npc_repo.get_by_id(participant.npc_id)
                    if npc and npc.name.lower() == target_name.lower():
                        target_npc = npc
                        target_ac = npc.ac
                        break

            if not target_npc:
                return f"Error: Target '{target_name}' not found in battle."  # TODO: Add available targets to the error message

        # Roll attack
        attack_roll, attack_total, is_hit, is_critical = roll_attack(attacker.attack_mod, target_ac)

        # Roll damage if hit
        damage = 0
        effective_dice_count = attacker.damage_dice_count
        if is_hit:
            damage = roll_damage(
                attacker.damage_dice_count, attacker.damage_dice_sides.value, is_critical
            )
            # Double dice count for display if critical
            if is_critical:
                effective_dice_count = attacker.damage_dice_count * 2

        # Calculate HP changes before display (for player targets)
        target_old_hp = None
        target_new_hp = None
        if is_hit and damage > 0 and target_is_player:
            target_old_hp = game_state.player.hp
            target_new_hp = max(0, target_old_hp - damage)

        # Display attack sequence with damage dice info for animation
        # Determine if attacker is ally (from player's perspective)
        attacker_is_ally = attacker.disposition == Disposition.ALLY

        display_attack_sequence(
            attack_action,
            attack_roll,
            attack_total,
            is_hit,
            target_ac,
            damage,
            effective_dice_count,
            attacker.damage_dice_sides.value,
            is_critical,
            attacker_is_ally,
            target_old_hp,
            target_new_hp,
        )

        # Apply damage
        if is_hit and damage > 0:
            if target_is_player:
                # Damage player (HP already calculated above)
                old_hp = game_state.player.hp
                new_hp = max(0, old_hp - damage)
                game_state.player.hp = new_hp
                player_repo.update_hp(game_state.player.id, new_hp)

                result_msg = f"{attacker.name} hit {game_state.player.name} for {damage} damage! {game_state.player.name} HP: {old_hp} → {new_hp}"

                # Check if player died
                if new_hp == 0:
                    result_msg += f"\n💀 {game_state.player.name} has been defeated!"

            else:
                # Damage NPC
                old_hp = target_npc.hp
                new_hp = max(0, old_hp - damage)
                target_npc.hp = new_hp
                npc_repo.update_hp(target_npc.id, new_hp)

                result_msg = f"{attacker.name} hit {target_npc.name} for {damage} damage! {target_npc.name} HP: {old_hp} → {new_hp}"

                # Check if target died
                if new_hp == 0:
                    # Mark as inactive in battle
                    participant_repo.update_is_active(
                        game_state.battle.id, npc_id=target_npc.id, player_id=None, is_active=False
                    )

                    # Award XP to attacker's team (but not to NPCs themselves)
                    # XP will be handled by combat engine for proper distribution
                    result_msg += f"\n💀 {target_npc.name} has been defeated!"

        else:
            result_msg = f"{attacker.name} missed {target_name}!"

        return result_msg

    finally:
        # Resume spinner
        if status:
            status.start()


# ===== PLAYER ATTACK TOOL =====
PLAYER_ATTACK_TOOL = {
    "name": "player_attack",
    "description": "Player attacks an enemy with an equipped weapon. The weapon must be equipped in the player's inventory.",
    "input_schema": {
        "type": "object",
        "properties": {
            "weapon_name": {
                "type": "string",
                "description": "Name of the equipped weapon to use for the attack. Must be an exact match.",
            },
            "target_name": {
                "type": "string",
                "description": "Name of the hostile NPC to attack. Must be an exact match.",
            },
            "attack_action": {
                "type": "string",
                "description": "A vivid, complete description of the attack action as a full sentence. MUST include target's name and refer to the player as 'you'. Make it immersive and descriptive.",
            },
        },
        "required": ["weapon_name", "target_name", "attack_action"],
    },
}
