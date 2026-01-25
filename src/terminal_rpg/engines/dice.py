"""
Dice rolling utilities for RPG mechanics.
"""

import random


def roll_d20() -> int:
    """
    Roll a 20-sided die.

    Returns:
        Random number between 1 and 20
    """
    return random.randint(1, 20)


def calculate_ability_modifier(ability_score: int) -> int:
    """
    Calculate D&D ability modifier from ability score.

    Formula: (ability_score - 10) // 2

    Args:
        ability_score: The ability score (e.g., strength, dexterity)

    Returns:
        The modifier value
    """
    return (ability_score - 10) // 2
