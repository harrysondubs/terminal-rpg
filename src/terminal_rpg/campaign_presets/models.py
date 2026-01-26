"""
Data models for campaign presets.
Defines the structure for preset definitions including worlds, locations, equipment, and character classes.
"""

from dataclasses import dataclass
from ..storage.models import Rarity, WeaponType, HandsRequired, ArmorType


@dataclass
class WorldDefinition:
    """Definition for a game world."""
    name: str
    description: str


@dataclass
class LocationDefinition:
    """Definition for a location within a world."""
    name: str
    description: str


@dataclass
class ItemDefinition:
    """Definition for a consumable item."""
    name: str
    description: str
    rarity: Rarity
    value: int


@dataclass
class WeaponDefinition:
    """Definition for a weapon."""
    name: str
    description: str
    type: WeaponType
    hands_required: HandsRequired
    attack: int
    rarity: Rarity
    value: int


@dataclass
class ArmorDefinition:
    """Definition for an armor piece."""
    name: str
    description: str
    type: ArmorType
    defense: int
    rarity: Rarity
    value: int


@dataclass
class NPCDefinition:
    """Definition for an NPC or enemy."""
    name: str
    character_class: str
    character_race: str
    hp: int
    max_hp: int
    level: int
    xp: int
    gold: int


@dataclass
class CharacterClassPreset:
    """Character class preset with stats and equipment."""
    name: str
    description: str
    character_race: str
    stats: dict[str, int]  # Keys: strength, dexterity, constitution, intelligence, wisdom, charisma
    base_hp: int
    starting_gold: int
    equipment_weapons: list[str]  # Weapon names to add to inventory
    equipment_armor: list[str]    # Armor names to add to inventory
    equipment_items: list[str]    # Item names to add to inventory
    auto_equip_weapon: str        # Weapon name to auto-equip
    auto_equip_armor: list[str]   # Armor names to auto-equip


@dataclass
class CampaignPreset:
    """
    Complete campaign preset definition.
    Contains all data needed to create a new campaign including world, locations, equipment, and classes.
    """
    id: str                                          # Unique identifier (e.g., "forgotten_realms")
    display_name: str                                # Display name for UI (e.g., "The Forgotten Realms")
    world: WorldDefinition                           # World definition
    locations: list[LocationDefinition]              # Locations in this world
    items: list[ItemDefinition]                      # Consumable items
    weapons: list[WeaponDefinition]                  # Weapons
    armor: list[ArmorDefinition]                     # Armor pieces
    npcs: list[NPCDefinition]                        # NPCs and enemies
    character_classes: dict[str, CharacterClassPreset]  # Available character classes
    starting_location_name: str                      # Name of starting location
