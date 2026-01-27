"""
Repository classes for RPG game data persistence.
"""

from .armor import ArmorRepository
from .base import BaseRepository
from .battle import BattleRepository
from .campaign import CampaignRepository
from .campaign_log import CampaignLogRepository
from .item import ItemRepository
from .location import LocationRepository
from .npc import NPCRepository
from .player import PlayerRepository
from .weapon import WeaponRepository
from .world import WorldRepository

__all__ = [
    "BaseRepository",
    "WorldRepository",
    "CampaignRepository",
    "PlayerRepository",
    "ItemRepository",
    "WeaponRepository",
    "ArmorRepository",
    "NPCRepository",
    "LocationRepository",
    "BattleRepository",
    "CampaignLogRepository",
]
