"""
Preset loader for inserting preset data into the database.
Handles idempotent loading of worlds, locations, equipment, and NPCs.
"""

from ..storage.database import Database
from ..storage.models import (
    NPC,
    Armor,
    Item,
    Location,
    Weapon,
    World,
)
from ..storage.repositories import (
    ArmorRepository,
    ItemRepository,
    LocationRepository,
    NPCRepository,
    WeaponRepository,
    WorldRepository,
)
from .models import (
    ArmorDefinition,
    CampaignPreset,
    ItemDefinition,
    LocationDefinition,
    NPCDefinition,
    WeaponDefinition,
    WorldDefinition,
)


class PresetLoader:
    """
    Loads campaign preset data into the database.
    All operations are idempotent - safe to call multiple times without duplicating data.
    """

    def __init__(self, db: Database):
        self.db = db

    def load_preset(self, preset: CampaignPreset) -> int:
        """
        Load a campaign preset into the database.

        Args:
            preset: The CampaignPreset to load

        Returns:
            The world_id of the loaded world

        Raises:
            ValueError: If preset data is invalid
        """
        # 1. Ensure world exists
        world_id = self._ensure_world(preset.world)

        # 2. Ensure locations exist
        self._ensure_locations(world_id, preset.locations)

        # 3. Ensure equipment exists
        self._ensure_equipment(world_id, preset.items, preset.weapons, preset.armor)

        # 4. Ensure NPCs exist
        self._ensure_npcs(world_id, preset.npcs)

        return world_id

    def _ensure_world(self, world_def: WorldDefinition) -> int:
        """
        Get or create a world by name.

        Args:
            world_def: World definition

        Returns:
            World ID
        """
        world_repo = WorldRepository(self.db)

        # Check if world already exists
        all_worlds = world_repo.get_all()
        for world in all_worlds:
            if world.name == world_def.name:
                return world.id

        # Create new world
        world = world_repo.create(World(name=world_def.name, description=world_def.description))

        return world.id

    def _ensure_locations(self, world_id: int, locations: list[LocationDefinition]) -> None:
        """
        Insert locations if they don't already exist.

        Args:
            world_id: World ID
            locations: List of location definitions
        """
        location_repo = LocationRepository(self.db)

        # Get existing locations for this world
        existing_locations = location_repo.get_by_world(world_id)
        existing_names = {loc.name for loc in existing_locations}

        # Insert new locations
        for loc_def in locations:
            if loc_def.name not in existing_names:
                location_repo.create(
                    Location(world_id=world_id, name=loc_def.name, description=loc_def.description)
                )

    def _ensure_equipment(
        self,
        world_id: int,
        items: list[ItemDefinition],
        weapons: list[WeaponDefinition],
        armor: list[ArmorDefinition],
    ) -> None:
        """
        Insert equipment if it doesn't already exist.

        Args:
            world_id: World ID
            items: List of item definitions
            weapons: List of weapon definitions
            armor: List of armor definitions
        """
        # Handle items
        item_repo = ItemRepository(self.db)
        existing_items = item_repo.get_by_world(world_id)
        existing_item_names = {item.name for item in existing_items}

        for item_def in items:
            if item_def.name not in existing_item_names:
                item_repo.create(
                    Item(
                        world_id=world_id,
                        name=item_def.name,
                        description=item_def.description,
                        rarity=item_def.rarity,
                        value=item_def.value,
                    )
                )

        # Handle weapons
        weapon_repo = WeaponRepository(self.db)
        existing_weapons = weapon_repo.get_by_world(world_id)
        existing_weapon_names = {weapon.name for weapon in existing_weapons}

        for weapon_def in weapons:
            if weapon_def.name not in existing_weapon_names:
                weapon_repo.create(
                    Weapon(
                        world_id=world_id,
                        name=weapon_def.name,
                        description=weapon_def.description,
                        type=weapon_def.type,
                        hands_required=weapon_def.hands_required,
                        damage_dice_count=weapon_def.damage_dice_count,
                        damage_dice_sides=weapon_def.damage_dice_sides,
                        rarity=weapon_def.rarity,
                        value=weapon_def.value,
                    )
                )

        # Handle armor
        armor_repo = ArmorRepository(self.db)
        existing_armor = armor_repo.get_by_world(world_id)
        existing_armor_names = {armor.name for armor in existing_armor}

        for armor_def in armor:
            if armor_def.name not in existing_armor_names:
                armor_repo.create(
                    Armor(
                        world_id=world_id,
                        name=armor_def.name,
                        description=armor_def.description,
                        type=armor_def.type,
                        ac=armor_def.ac,
                        rarity=armor_def.rarity,
                        value=armor_def.value,
                    )
                )

    def _ensure_npcs(self, world_id: int, npcs: list[NPCDefinition]) -> None:
        """
        Insert NPCs if they don't already exist.

        Args:
            world_id: World ID
            npcs: List of NPC definitions
        """
        npc_repo = NPCRepository(self.db)

        # Get existing NPCs for this world
        existing_npcs = npc_repo.get_by_world(world_id)
        existing_npc_names = {npc.name for npc in existing_npcs}

        # Insert new NPCs
        for npc_def in npcs:
            if npc_def.name not in existing_npc_names:
                npc_repo.create(
                    NPC(
                        world_id=world_id,
                        name=npc_def.name,
                        character_class=npc_def.character_class,
                        character_species=npc_def.character_species,
                        hp=npc_def.hp,
                        max_hp=npc_def.max_hp,
                        level=npc_def.level,
                        xp=npc_def.xp,
                        gold=npc_def.gold,
                        disposition=npc_def.disposition,
                    )
                )
