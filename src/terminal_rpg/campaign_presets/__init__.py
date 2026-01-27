"""
Campaign preset system for Terminal RPG.
Provides extensible preset definitions for worlds, equipment, and character classes.
"""

# Import all preset modules to trigger registration
from . import presets  # noqa: F401
from .loader import PresetLoader
from .models import (
    ArmorDefinition,
    CampaignPreset,
    CharacterClassPreset,
    ItemDefinition,
    LocationDefinition,
    NPCDefinition,
    WeaponDefinition,
    WorldDefinition,
)
from .registry import PresetRegistry

__all__ = [
    "CampaignPreset",
    "WorldDefinition",
    "LocationDefinition",
    "ItemDefinition",
    "WeaponDefinition",
    "ArmorDefinition",
    "NPCDefinition",
    "CharacterClassPreset",
    "PresetRegistry",
    "PresetLoader",
]
