"""
Player inventory viewing tool for DM.
"""

from ....storage.models import GameState


# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "view_player_inventory",
    "description": "View the player's complete inventory including equipped items, weapons, armor, and consumables. Use this when the player asks about their inventory or when you need to check what items they have available.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


def execute(game_state: GameState) -> str:
    """
    Format player inventory as markdown.

    Args:
        game_state: Current game state

    Returns:
        Formatted markdown string
    """
    player = game_state.player

    lines = [
        f"# {player.name}'s Inventory",
        f"**Gold**: {player.gold}g",
        "",
        "## Equipped Weapons"
    ]

    if game_state.equipped_weapons:
        for weapon in game_state.equipped_weapons:
            lines.append(f"- **{weapon.name}** (Attack: +{weapon.attack}, {weapon.type.value}, {weapon.hands_required.value})")
            lines.append(f"  _{weapon.description}_")
    else:
        lines.append("- None")

    lines.extend(["", "## Equipped Armor"])

    if game_state.equipped_armor:
        for armor in game_state.equipped_armor:
            lines.append(f"- **{armor.name}** (Defense: +{armor.defense}, {armor.type.value})")
            lines.append(f"  _{armor.description}_")
    else:
        lines.append("- None")

    lines.extend(["", "## Weapons in Inventory"])

    if game_state.inventory_weapons:
        for weapon, qty in game_state.inventory_weapons:
            lines.append(f"- **{weapon.name}** x{qty} (Attack: +{weapon.attack})")
    else:
        lines.append("- None")

    lines.extend(["", "## Armor in Inventory"])

    if game_state.inventory_armor:
        for armor, qty in game_state.inventory_armor:
            lines.append(f"- **{armor.name}** x{qty} (Defense: +{armor.defense})")
    else:
        lines.append("- None")

    lines.extend(["", "## Items"])

    if game_state.inventory_items:
        for item, qty in game_state.inventory_items:
            lines.append(f"- **{item.name}** x{qty}")
            lines.append(f"  _{item.description}_")
    else:
        lines.append("- None")

    return "\n".join(lines)
