"""
XP and leveling system utilities for RPG mechanics.
Implements accelerated D&D-style progression for terminal gameplay.
"""

# Accelerated XP thresholds for levels 1-20
# Designed for faster progression suitable for terminal-based gameplay
XP_THRESHOLDS = {
    1: 0,
    2: 50,
    3: 250,
    4: 600,
    5: 1200,
    6: 2100,
    7: 3300,
    8: 4800,
    9: 6600,
    10: 8700,
    11: 11100,
    12: 13800,
    13: 16800,
    14: 20100,
    15: 23700,
    16: 27600,
    17: 31800,
    18: 36300,
    19: 41100,
    20: 46200,
}

MAX_LEVEL = 20


def get_level_from_xp(xp: int) -> int:
    """
    Calculate current level from total XP.

    Args:
        xp: Total experience points

    Returns:
        Current level (1-20)
    """
    for level in range(MAX_LEVEL, 0, -1):
        if xp >= XP_THRESHOLDS[level]:
            return level
    return 1


def get_xp_for_next_level(current_level: int) -> int | None:
    """
    Get the total XP required to reach the next level.

    Args:
        current_level: Player's current level

    Returns:
        XP threshold for next level, or None if at max level
    """
    if current_level >= MAX_LEVEL:
        return None
    return XP_THRESHOLDS[current_level + 1]


def calculate_hp_increase(constitution_score: int) -> int:
    """
    Calculate HP gain on level up based on constitution modifier.
    Uses D&D 5E constitution modifier rules.

    Args:
        constitution_score: Player's constitution ability score

    Returns:
        HP increase amount (minimum 1)
    """
    from .utils import calculate_ability_modifier

    modifier = calculate_ability_modifier(constitution_score)
    # HP increase is constitution modifier, minimum 1
    return max(1, modifier)


def get_xp_progress(current_xp: int, current_level: int) -> tuple[int, int, float]:
    """
    Get XP progress information for display.

    Args:
        current_xp: Player's current total XP
        current_level: Player's current level

    Returns:
        Tuple of (xp_in_current_level, xp_needed_for_next, progress_percentage)
        Returns (current_xp, 0, 100.0) if at max level
    """
    if current_level >= MAX_LEVEL:
        return (current_xp, 0, 100.0)

    current_level_threshold = XP_THRESHOLDS[current_level]
    next_level_threshold = XP_THRESHOLDS[current_level + 1]

    xp_in_current_level = current_xp - current_level_threshold
    xp_needed = next_level_threshold - current_level_threshold

    progress = (xp_in_current_level / xp_needed) * 100 if xp_needed > 0 else 100.0

    return (xp_in_current_level, xp_needed, progress)
