"""
Player inventory management tools for DM.
"""

from ....storage.database import Database
from ....storage.models import (
    Armor,
    ArmorType,
    DamageDiceSides,
    GameState,
    HandsRequired,
    Item,
    Rarity,
    Weapon,
    WeaponType,
)
from ....storage.repositories import (
    ArmorRepository,
    ItemRepository,
    PlayerRepository,
    WeaponRepository,
)

# ===== VIEW INVENTORY TOOL =====
VIEW_INVENTORY_TOOL = {
    "name": "view_player_inventory",
    "description": "View the player's complete inventory including equipped items, weapons, armor, and consumables. Use this when the player asks about their inventory or when you need to check what items they have available.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


def view_inventory_execute(game_state: GameState) -> str:
    """
    Format player inventory as markdown.

    Args:
        game_state: Current game state

    Returns:
        Formatted markdown string
    """
    player = game_state.player

    lines = [f"# {player.name}'s Inventory", f"**Gold**: {player.gold}g", "", "## Equipped Weapons"]

    if game_state.equipped_weapons:
        for weapon in game_state.equipped_weapons:
            dice_str = f"{weapon.damage_dice_count}{weapon.damage_dice_sides.value}"
            lines.append(
                f"- **{weapon.name}** (Damage: {dice_str}, {weapon.type.value}, {weapon.hands_required.value})"
            )
            lines.append(f"  _{weapon.description}_")
    else:
        lines.append("- None")

    lines.extend(["", "## Equipped Armor"])

    if game_state.equipped_armor:
        for armor in game_state.equipped_armor:
            ac_display = (
                f"AC: {armor.ac}" if armor.type.value != "shield" else f"AC Bonus: +{armor.ac}"
            )
            lines.append(f"- **{armor.name}** ({ac_display}, {armor.type.value})")
            lines.append(f"  _{armor.description}_")
    else:
        lines.append("- None")

    lines.extend(["", "## Weapons in Inventory"])

    if game_state.inventory_weapons:
        for weapon, qty in game_state.inventory_weapons:
            dice_str = f"{weapon.damage_dice_count}{weapon.damage_dice_sides.value}"
            lines.append(f"- **{weapon.name}** x{qty} (Damage: {dice_str})")
    else:
        lines.append("- None")

    lines.extend(["", "## Armor in Inventory"])

    if game_state.inventory_armor:
        for armor, qty in game_state.inventory_armor:
            ac_display = (
                f"AC: {armor.ac}" if armor.type.value != "shield" else f"AC Bonus: +{armor.ac}"
            )
            lines.append(f"- **{armor.name}** x{qty} ({ac_display})")
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


# ===== ADD ITEM TO INVENTORY TOOL =====
ADD_ITEM_TOOL = {
    "name": "add_item_to_inventory",
    "description": "Add a new item to the player's inventory. Use this when the player finds, buys, or receives a new consumable item.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the item"},
            "description": {
                "type": "string",
                "description": "Description of the item and its effects",
            },
            "rarity": {
                "type": "string",
                "enum": ["common", "rare", "legendary"],
                "description": "Rarity level of the item",
            },
            "value": {"type": "integer", "description": "Gold value of the item"},
            "quantity": {
                "type": "integer",
                "description": "Number of items to add (default 1)",
                "default": 1,
            },
        },
        "required": ["name", "description", "rarity", "value"],
    },
}


def add_item_execute(
    name: str,
    description: str,
    rarity: str,
    value: int,
    game_state: GameState,
    db: Database,
    quantity: int = 1,
) -> str:
    """
    Add a new item to player inventory.

    Args:
        name: Item name
        description: Item description
        rarity: Item rarity (common/rare/legendary)
        value: Item gold value
        game_state: Current game state
        db: Database connection
        quantity: Number of items to add

    Returns:
        Success/failure message
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: Item name cannot be empty."

    if not description or not description.strip():
        return "Error: Item description cannot be empty."

    if value < 0:
        return "Error: Item value cannot be negative."

    if quantity < 1:
        return "Error: Quantity must be at least 1."

    # Convert rarity string to enum
    try:
        rarity_enum = Rarity(rarity.lower())
    except ValueError:
        return f"Error: Invalid rarity '{rarity}'. Must be one of: common, rare, legendary."

    name = name.strip()
    description = description.strip()

    item_repo = ItemRepository(db)
    player_repo = PlayerRepository(db)

    # Create new item
    new_item = Item(
        world_id=game_state.world.id,
        campaign_id=game_state.campaign.id,
        name=name,
        description=description,
        rarity=rarity_enum,
        value=value,
    )

    try:
        created_item = item_repo.create(new_item)

        # Add to player inventory
        player_repo.add_item(game_state.player.id, created_item.id, quantity)

        qty_text = f"{quantity}x " if quantity > 1 else ""
        return f"Successfully added {qty_text}{created_item.name} ({rarity}) to {game_state.player.name}'s inventory."
    except Exception as e:
        return f"Error adding item to inventory: {str(e)}"


# ===== ADD WEAPON TO INVENTORY TOOL =====
ADD_WEAPON_TOOL = {
    "name": "add_weapon_to_inventory",
    "description": "Add a new weapon to the player's inventory. Use this when the player finds, buys, or receives a new weapon.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the weapon"},
            "description": {"type": "string", "description": "Description of the weapon"},
            "rarity": {
                "type": "string",
                "enum": ["common", "rare", "legendary"],
                "description": "Rarity level of the weapon",
            },
            "type": {
                "type": "string",
                "enum": ["melee", "ranged"],
                "description": "Weapon combat type",
            },
            "hands_required": {
                "type": "string",
                "enum": ["one_handed", "two_handed"],
                "description": "Number of hands needed to wield",
            },
            "damage_dice_count": {
                "type": "integer",
                "description": "Number of damage dice to roll (typically 1-2)",
            },
            "damage_dice_sides": {
                "type": "string",
                "enum": ["d4", "d6", "d8", "d10", "d12"],
                "description": "Type of damage die (d4, d6, d8, d10, or d12)",
            },
            "value": {"type": "integer", "description": "Gold value of the weapon"},
            "quantity": {
                "type": "integer",
                "description": "Number of weapons to add (default 1)",
                "default": 1,
            },
        },
        "required": [
            "name",
            "description",
            "rarity",
            "type",
            "hands_required",
            "damage_dice_count",
            "damage_dice_sides",
            "value",
        ],
    },
}


def add_weapon_execute(
    name: str,
    description: str,
    rarity: str,
    type: str,
    hands_required: str,
    damage_dice_count: int,
    damage_dice_sides: str,
    value: int,
    game_state: GameState,
    db: Database,
    quantity: int = 1,
) -> str:
    """
    Add a new weapon to player inventory.

    Args:
        name: Weapon name
        description: Weapon description
        rarity: Weapon rarity (common/rare/legendary)
        type: Weapon type (melee/ranged)
        hands_required: Hands required (one_handed/two_handed)
        damage_dice_count: Number of damage dice
        damage_dice_sides: Type of damage die (d4/d6/d8/d10/d12)
        value: Weapon gold value
        game_state: Current game state
        db: Database connection
        quantity: Number of weapons to add

    Returns:
        Success/failure message
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: Weapon name cannot be empty."

    if not description or not description.strip():
        return "Error: Weapon description cannot be empty."

    if damage_dice_count < 1:
        return "Error: Damage dice count must be at least 1."

    if value < 0:
        return "Error: Weapon value cannot be negative."

    if quantity < 1:
        return "Error: Quantity must be at least 1."

    # Convert strings to enums
    try:
        rarity_enum = Rarity(rarity.lower())
    except ValueError:
        return f"Error: Invalid rarity '{rarity}'. Must be one of: common, rare, legendary."

    try:
        type_enum = WeaponType(type.lower())
    except ValueError:
        return f"Error: Invalid weapon type '{type}'. Must be one of: melee, ranged."

    try:
        hands_enum = HandsRequired(hands_required.lower())
    except ValueError:
        return f"Error: Invalid hands_required '{hands_required}'. Must be one of: one_handed, two_handed."

    try:
        dice_enum = DamageDiceSides(damage_dice_sides.lower())
    except ValueError:
        return f"Error: Invalid damage_dice_sides '{damage_dice_sides}'. Must be one of: d4, d6, d8, d10, d12."

    name = name.strip()
    description = description.strip()

    weapon_repo = WeaponRepository(db)
    player_repo = PlayerRepository(db)

    # Create new weapon
    new_weapon = Weapon(
        world_id=game_state.world.id,
        campaign_id=game_state.campaign.id,
        name=name,
        description=description,
        type=type_enum,
        hands_required=hands_enum,
        damage_dice_count=damage_dice_count,
        damage_dice_sides=dice_enum,
        rarity=rarity_enum,
        value=value,
    )

    try:
        created_weapon = weapon_repo.create(new_weapon)

        # Add to player inventory
        player_repo.add_weapon(game_state.player.id, created_weapon.id, quantity)

        qty_text = f"{quantity}x " if quantity > 1 else ""
        dice_str = f"{damage_dice_count}{damage_dice_sides}"
        return f"Successfully added {qty_text}{created_weapon.name} (Damage: {dice_str}, {type}, {rarity}) to {game_state.player.name}'s inventory."
    except Exception as e:
        return f"Error adding weapon to inventory: {str(e)}"


# ===== ADD ARMOR TO INVENTORY TOOL =====
ADD_ARMOR_TOOL = {
    "name": "add_armor_to_inventory",
    "description": "Add a new armor piece to the player's inventory. Use this when the player finds, buys, or receives new armor. For light/medium/heavy armor, 'ac' is the base AC. For shields, 'ac' is the AC bonus.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name of the armor"},
            "description": {"type": "string", "description": "Description of the armor"},
            "rarity": {
                "type": "string",
                "enum": ["common", "rare", "legendary"],
                "description": "Rarity level of the armor",
            },
            "type": {
                "type": "string",
                "enum": ["light", "medium", "heavy", "shield"],
                "description": "Armor type: light (AC 11-12), medium (AC 13-15), heavy (AC 16-18), shield (AC bonus +1 to +3)",
            },
            "ac": {
                "type": "integer",
                "description": "For light/medium/heavy: base AC (11-18). For shields: AC bonus (+1 to +3, typically +2)",
            },
            "value": {"type": "integer", "description": "Gold value of the armor"},
            "quantity": {
                "type": "integer",
                "description": "Number of armor pieces to add (default 1)",
                "default": 1,
            },
        },
        "required": ["name", "description", "rarity", "type", "ac", "value"],
    },
}


def add_armor_execute(
    name: str,
    description: str,
    rarity: str,
    type: str,
    ac: int,
    value: int,
    game_state: GameState,
    db: Database,
    quantity: int = 1,
) -> str:
    """
    Add a new armor piece to player inventory.

    Args:
        name: Armor name
        description: Armor description
        rarity: Armor rarity (common/rare/legendary)
        type: Armor type (light/medium/heavy/shield)
        ac: AC value (base AC for armor, AC bonus for shields)
        value: Armor gold value
        game_state: Current game state
        db: Database connection
        quantity: Number of armor pieces to add

    Returns:
        Success/failure message
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: Armor name cannot be empty."

    if not description or not description.strip():
        return "Error: Armor description cannot be empty."

    if ac < 0:
        return "Error: AC value cannot be negative."

    if value < 0:
        return "Error: Armor value cannot be negative."

    if quantity < 1:
        return "Error: Quantity must be at least 1."

    # Convert strings to enums
    try:
        rarity_enum = Rarity(rarity.lower())
    except ValueError:
        return f"Error: Invalid rarity '{rarity}'. Must be one of: common, rare, legendary."

    try:
        type_enum = ArmorType(type.lower())
    except ValueError:
        return f"Error: Invalid armor type '{type}'. Must be one of: light, medium, heavy, shield."

    name = name.strip()
    description = description.strip()

    armor_repo = ArmorRepository(db)
    player_repo = PlayerRepository(db)

    # Create new armor
    new_armor = Armor(
        world_id=game_state.world.id,
        campaign_id=game_state.campaign.id,
        name=name,
        description=description,
        type=type_enum,
        ac=ac,
        rarity=rarity_enum,
        value=value,
    )

    try:
        created_armor = armor_repo.create(new_armor)

        # Add to player inventory
        player_repo.add_armor(game_state.player.id, created_armor.id, quantity)

        qty_text = f"{quantity}x " if quantity > 1 else ""
        ac_display = f"AC: {ac}" if type != "shield" else f"AC Bonus: +{ac}"
        return f"Successfully added {qty_text}{created_armor.name} ({ac_display}, {type}, {rarity}) to {game_state.player.name}'s inventory."
    except Exception as e:
        return f"Error adding armor to inventory: {str(e)}"


# ===== REMOVE FROM INVENTORY TOOL =====
REMOVE_INVENTORY_TOOL = {
    "name": "remove_from_inventory",
    "description": "Remove an item, weapon, or armor from the player's inventory. Use this when the player uses, sells, or loses items.",
    "input_schema": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["item", "weapon", "armor"],
                "description": "Type of inventory entry to remove",
            },
            "name": {"type": "string", "description": "Name of the item/weapon/armor to remove"},
            "quantity": {
                "type": "integer",
                "description": "Number to remove (default 1)",
                "default": 1,
            },
        },
        "required": ["type", "name"],
    },
}


def remove_inventory_execute(
    type: str, name: str, game_state: GameState, db: Database, quantity: int = 1
) -> str:
    """
    Remove item/weapon/armor from player inventory.

    Args:
        type: Type of entry (item/weapon/armor)
        name: Name of the item to remove
        game_state: Current game state
        db: Database connection
        quantity: Number to remove

    Returns:
        Success/failure message
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: Item name cannot be empty."

    if quantity < 1:
        return "Error: Quantity must be at least 1."

    name = name.strip()

    if type == "item":
        return _remove_item(name, quantity, game_state, db)
    elif type == "weapon":
        return _remove_weapon(name, quantity, game_state, db)
    elif type == "armor":
        return _remove_armor(name, quantity, game_state, db)
    else:
        return f"Error: Invalid type '{type}'. Must be one of: item, weapon, armor."


def _remove_item(name: str, quantity: int, game_state: GameState, db: Database) -> str:
    """Remove item from player inventory."""
    item_repo = ItemRepository(db)

    # Find the item by name
    items = item_repo.get_by_world(game_state.world.id, campaign_id=game_state.campaign.id)
    target_item = None
    for item in items:
        if item.name.lower() == name.lower():
            target_item = item
            break

    if not target_item:
        return f"Error: Item '{name}' not found in the game world."

    # Check if player has this item
    cursor = db.conn.execute(
        "SELECT quantity FROM player_items WHERE player_id = ? AND item_id = ?",
        (game_state.player.id, target_item.id),
    )
    row = cursor.fetchone()

    if not row:
        return f"Warning: {game_state.player.name} does not have '{name}' in their inventory."

    current_quantity = row["quantity"]

    if quantity > current_quantity:
        return f"Warning: Cannot remove {quantity}x {name}. Player only has {current_quantity}x in inventory."

    # Update or remove the entry
    if quantity == current_quantity:
        # Remove entirely
        db.conn.execute(
            "DELETE FROM player_items WHERE player_id = ? AND item_id = ?",
            (game_state.player.id, target_item.id),
        )
        db.conn.commit()
        return f"Successfully removed all {name} ({current_quantity}x) from {game_state.player.name}'s inventory."
    else:
        # Reduce quantity
        new_quantity = current_quantity - quantity
        db.conn.execute(
            "UPDATE player_items SET quantity = ? WHERE player_id = ? AND item_id = ?",
            (new_quantity, game_state.player.id, target_item.id),
        )
        db.conn.commit()
        qty_text = f"{quantity}x " if quantity > 1 else ""
        return f"Successfully removed {qty_text}{name} from {game_state.player.name}'s inventory. Remaining: {new_quantity}x."


def _remove_weapon(name: str, quantity: int, game_state: GameState, db: Database) -> str:
    """Remove weapon from player inventory."""
    weapon_repo = WeaponRepository(db)

    # Find the weapon by name
    weapons = weapon_repo.get_by_world(game_state.world.id, campaign_id=game_state.campaign.id)
    target_weapon = None
    for weapon in weapons:
        if weapon.name.lower() == name.lower():
            target_weapon = weapon
            break

    if not target_weapon:
        return f"Error: Weapon '{name}' not found in the game world."

    # Check if player has this weapon
    cursor = db.conn.execute(
        "SELECT quantity FROM player_weapons WHERE player_id = ? AND weapon_id = ?",
        (game_state.player.id, target_weapon.id),
    )
    row = cursor.fetchone()

    if not row:
        return f"Warning: {game_state.player.name} does not have '{name}' in their inventory."

    current_quantity = row["quantity"]

    if quantity > current_quantity:
        return f"Warning: Cannot remove {quantity}x {name}. Player only has {current_quantity}x in inventory."

    # Update or remove the entry
    if quantity == current_quantity:
        # Remove entirely
        db.conn.execute(
            "DELETE FROM player_weapons WHERE player_id = ? AND weapon_id = ?",
            (game_state.player.id, target_weapon.id),
        )
        db.conn.commit()
        return f"Successfully removed all {name} ({current_quantity}x) from {game_state.player.name}'s inventory."
    else:
        # Reduce quantity
        new_quantity = current_quantity - quantity
        db.conn.execute(
            "UPDATE player_weapons SET quantity = ? WHERE player_id = ? AND weapon_id = ?",
            (new_quantity, game_state.player.id, target_weapon.id),
        )
        db.conn.commit()
        qty_text = f"{quantity}x " if quantity > 1 else ""
        return f"Successfully removed {qty_text}{name} from {game_state.player.name}'s inventory. Remaining: {new_quantity}x."


def _remove_armor(name: str, quantity: int, game_state: GameState, db: Database) -> str:
    """Remove armor from player inventory."""
    armor_repo = ArmorRepository(db)

    # Find the armor by name
    armors = armor_repo.get_by_world(game_state.world.id, campaign_id=game_state.campaign.id)
    target_armor = None
    for armor in armors:
        if armor.name.lower() == name.lower():
            target_armor = armor
            break

    if not target_armor:
        return f"Error: Armor '{name}' not found in the game world."

    # Check if player has this armor
    cursor = db.conn.execute(
        "SELECT quantity FROM player_armor WHERE player_id = ? AND armor_id = ?",
        (game_state.player.id, target_armor.id),
    )
    row = cursor.fetchone()

    if not row:
        return f"Warning: {game_state.player.name} does not have '{name}' in their inventory."

    current_quantity = row["quantity"]

    if quantity > current_quantity:
        return f"Warning: Cannot remove {quantity}x {name}. Player only has {current_quantity}x in inventory."

    # Update or remove the entry
    if quantity == current_quantity:
        # Remove entirely
        db.conn.execute(
            "DELETE FROM player_armor WHERE player_id = ? AND armor_id = ?",
            (game_state.player.id, target_armor.id),
        )
        db.conn.commit()
        return f"Successfully removed all {name} ({current_quantity}x) from {game_state.player.name}'s inventory."
    else:
        # Reduce quantity
        new_quantity = current_quantity - quantity
        db.conn.execute(
            "UPDATE player_armor SET quantity = ? WHERE player_id = ? AND armor_id = ?",
            (new_quantity, game_state.player.id, target_armor.id),
        )
        db.conn.commit()
        qty_text = f"{quantity}x " if quantity > 1 else ""
        return f"Successfully removed {qty_text}{name} from {game_state.player.name}'s inventory. Remaining: {new_quantity}x."


# Legacy exports for backwards compatibility
TOOL_DEFINITION = VIEW_INVENTORY_TOOL
execute = view_inventory_execute
