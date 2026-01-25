"""
Tools for the DM to interact with the game state.
"""

from .inventory_tool import TOOL_DEFINITION as INVENTORY_TOOL, execute as execute_inventory
from .location_tool import TOOL_DEFINITION as LOCATION_TOOL, execute as execute_location
from .gold_tool import TOOL_DEFINITION as GOLD_TOOL, execute as execute_gold
from .hp_tool import TOOL_DEFINITION as HP_TOOL, execute as execute_hp
from .ability_check_tool import TOOL_DEFINITION as ABILITY_CHECK_TOOL, execute as execute_ability_check

__all__ = [
    "INVENTORY_TOOL",
    "LOCATION_TOOL",
    "GOLD_TOOL",
    "HP_TOOL",
    "ABILITY_CHECK_TOOL",
    "execute_inventory",
    "execute_location",
    "execute_gold",
    "execute_hp",
    "execute_ability_check",
]
