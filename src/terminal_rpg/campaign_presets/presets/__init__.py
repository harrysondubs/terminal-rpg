"""
Campaign presets for Terminal RPG.
Each preset defines a complete campaign package with world, locations, equipment, and classes.
"""

# Import all preset modules to trigger registration
from . import forgotten_realms, sword_coast

__all__ = [
    "forgotten_realms",
    "sword_coast",
]
