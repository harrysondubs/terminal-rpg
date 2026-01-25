"""
Campaign creation engine for RPG game.
Handles character class presets, equipment setup, and campaign initialization.
"""

from ..storage.database import Database
from ..storage.models import Campaign, Player, World
from ..storage.repositories import (
    WorldRepository,
    CampaignRepository,
    PlayerRepository,
    ItemRepository,
    WeaponRepository,
    ArmorRepository,
)


def get_available_worlds(db: Database) -> list[World]:
    """
    Query all available worlds from the database.

    Args:
        db: Connected Database instance

    Returns:
        List of World objects
    """
    world_repo = WorldRepository(db)
    return world_repo.get_all()


def create_character_class_presets() -> dict[str, dict]:
    """
    Return character class definitions with stats and equipment.

    Returns:
        Dictionary mapping class names to their configuration:
        {
            "Fighter": {
                "name": "Fighter",
                "description": "...",
                "character_race": "Human",
                "stats": {...},
                "base_hp": 50,
                "starting_gold": 100,
                "equipment": {...},
                "auto_equip": {...}
            },
            ...
        }
    """
    return {
        "Fighter": {
            "name": "Fighter",
            "description": "A mighty warrior skilled in melee combat and heavy armor",
            "character_race": "Human",
            "stats": {
                "strength": 16,
                "dexterity": 12,
                "constitution": 15,
                "intelligence": 8,
                "wisdom": 10,
                "charisma": 9
            },
            "base_hp": 50,
            "starting_gold": 100,
            "equipment": {
                "weapons": ["Iron Sword", "Battle Axe"],
                "armor": ["Leather Armor", "Steel Helmet"],
                "items": ["Minor Health Potion"]
            },
            "auto_equip": {
                "weapon": "Iron Sword",
                "armor": ["Leather Armor", "Steel Helmet"]
            }
        },
        "Thief": {
            "name": "Thief",
            "description": "A nimble rogue who relies on speed, stealth, and precision",
            "character_race": "Halfling",
            "stats": {
                "strength": 10,
                "dexterity": 17,
                "constitution": 12,
                "intelligence": 11,
                "wisdom": 12,
                "charisma": 14
            },
            "base_hp": 40,
            "starting_gold": 75,
            "equipment": {
                "weapons": ["Rusty Dagger", "Wooden Bow"],
                "armor": ["Leather Armor", "Leather Boots"],
                "items": ["Minor Health Potion"]
            },
            "auto_equip": {
                "weapon": "Rusty Dagger",
                "armor": ["Leather Armor", "Leather Boots"]
            }
        },
        "Bard": {
            "name": "Bard",
            "description": "A charismatic performer who weaves magic through music and words",
            "character_race": "Elf",
            "stats": {
                "strength": 9,
                "dexterity": 13,
                "constitution": 11,
                "intelligence": 14,
                "wisdom": 12,
                "charisma": 16
            },
            "base_hp": 35,
            "starting_gold": 80,
            "equipment": {
                "weapons": ["Rusty Dagger", "Wooden Bow"],
                "armor": ["Leather Armor", "Leather Cap"],
                "items": ["Minor Health Potion"]
            },
            "auto_equip": {
                "weapon": "Rusty Dagger",
                "armor": ["Leather Armor", "Leather Cap"]
            }
        }
    }


def create_new_campaign(
    db: Database,
    world_id: int,
    campaign_name: str,
    player_name: str,
    player_description: str,
    class_preset: dict
) -> tuple[Campaign, Player]:
    """
    Create a new campaign with player and starting inventory.
    All operations are atomic - if any step fails, entire transaction rolls back.

    Args:
        db: Connected Database instance
        world_id: ID of selected world
        campaign_name: Name for the campaign
        player_name: Player's character name
        player_description: Character background/appearance
        class_preset: Class configuration dict from create_character_class_presets()

    Returns:
        Tuple of (Campaign, Player) with IDs populated

    Raises:
        ValueError: If equipment not found in database
        sqlite3.Error: If any database operation fails
    """
    # Get repositories
    campaign_repo = CampaignRepository(db)
    player_repo = PlayerRepository(db)

    # 1. Create Campaign
    campaign = campaign_repo.create(Campaign(
        name=campaign_name,
        world_id=world_id
    ))

    # 2. Calculate HP from constitution
    constitution = class_preset['stats']['constitution']
    max_hp = class_preset['base_hp'] + (constitution * 2)

    # 3. Create Player with class stats
    player = player_repo.create(Player(
        campaign_id=campaign.id,
        name=player_name,
        description=player_description,
        character_class=class_preset['name'],
        character_race=class_preset['character_race'],
        level=1,
        xp=0,
        hp=max_hp,
        max_hp=max_hp,
        gold=class_preset['starting_gold'],
        strength=class_preset['stats']['strength'],
        dexterity=class_preset['stats']['dexterity'],
        constitution=class_preset['stats']['constitution'],
        intelligence=class_preset['stats']['intelligence'],
        wisdom=class_preset['stats']['wisdom'],
        charisma=class_preset['stats']['charisma']
    ))

    # 4. Resolve equipment IDs from names
    equipment_ids = _resolve_equipment_ids(db, world_id, class_preset['equipment'])

    # 5. Add equipment to inventory and auto-equip
    _add_starting_equipment(db, player.id, equipment_ids, class_preset['auto_equip'])

    return campaign, player


def _resolve_equipment_ids(
    db: Database,
    world_id: int,
    equipment_config: dict
) -> dict[str, list[int]]:
    """
    Convert equipment names to database IDs.

    Args:
        db: Connected Database instance
        world_id: World ID to query equipment from
        equipment_config: Dict with keys 'weapons', 'armor', 'items'
                         containing lists of equipment names

    Returns:
        Dict with keys 'weapon_ids', 'armor_ids', 'item_ids'
        containing lists of resolved IDs

    Raises:
        ValueError: If any equipment name not found in database
    """
    item_repo = ItemRepository(db)
    weapon_repo = WeaponRepository(db)
    armor_repo = ArmorRepository(db)

    # Get all equipment for this world
    all_items = item_repo.get_by_world(world_id)
    all_weapons = weapon_repo.get_by_world(world_id)
    all_armor = armor_repo.get_by_world(world_id)

    # Create name -> id mappings
    item_map = {item.name: item.id for item in all_items}
    weapon_map = {weapon.name: weapon.id for weapon in all_weapons}
    armor_map = {armor.name: armor.id for armor in all_armor}

    # Resolve IDs
    weapon_ids = []
    for weapon_name in equipment_config.get('weapons', []):
        if weapon_name not in weapon_map:
            raise ValueError(f"Weapon '{weapon_name}' not found in world {world_id}")
        weapon_ids.append(weapon_map[weapon_name])

    armor_ids = []
    for armor_name in equipment_config.get('armor', []):
        if armor_name not in armor_map:
            raise ValueError(f"Armor '{armor_name}' not found in world {world_id}")
        armor_ids.append(armor_map[armor_name])

    item_ids = []
    for item_name in equipment_config.get('items', []):
        if item_name not in item_map:
            raise ValueError(f"Item '{item_name}' not found in world {world_id}")
        item_ids.append(item_map[item_name])

    return {
        'weapon_ids': weapon_ids,
        'armor_ids': armor_ids,
        'item_ids': item_ids
    }


def _add_starting_equipment(
    db: Database,
    player_id: int,
    equipment_ids: dict,
    auto_equip_config: dict
) -> None:
    """
    Add equipment to player inventory and auto-equip specified items.

    Args:
        db: Connected Database instance
        player_id: Player ID
        equipment_ids: Resolved equipment IDs from _resolve_equipment_ids
        auto_equip_config: Dict specifying which items to equip
    """
    player_repo = PlayerRepository(db)
    weapon_repo = WeaponRepository(db)
    armor_repo = ArmorRepository(db)

    # Get all equipment to create name->id mappings for auto-equip
    all_weapons = {w.id: w for w in [weapon_repo.get_by_id(wid) for wid in equipment_ids['weapon_ids']]}
    all_armor = {a.id: a for a in [armor_repo.get_by_id(aid) for aid in equipment_ids['armor_ids']]}

    # Add items (consumables - not equipped)
    for item_id in equipment_ids['item_ids']:
        player_repo.add_item(player_id, item_id, quantity=1)

    # Add weapons
    for weapon_id in equipment_ids['weapon_ids']:
        player_repo.add_weapon(player_id, weapon_id, quantity=1)

    # Add armor
    for armor_id in equipment_ids['armor_ids']:
        player_repo.add_armor(player_id, armor_id, quantity=1)

    # Auto-equip primary weapon
    primary_weapon_name = auto_equip_config.get('weapon')
    if primary_weapon_name:
        for weapon_id, weapon in all_weapons.items():
            if weapon.name == primary_weapon_name:
                player_repo.equip_weapon(player_id, weapon_id)
                break

    # Auto-equip armor pieces
    armor_to_equip = auto_equip_config.get('armor', [])
    for armor_id, armor in all_armor.items():
        if armor.name in armor_to_equip:
            player_repo.equip_armor(player_id, armor_id)
