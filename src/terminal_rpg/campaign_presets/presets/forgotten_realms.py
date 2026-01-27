"""
The Forgotten Realms campaign preset.
A classic fantasy world with diverse locations, equipment, and character classes.
"""

from ..models import (
    CampaignPreset,
    WorldDefinition,
    LocationDefinition,
    ItemDefinition,
    WeaponDefinition,
    ArmorDefinition,
    CharacterClassPreset,
)
from ..registry import PresetRegistry
from ...storage.models import (
    Rarity,
    WeaponType,
    HandsRequired,
    ArmorType,
)


# Define the Forgotten Realms preset
FORGOTTEN_REALMS_PRESET = CampaignPreset(
    id="forgotten_realms",
    display_name="The Forgotten Realms",
    world=WorldDefinition(
        name="The Forgotten Realms",
        description="A vast fantasy world shrouded in mystery and ancient magic. "
                    "Brave adventurers explore forgotten dungeons, battle fearsome creatures, "
                    "and uncover legendary treasures. Will you become a hero of legend?"
    ),
    locations=[
        LocationDefinition(
            name="The Prancing Pony Inn",
            description="A warm and welcoming tavern with a crackling fireplace. "
                        "The smell of roasted meat and fresh bread fills the air. "
                        "Adventurers gather here to share tales, find companions, and hear rumors of treasure. "
                        "The innkeeper, a jovial halfling named Baldo, greets you with a wide smile."
        ),
        LocationDefinition(
            name="Whispering Woods",
            description="Ancient trees tower above you, their leaves rustling with secrets. "
                        "Dappled sunlight filters through the canopy, illuminating a winding path. "
                        "You hear the distant calls of birds and the occasional snap of a twig. "
                        "This forest is known to harbor both friendly creatures and lurking dangers."
        ),
        LocationDefinition(
            name="Ruins of Shadowkeep",
            description="The crumbling remains of an ancient fortress loom before you. "
                        "Dark stone walls are covered in creeping vines and mysterious runes. "
                        "A sense of foreboding hangs in the air. Local legends speak of untold riches "
                        "hidden within, guarded by creatures that should have died long ago."
        ),
        LocationDefinition(
            name="Crystal Caverns",
            description="Luminescent crystals jut from the cavern walls, casting an ethereal blue glow. "
                        "The sound of dripping water echoes through the chambers. "
                        "These caves are said to be touched by ancient magic, and those who enter "
                        "sometimes emerge changed, for better or worse."
        ),
        LocationDefinition(
            name="Millhaven Village",
            description="A quaint village nestled in a peaceful valley. "
                        "Farmers tend their fields, blacksmiths hammer at their forges, "
                        "and children play in the town square. The villagers are friendly but cautious, "
                        "having learned to be wary of strangers after recent goblin raids."
        ),
    ],
    items=[
        # Starting item for all classes
        ItemDefinition(
            name="Minor Health Potion",
            description="A small vial of crimson liquid. Restores 25 HP when consumed.",
            rarity=Rarity.COMMON,
            value=15
        ),
    ],
    weapons=[
        # Fighter weapons
        WeaponDefinition(
            name="Iron Sword",
            description="A well-balanced blade of solid iron. A reliable weapon for any warrior.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.ONE_HANDED,
            attack=12,
            rarity=Rarity.COMMON,
            value=50
        ),
        WeaponDefinition(
            name="Battle Axe",
            description="A heavy, double-bladed axe. Requires two hands but deals devastating damage.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.TWO_HANDED,
            attack=18,
            rarity=Rarity.COMMON,
            value=75
        ),
        # Thief and Bard weapons
        WeaponDefinition(
            name="Rusty Dagger",
            description="A small, worn blade. Better than nothing, barely.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.ONE_HANDED,
            attack=5,
            rarity=Rarity.COMMON,
            value=10
        ),
        WeaponDefinition(
            name="Wooden Bow",
            description="A simple bow carved from flexible oak. Good for hunting and combat.",
            type=WeaponType.RANGED,
            hands_required=HandsRequired.TWO_HANDED,
            attack=10,
            rarity=Rarity.COMMON,
            value=40
        ),
    ],
    armor=[
        # Shared by all classes
        ArmorDefinition(
            name="Leather Armor",
            description="Sturdy leather armor, hardened and treated. Light and flexible.",
            type=ArmorType.CHESTPLATE,
            defense=5,
            rarity=Rarity.COMMON,
            value=40
        ),
        # Fighter armor
        ArmorDefinition(
            name="Steel Helmet",
            description="A polished steel helm with a protective visor.",
            type=ArmorType.HELMET,
            defense=8,
            rarity=Rarity.RARE,
            value=100
        ),
        # Thief armor
        ArmorDefinition(
            name="Leather Boots",
            description="Well-worn leather boots. Comfortable for long journeys.",
            type=ArmorType.BOOTS,
            defense=2,
            rarity=Rarity.COMMON,
            value=15
        ),
        # Bard armor
        ArmorDefinition(
            name="Leather Cap",
            description="A simple leather helmet. Provides minimal protection.",
            type=ArmorType.HELMET,
            defense=2,
            rarity=Rarity.COMMON,
            value=15
        ),
    ],
    npcs=[
        # NPCs are not needed for initial campaign setup
        # They can be added later as the game progresses
    ],
    character_classes={
        "Fighter": CharacterClassPreset(
            name="Fighter",
            description="A mighty warrior skilled in melee combat and heavy armor",
            character_species="Human",
            stats={
                "strength": 16,
                "dexterity": 12,
                "constitution": 15,
                "intelligence": 8,
                "wisdom": 10,
                "charisma": 9
            },
            base_hp=50,
            starting_gold=100,
            equipment_weapons=["Iron Sword", "Battle Axe"],
            equipment_armor=["Leather Armor", "Steel Helmet"],
            equipment_items=["Minor Health Potion"],
            auto_equip_weapon="Iron Sword",
            auto_equip_armor=["Leather Armor", "Steel Helmet"]
        ),
        "Thief": CharacterClassPreset(
            name="Thief",
            description="A nimble rogue who relies on speed, stealth, and precision",
            character_species="Halfling",
            stats={
                "strength": 10,
                "dexterity": 17,
                "constitution": 12,
                "intelligence": 11,
                "wisdom": 12,
                "charisma": 14
            },
            base_hp=40,
            starting_gold=75,
            equipment_weapons=["Rusty Dagger", "Wooden Bow"],
            equipment_armor=["Leather Armor", "Leather Boots"],
            equipment_items=["Minor Health Potion"],
            auto_equip_weapon="Rusty Dagger",
            auto_equip_armor=["Leather Armor", "Leather Boots"]
        ),
        "Bard": CharacterClassPreset(
            name="Bard",
            description="A charismatic performer who weaves magic through music and words",
            character_species="Elf",
            stats={
                "strength": 9,
                "dexterity": 13,
                "constitution": 11,
                "intelligence": 14,
                "wisdom": 12,
                "charisma": 16
            },
            base_hp=35,
            starting_gold=80,
            equipment_weapons=["Rusty Dagger", "Wooden Bow"],
            equipment_armor=["Leather Armor", "Leather Cap"],
            equipment_items=["Minor Health Potion"],
            auto_equip_weapon="Rusty Dagger",
            auto_equip_armor=["Leather Armor", "Leather Cap"]
        ),
    },
    starting_location_name="The Prancing Pony Inn"
)

# Register the preset
PresetRegistry.register(FORGOTTEN_REALMS_PRESET)
