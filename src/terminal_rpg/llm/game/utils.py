"""
Utility functions for the game module.
"""

import importlib
import logging
import sys
from typing import Any, Dict, List, Tuple

from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


def reload_game_modules() -> Tuple[int, Dict[str, Any]]:
    """
    Reload game modules for hot-reload during development.
    
    Returns:
        Tuple of (reloaded_count, reloaded_components) where reloaded_components
        is a dictionary containing all the freshly imported tools and functions.
    """
    # List of modules to reload in dependency order
    modules_to_reload = [
        'terminal_rpg.engines.dice',
        'terminal_rpg.llm.game.tools.inventory_tools',
        'terminal_rpg.llm.game.tools.location_tools',
        'terminal_rpg.llm.game.tools.gold_tools',
        'terminal_rpg.llm.game.tools.hp_tools',
        'terminal_rpg.llm.game.tools.ability_check_tools',
        'terminal_rpg.llm.game.tools',
        'terminal_rpg.llm.game.prompts.dm_game_prompts',
        'terminal_rpg.llm.game.message_history',
    ]

    reloaded_count = 0
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            reloaded_count += 1
            logger.info(f"Reloaded module: {module_name}")

    # Import fresh versions of all components
    from .tools import (
        ABILITY_CHECK_TOOL,
        ADD_ARMOR_TOOL,
        ADD_ITEM_TOOL,
        ADD_WEAPON_TOOL,
        CHANGE_LOCATION_TOOL,
        CREATE_LOCATION_TOOL,
        GOLD_TOOL,
        HP_TOOL,
        REMOVE_INVENTORY_TOOL,
        VIEW_INVENTORY_TOOL,
        VIEW_LOCATIONS_TOOL,
        add_armor_execute,
        add_item_execute,
        add_weapon_execute,
        change_location_execute,
        create_location_execute,
        execute_ability_check,
        execute_gold,
        execute_hp,
        remove_inventory_execute,
        view_inventory_execute,
        view_locations_execute,
    )

    from .message_history import (
        reconstruct_message_history,
        save_assistant_message,
        save_tool_call,
        save_tool_results,
        save_user_message,
    )

    from .prompts.dm_game_prompts import create_dm_system_prompt

    # Package everything into a dictionary for easy access
    reloaded_components = {
        # Tool definitions
        'TOOLS': [
            VIEW_INVENTORY_TOOL,
            ADD_ITEM_TOOL,
            ADD_WEAPON_TOOL,
            ADD_ARMOR_TOOL,
            REMOVE_INVENTORY_TOOL,
            CHANGE_LOCATION_TOOL,
            VIEW_LOCATIONS_TOOL,
            CREATE_LOCATION_TOOL,
            GOLD_TOOL,
            HP_TOOL,
            ABILITY_CHECK_TOOL
        ],
        # Tool executors
        'view_inventory_execute': view_inventory_execute,
        'add_item_execute': add_item_execute,
        'add_weapon_execute': add_weapon_execute,
        'add_armor_execute': add_armor_execute,
        'remove_inventory_execute': remove_inventory_execute,
        'change_location_execute': change_location_execute,
        'view_locations_execute': view_locations_execute,
        'create_location_execute': create_location_execute,
        'execute_gold': execute_gold,
        'execute_hp': execute_hp,
        'execute_ability_check': execute_ability_check,
        # Message history functions
        'reconstruct_message_history': reconstruct_message_history,
        'save_assistant_message': save_assistant_message,
        'save_tool_call': save_tool_call,
        'save_tool_results': save_tool_results,
        'save_user_message': save_user_message,
        # Prompt generation
        'create_dm_system_prompt': create_dm_system_prompt,
    }

    return reloaded_count, reloaded_components
