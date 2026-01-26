"""
Storage package for RPG game data persistence.

Provides:
- Data models (dataclasses and enums)
- Database connection management
- Repository pattern for CRUD operations
"""

# Database
from .database import Database

# Models
from .models import (
    # Enums
    Rarity, WeaponType, HandsRequired, ArmorType, LogType,
    # Entities
    World, Campaign, Player, Item, Weapon, Armor, NPC, Location, Battle, CampaignLog,
    # Join tables
    PlayerItem, PlayerWeapon, PlayerArmor,
    # Composite models
    GameState,
    # Helper functions
    datetime_to_db, datetime_from_db
)

# Repositories
from .repositories import (
    BaseRepository,
    WorldRepository,
    CampaignRepository,
    PlayerRepository,
    ItemRepository,
    WeaponRepository,
    ArmorRepository,
    NPCRepository,
    LocationRepository,
    BattleRepository,
    CampaignLogRepository
)

__all__ = [
    # Database
    'Database',
    # Enums
    'Rarity',
    'WeaponType',
    'HandsRequired',
    'ArmorType',
    'LogType',
    # Entities
    'World',
    'Campaign',
    'Player',
    'Item',
    'Weapon',
    'Armor',
    'NPC',
    'Location',
    'Battle',
    'CampaignLog',
    # Join tables
    'PlayerItem',
    'PlayerWeapon',
    'PlayerArmor',
    # Composite models
    'GameState',
    # Helper functions
    'datetime_to_db',
    'datetime_from_db',
    # Repositories
    'BaseRepository',
    'WorldRepository',
    'CampaignRepository',
    'PlayerRepository',
    'ItemRepository',
    'WeaponRepository',
    'ArmorRepository',
    'NPCRepository',
    'LocationRepository',
    'BattleRepository',
    'CampaignLogRepository',
]
