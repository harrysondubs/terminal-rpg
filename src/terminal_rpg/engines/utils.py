"""
Utility functions for RPG mechanics.
"""

import random


def calculate_ability_modifier(ability_score: int) -> int:
    """
    Calculate D&D ability modifier from ability score.

    Formula: (ability_score - 10) // 2 (floor division to negative infinity)

    Args:
        ability_score: The ability score (e.g., strength, dexterity)

    Returns:
        The modifier value
    """
    return (ability_score - 10) // 2


def calculate_player_ac(player, equipped_armor: list) -> int:
    """
    Calculate player's Armor Class based on equipped armor and dexterity.

    Rules:
    - Unarmored: 10 + DEX modifier
    - Light armor: armor AC + DEX modifier
    - Medium armor: armor AC + DEX modifier
    - Heavy armor: armor AC (no DEX modifier)
    - Shield: +2 to any of the above

    Args:
        player: Player object with dexterity stat
        equipped_armor: List of equipped Armor objects

    Returns:
        Total armor class value
    """
    from ..storage.models import ArmorType

    dex_modifier = calculate_ability_modifier(player.dexterity)

    # Check for different armor types
    has_shield = False
    base_armor = None
    base_ac = 10  # Unarmored base

    for armor in equipped_armor:
        if armor.type == ArmorType.SHIELD:
            has_shield = True
        else:
            # Use the first non-shield armor found
            if base_armor is None:
                base_armor = armor

    # Calculate base AC
    if base_armor is None:
        # Unarmored: 10 + DEX mod
        ac = base_ac + dex_modifier
    elif base_armor.type == ArmorType.LIGHT:
        # Light armor: armor AC + DEX mod
        ac = base_armor.ac + dex_modifier
    elif base_armor.type == ArmorType.MEDIUM:
        # Medium armor: armor AC + DEX mod (capped at +2 in some systems, but we'll use full)
        ac = base_armor.ac + dex_modifier
    elif base_armor.type == ArmorType.HEAVY:
        # Heavy armor: armor AC only (no DEX)
        ac = base_armor.ac
    else:
        ac = base_ac + dex_modifier

    # Add shield bonus
    if has_shield:
        ac += 2

    return ac


def roll_attack(attacker_bonus: int, target_ac: int) -> tuple[int, int, bool, bool]:
    """
    Roll an attack roll (d20 + bonus) and check if it hits the target.

    Args:
        attacker_bonus: Attack modifier to add to the roll
        target_ac: Target's armor class

    Returns:
        Tuple of (raw_roll, total, is_hit, is_critical)
        - raw_roll: The d20 roll result (1-20)
        - total: raw_roll + attacker_bonus
        - is_hit: True if total >= target_ac OR raw_roll == 20 (critical hit)
        - is_critical: True if raw_roll == 20 (natural 20)
    """
    raw_roll = random.randint(1, 20)
    total = raw_roll + attacker_bonus
    is_critical = raw_roll == 20
    # Critical hit (nat 20) is always a hit, regardless of AC
    is_hit = is_critical or total >= target_ac

    return raw_roll, total, is_hit, is_critical


def roll_damage(dice_count: int, dice_sides: str, is_critical: bool = False) -> int:
    """
    Roll damage dice and return the total.

    Args:
        dice_count: Number of dice to roll
        dice_sides: Dice type as string (e.g., "d6", "d8", "d10")
        is_critical: If True, doubles the number of dice rolled (critical hit)

    Returns:
        Total damage rolled
    """
    # Parse dice sides from string (e.g., "d6" -> 6)
    sides_map = {"d4": 4, "d6": 6, "d8": 8, "d10": 10, "d12": 12, "d20": 20}

    sides = sides_map.get(dice_sides.lower(), 6)  # Default to d6 if invalid

    # Double dice on critical hit
    effective_dice_count = dice_count * 2 if is_critical else dice_count

    total = 0
    for _ in range(effective_dice_count):
        total += random.randint(1, sides)

    return total
