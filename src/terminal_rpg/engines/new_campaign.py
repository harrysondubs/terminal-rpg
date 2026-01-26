"""
Campaign creation engine for RPG game.
Handles preset-based campaign creation with equipment setup and initialization.
"""

from ..storage.database import Database
from ..storage.models import Campaign, Player
from ..storage.repositories import (
    CampaignRepository,
    PlayerRepository,
    ItemRepository,
    WeaponRepository,
    ArmorRepository,
    LocationRepository,
)
from ..campaign_presets import CampaignPreset, CharacterClassPreset, PresetRegistry, PresetLoader


def get_available_presets() -> list[CampaignPreset]:
    """
    Get all available campaign presets.

    Returns:
        List of CampaignPreset objects
    """
    PresetRegistry.discover_presets()
    return PresetRegistry.get_all()


def load_preset_into_database(db: Database, preset: CampaignPreset) -> int:
    """
    Load a campaign preset into the database.

    Args:
        db: Connected Database instance
        preset: The CampaignPreset to load

    Returns:
        The world_id of the loaded world
    """
    loader = PresetLoader(db)
    return loader.load_preset(preset)


def create_new_campaign_from_preset(
    db: Database,
    preset: CampaignPreset,
    campaign_name: str,
    player_name: str,
    player_description: str,
    class_preset: CharacterClassPreset
) -> tuple[Campaign, Player]:
    """
    Create a new campaign from a campaign preset.
    All operations are atomic - if any step fails, entire transaction rolls back.

    Args:
        db: Connected Database instance
        preset: The CampaignPreset to use
        campaign_name: Name for the campaign
        player_name: Player's character name
        player_description: Character background/appearance
        class_preset: CharacterClassPreset from the preset

    Returns:
        Tuple of (Campaign, Player) with IDs populated

    Raises:
        ValueError: If equipment not found in database
        sqlite3.Error: If any database operation fails
    """
    # 1. Load preset into database (idempotent)
    world_id = load_preset_into_database(db, preset)

    # Get repositories
    campaign_repo = CampaignRepository(db)
    player_repo = PlayerRepository(db)
    location_repo = LocationRepository(db)

    # 2. Find starting location
    locations = location_repo.get_by_world(world_id)
    starting_location = None
    for loc in locations:
        if loc.name == preset.starting_location_name:
            starting_location = loc
            break

    # Fallback to first location if specified starting location not found
    if not starting_location and locations:
        starting_location = locations[0]

    if not starting_location:
        raise ValueError(f"No locations found in world {world_id}")

    # 3. Create Campaign with starting location
    campaign = campaign_repo.create(Campaign(
        name=campaign_name,
        world_id=world_id,
        current_location_id=starting_location.id
    ))

    # 4. Calculate HP from constitution
    constitution = class_preset.stats['constitution']
    max_hp = class_preset.base_hp + (constitution * 2)

    # 5. Create Player with class stats
    player = player_repo.create(Player(
        campaign_id=campaign.id,
        name=player_name,
        description=player_description,
        character_class=class_preset.name,
        character_race=class_preset.character_race,
        level=1,
        xp=0,
        hp=max_hp,
        max_hp=max_hp,
        gold=class_preset.starting_gold,
        strength=class_preset.stats['strength'],
        dexterity=class_preset.stats['dexterity'],
        constitution=class_preset.stats['constitution'],
        intelligence=class_preset.stats['intelligence'],
        wisdom=class_preset.stats['wisdom'],
        charisma=class_preset.stats['charisma']
    ))

    # 6. Resolve equipment IDs from names
    equipment_config = {
        'weapons': class_preset.equipment_weapons,
        'armor': class_preset.equipment_armor,
        'items': class_preset.equipment_items
    }
    equipment_ids = _resolve_equipment_ids(db, world_id, equipment_config)

    # 7. Add equipment to inventory and auto-equip
    auto_equip_config = {
        'weapon': class_preset.auto_equip_weapon,
        'armor': class_preset.auto_equip_armor
    }
    _add_starting_equipment(db, player.id, equipment_ids, auto_equip_config)

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
