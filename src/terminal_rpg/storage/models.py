"""
Data models for the RPG game.
Uses dataclasses for clean, type-hinted entity representations.
Follows normalized database design with proper foreign key relationships.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


# ===== Enum Definitions =====

class Rarity(Enum):
    """Item rarity levels"""
    COMMON = "common"
    RARE = "rare"
    LEGENDARY = "legendary"


class WeaponType(Enum):
    """Weapon combat types"""
    MELEE = "melee"
    RANGED = "ranged"


class HandsRequired(Enum):
    """Number of hands required to wield a weapon or spell"""
    ONE_HANDED = "one_handed"
    TWO_HANDED = "two_handed"


class ArmorType(Enum):
    """Armor equipment slots"""
    HELMET = "helmet"
    SHIELD = "shield"
    CHESTPLATE = "chestplate"
    BOOTS = "boots"
    LEGGINGS = "leggings"


class LogType(Enum):
    """Campaign log entry types"""
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class Disposition(Enum):
    """NPC disposition towards the player"""
    HOSTILE = "hostile"
    ALLY = "ally"


# ===== Entity Dataclasses =====

@dataclass
class World:
    """Base description of a campaign's world"""
    name: str
    description: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Campaign:
    """Main save file for a game campaign"""
    name: str
    world_id: int
    current_location_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_save_at: Optional[datetime] = None


@dataclass
class Player:
    """Human player character (one per campaign)"""
    campaign_id: int
    name: str
    description: str
    character_class: str
    character_species: str
    hp: int
    max_hp: int
    level: int = 1
    xp: int = 0
    gold: int = 0
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Item:
    """General inventory item"""
    world_id: int
    name: str
    description: str
    rarity: Rarity
    value: int = 0
    campaign_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Weapon:
    """Combat weapon"""
    world_id: int
    name: str
    description: str
    type: WeaponType
    hands_required: HandsRequired
    attack: int
    rarity: Rarity
    value: int = 0
    campaign_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Armor:
    """Protective armor piece"""
    world_id: int
    name: str
    description: str
    type: ArmorType
    defense: int
    rarity: Rarity
    value: int = 0
    campaign_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class NPC:
    """Non-player character for battles"""
    world_id: int
    name: str
    character_class: str
    character_species: str
    hp: int
    max_hp: int
    disposition: Disposition = Disposition.HOSTILE
    level: int = 1
    xp: int = 0
    gold: int = 0
    campaign_id: Optional[int] = None
    battle_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Location:
    """Location in the game world"""
    world_id: int
    name: str
    description: str
    campaign_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Battle:
    """Battle encounter between player and NPCs"""
    world_id: int
    name: str
    description: str
    campaign_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class CampaignLog:
    """Historical log entry for campaign events"""
    campaign_id: int
    world_id: int
    location_id: int
    type: LogType
    content: str
    battle_id: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class PlayerItem:
    """Join table linking players to items"""
    player_id: int
    item_id: int
    quantity: int = 1
    acquired_at: Optional[datetime] = None


@dataclass
class PlayerWeapon:
    """Join table linking players to weapons"""
    player_id: int
    weapon_id: int
    quantity: int = 1
    equipped: bool = False
    acquired_at: Optional[datetime] = None


@dataclass
class PlayerArmor:
    """Join table linking players to armor"""
    player_id: int
    armor_id: int
    quantity: int = 1
    equipped: bool = False
    acquired_at: Optional[datetime] = None


@dataclass
class GameState:
    """Composite model for full game state"""
    campaign: Campaign
    world: World
    player: Player
    location: Location
    equipped_weapons: list[Weapon]
    equipped_armor: list[Armor]
    inventory_items: list[tuple[Item, int]]  # (item, quantity)
    inventory_weapons: list[tuple[Weapon, int]]  # (weapon, quantity)
    inventory_armor: list[tuple[Armor, int]]  # (armor, quantity)
    battle: Optional[Battle] = None
    pending_level_up: bool = False


# ===== Helper Functions =====
# TODO: Move to shared utils file.

def datetime_to_db(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO8601 string for SQLite storage"""
    return dt.isoformat() if dt else None


def datetime_from_db(s: Optional[str]) -> Optional[datetime]:
    """Convert ISO8601 string from SQLite to datetime object"""
    return datetime.fromisoformat(s) if s else None
