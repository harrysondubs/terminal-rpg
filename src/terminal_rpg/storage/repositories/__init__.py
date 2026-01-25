"""
Repository classes for RPG game data persistence.
"""

from .base import BaseRepository
from .world import WorldRepository
from .campaign import CampaignRepository
from .player import PlayerRepository
from .item import ItemRepository
from .weapon import WeaponRepository
from .armor import ArmorRepository
from .npc import NPCRepository
from .location import LocationRepository
from .battle import BattleRepository
from .campaign_log import CampaignLogRepository

__all__ = [
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
