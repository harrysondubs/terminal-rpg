"""
Utility functions for RPG mechanics.
"""

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
