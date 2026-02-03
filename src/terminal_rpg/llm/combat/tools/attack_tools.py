"""
Combat attack tools for NPC and player actions.
"""

from rich.console import Console

from ....engines.utils import calculate_player_ac, roll_attack, roll_damage
from ....engines.xp_utils import get_level_from_xp
from ....storage.database import Database
from ....storage.models import Disposition, GameState
from ....storage.repositories import (
    BattleParticipantRepository,
    NPCRepository,
    PlayerRepository,
)
from ....ui.battle_display import display_attack_sequence, display_npc_defeated

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


def player_attack_execute(
    weapon_name: str,
    target_name: str,
    attack_action: str,
    game_state: GameState,
    db: Database,
    status=None,
) -> str:
    """
    Execute a player attack on a hostile NPC.

    Args:
        weapon_name: Name of weapon to use (must be equipped)
        target_name: Name of the hostile NPC target
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

        # Check if weapon is equipped
        weapon = None
        for equipped_weapon in game_state.equipped_weapons:
            if equipped_weapon.name.lower() == weapon_name.lower():
                weapon = equipped_weapon
                break

        if not weapon:
            equipped_names = [w.name for w in game_state.equipped_weapons]
            return f"Error: Weapon '{weapon_name}' is not equipped. Equipped weapons: {', '.join(equipped_names) if equipped_names else 'None'}. Please try again with an equipped weapon."

        # Find target NPC
        target_npc = None
        participants = participant_repo.get_by_battle(game_state.battle.id)
        for participant in participants:
            if participant.npc_id and participant.is_active:
                npc = npc_repo.get_by_id(participant.npc_id)
                if npc and npc.name.lower() == target_name.lower():
                    # Verify it's hostile
                    if npc.disposition != Disposition.HOSTILE:
                        return f"Error: {npc.name} is not hostile. You can only attack hostile enemies."
                    target_npc = npc
                    break

        if not target_npc:
            return f"Error: Hostile NPC '{target_name}' not found in battle or already defeated."  # TODO: Add available targets to the error message.

        # Calculate player's attack bonus (using strength for melee, dexterity for ranged)
        from ....engines.utils import calculate_ability_modifier
        from ....storage.models import WeaponType
        from ....ui.battle_display import display_player_attack_interactive

        if weapon.type == WeaponType.MELEE:
            attack_bonus = calculate_ability_modifier(game_state.player.strength)
        else:  # RANGED
            attack_bonus = calculate_ability_modifier(game_state.player.dexterity)

        # Display interactive attack with prompts and animations
        # This function handles rolling and displaying everything
        attack_roll, attack_total, is_hit, damage = display_player_attack_interactive(
            game_state.player.name,
            target_npc.name,
            attack_action,
            attack_bonus,
            target_npc.ac,
            weapon.damage_dice_count,
            weapon.damage_dice_sides.value,
        )

        # Apply damage
        if is_hit and damage > 0:
            old_hp = target_npc.hp
            new_hp = max(0, old_hp - damage)
            target_npc.hp = new_hp
            npc_repo.update_hp(target_npc.id, new_hp)

            result_msg = f"{game_state.player.name} hit {target_npc.name} for {damage} damage! {target_npc.name} HP: {old_hp} → {new_hp}"

            # Check if target died
            if new_hp == 0:
                # Mark as inactive in battle
                participant_repo.update_is_active(
                    game_state.battle.id, npc_id=target_npc.id, player_id=None, is_active=False
                )

                # Award XP immediately
                old_xp = game_state.player.xp
                old_level = game_state.player.level
                xp_gained = target_npc.xp
                gold_gained = target_npc.gold
                new_xp = old_xp + xp_gained
                new_level = get_level_from_xp(new_xp)

                # Update player XP and level
                player_repo.update_xp_and_level(game_state.player.id, new_xp, new_level)
                game_state.player.xp = new_xp
                game_state.player.level = new_level

                # Set level up flag if leveled up
                if new_level > old_level:
                    game_state.pending_level_up = True

                # Display defeat message
                display_npc_defeated(target_npc, xp_gained, gold_gained)

                result_msg += f"\n💀 {target_npc.name} has been defeated! Gained {xp_gained} XP and {gold_gained} gold."

        else:
            result_msg = f"{game_state.player.name} missed {target_npc.name}!"

        return result_msg

    finally:
        # Resume spinner
        if status:
            status.start()


# ===== ESCAPE COMBAT TOOL =====
ESCAPE_COMBAT_TOOL = {
    "name": "escape_combat",
    "description": "Attempt to escape from combat by making an ability check. If successful, combat ends. If failed, the player takes damage. Common DCs: 10 (Easy), 15 (Medium), 20 (Hard), 30 (Nearly Impossible).",
    "input_schema": {
        "type": "object",
        "properties": {
            "ability_type": {
                "type": "string",
                "enum": [
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ],
                "description": "The ability to check against for escape attempt",
            },
            "difficulty_class": {
                "type": "integer",
                "description": "The DC (difficulty class) - target number the player must meet or beat",
                "minimum": 1,
                "maximum": 30,
            },
            "failure_damage": {
                "type": "integer",
                "description": "The damage dealt to the player if they fail the escape attempt",
                "minimum": 0,
            },
        },
        "required": ["ability_type", "difficulty_class", "failure_damage"],
    },
}


def escape_combat_execute(
    ability_type: str,
    difficulty_class: int,
    failure_damage: int,
    game_state: GameState,
    db: Database,
    status=None,
) -> str:
    """
    Attempt to escape from combat with an ability check.

    Args:
        ability_type: Which ability to check (strength, dexterity, etc.)
        difficulty_class: Target DC to meet or beat
        failure_damage: Damage dealt to player if escape fails
        game_state: Current game state
        db: Database connection
        status: Optional Rich Status object to pause during display

    Returns:
        Result message indicating success or failure
    """
    # Use the existing ability check logic
    from ...game.tools.ability_check_tools import execute as ability_check_execute

    # Execute the ability check
    result = ability_check_execute(
        ability_type, difficulty_class, "escape from combat", game_state, db, status
    )

    # Check if it was successful
    if "PASSED" in result:
        # End combat
        game_state.battle = None

        from ....ui.battle_display import display_combat_escaped

        display_combat_escaped()

        return f"Escape successful! {result}"
    else:
        # Apply damage to player on failed escape
        from ....storage.repositories.player import PlayerRepository
        from ....ui.battle_display import display_combat_escape_failed

        player_repo = PlayerRepository(db)

        old_hp = game_state.player.hp
        new_hp = max(0, old_hp - failure_damage)
        game_state.player.hp = new_hp
        player_repo.update_hp(game_state.player.id, new_hp)

        # Display the failed escape with damage
        display_combat_escape_failed(failure_damage, old_hp, new_hp)

        result_msg = f"Escape failed. {result} Took {failure_damage} damage! HP: {old_hp} → {new_hp}. Combat continues."

        # Check if player died from the damage
        if new_hp == 0:
            result_msg += f"\n💀 {game_state.player.name} has been defeated!"

        return result_msg
