"""
The Sword Coast campaign preset (Minimal Template).
A minimal preset demonstrating the extensibility of the campaign system.
This serves as a template for creating new campaign presets.
"""

from ..models import (
    CampaignPreset,
    WorldDefinition,
    LocationDefinition,
    ItemDefinition,
    WeaponDefinition,
    ArmorDefinition,
    NPCDefinition,
    CharacterClassPreset,
)
from ..registry import PresetRegistry
from ...storage.models import (
    Rarity,
    WeaponType,
    HandsRequired,
    ArmorType,
)


# Define the Sword Coast preset
SWORD_COAST_PRESET = CampaignPreset(
    id="sword_coast",
    display_name="The Sword Coast",
    world=WorldDefinition(
        name="The Sword Coast",
        description="The western coastline of Faerûn, a land of bustling cities, dangerous wilds, "
                    "and ancient mysteries. From the great city of Waterdeep to the rough streets of "
                    "Baldur's Gate, adventure awaits those brave enough to seek it."
    ),
    locations=[
        LocationDefinition(
            name="Waterdeep Harbor",
            description="The grand harbor of Waterdeep stretches before you, filled with ships from "
                        "across the Realms. The salty sea air mingles with the scents of exotic spices "
                        "and fresh fish. Sailors, merchants, and adventurers bustle about the docks, "
                        "each with their own story to tell."
        ),
        LocationDefinition(
            name="Baldur's Gate",
            description="The mighty city of Baldur's Gate rises from the coastal plains, its walls "
                        "scarred by countless battles. Inside, the city thrums with commerce and intrigue. "
                        "The streets are crowded with merchants, mercenaries, and mysterious figures "
                        "cloaked in shadow."
        ),
    ],
    items=[
        # Basic healing item
        ItemDefinition(
            name="Health Potion",
            description="A flask of glowing red liquid. Restores 50 HP when consumed.",
            rarity=Rarity.COMMON,
            value=35
        ),
    ],
    weapons=[
        # Basic weapon
        WeaponDefinition(
            name="Longbow",
            description="A finely crafted longbow made from yew wood. Accurate and deadly at range.",
            type=WeaponType.RANGED,
            hands_required=HandsRequired.TWO_HANDED,
            attack=13,
            rarity=Rarity.COMMON,
            value=60
        ),
        WeaponDefinition(
            name="Short Sword",
            description="A versatile blade favored by rangers and scouts.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.ONE_HANDED,
            attack=11,
            rarity=Rarity.COMMON,
            value=45
        ),
    ],
    armor=[
        # Basic armor
        ArmorDefinition(
            name="Studded Leather Armor",
            description="Leather armor reinforced with metal studs. A good balance of protection and mobility.",
            type=ArmorType.CHESTPLATE,
            defense=6,
            rarity=Rarity.COMMON,
            value=50
        ),
        ArmorDefinition(
            name="Ranger's Hood",
            description="A practical hood that provides some protection while keeping you inconspicuous.",
            type=ArmorType.HELMET,
            defense=3,
            rarity=Rarity.COMMON,
            value=20
        ),
    ],
    npcs=[
        # Basic enemies
        NPCDefinition(
            name="Bandit Archer",
            character_class="Rogue",
            character_species="Human",
            hp=30,
            max_hp=30,
            level=2,
            xp=15,
            gold=10
        ),
        NPCDefinition(
            name="Coastal Pirate",
            character_class="Fighter",
            character_species="Human",
            hp=40,
            max_hp=40,
            level=3,
            xp=25,
            gold=20
        ),
    ],
    character_classes={
        "Ranger": CharacterClassPreset(
            name="Ranger",
            description="A skilled tracker and archer, equally at home in wilderness and city",
            character_species="Human",
            stats={
                "strength": 13,
                "dexterity": 16,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 15,
                "charisma": 8
            },
            base_hp=45,
            starting_gold=90,
            equipment_weapons=["Longbow", "Short Sword"],
            equipment_armor=["Studded Leather Armor", "Ranger's Hood"],
            equipment_items=["Health Potion"],
            auto_equip_weapon="Longbow",
            auto_equip_armor=["Studded Leather Armor", "Ranger's Hood"]
        ),
    },
    starting_location_name="Waterdeep Harbor"
)

# Register the preset
PresetRegistry.register(SWORD_COAST_PRESET)
