"""
Campaign preset system for Terminal RPG.
Provides extensible preset definitions for worlds, equipment, and character classes.
"""

from .models import (
    CampaignPreset,
    WorldDefinition,
    LocationDefinition,
    ItemDefinition,
    WeaponDefinition,
    ArmorDefinition,
    NPCDefinition,
    CharacterClassPreset
)
from .registry import PresetRegistry
from .loader import PresetLoader

# Import all preset modules to trigger registration
from . import presets

__all__ = [
    'CampaignPreset',
    'WorldDefinition',
    'LocationDefinition',
    'ItemDefinition',
    'WeaponDefinition',
    'ArmorDefinition',
    'NPCDefinition',
    'CharacterClassPreset',
    'PresetRegistry',
    'PresetLoader',
]
