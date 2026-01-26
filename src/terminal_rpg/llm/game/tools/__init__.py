"""
Tools for the DM to interact with the game state.
"""

from .inventory_tools import (
    VIEW_INVENTORY_TOOL,
    ADD_ITEM_TOOL,
    ADD_WEAPON_TOOL,
    ADD_ARMOR_TOOL,
    REMOVE_INVENTORY_TOOL,
    view_inventory_execute,
    add_item_execute,
    add_weapon_execute,
    add_armor_execute,
    remove_inventory_execute,
    # Legacy exports for backwards compatibility
    TOOL_DEFINITION as INVENTORY_TOOL,
    execute as execute_inventory
)
from .location_tools import (
    CHANGE_LOCATION_TOOL,
    VIEW_LOCATIONS_TOOL,
    CREATE_LOCATION_TOOL,
    change_location_execute,
    view_locations_execute,
    create_location_execute,
)
from .gold_tools import TOOL_DEFINITION as GOLD_TOOL, execute as execute_gold
from .hp_tools import TOOL_DEFINITION as HP_TOOL, execute as execute_hp
from .ability_check_tools import TOOL_DEFINITION as ABILITY_CHECK_TOOL, execute as execute_ability_check

__all__ = [
    "INVENTORY_TOOL",
    "VIEW_INVENTORY_TOOL",
    "ADD_ITEM_TOOL",
    "ADD_WEAPON_TOOL",
    "ADD_ARMOR_TOOL",
    "REMOVE_INVENTORY_TOOL",
    "CHANGE_LOCATION_TOOL",
    "VIEW_LOCATIONS_TOOL",
    "CREATE_LOCATION_TOOL",
    "GOLD_TOOL",
    "HP_TOOL",
    "ABILITY_CHECK_TOOL",
    "execute_inventory",
    "view_inventory_execute",
    "add_item_execute",
    "add_weapon_execute",
    "add_armor_execute",
    "remove_inventory_execute",
    "change_location_execute",
    "view_locations_execute",
    "create_location_execute",
    "execute_gold",
    "execute_hp",
    "execute_ability_check",
]
