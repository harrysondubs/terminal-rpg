"""
Campaign Preset Template
Copy this file and customize it to create your own campaign preset.

Replace all PLACEHOLDER values with your own content.
Delete or add sections as needed for your campaign.

IMPORTANT: Be sure to update the __init__.py file to import your preset.
"""

from ...storage.models import (
    ArmorType,
    DamageDiceSides,
    HandsRequired,
    Rarity,
    WeaponType,
)
from ..models import (
    ArmorDefinition,
    CampaignPreset,
    CharacterClassPreset,
    ItemDefinition,
    LocationDefinition,
    WeaponDefinition,
    WorldDefinition,
)
from ..registry import PresetRegistry

# Define your campaign preset
YOUR_PRESET_NAME = CampaignPreset(
    # STEP 1: Set the unique ID and display name for your campaign
    id="your_preset_id",  # Must be unique, lowercase with underscores
    display_name="Your Campaign Name",  # What players will see in the menu
    # STEP 2: Define the world
    world=WorldDefinition(
        name="Your World Name",
        description="A brief, engaging description of your world. "
        "What makes it unique? What can players expect? "
        "Paint a picture that draws them in.",
    ),
    # STEP 3: Create a starting location
    locations=[
        LocationDefinition(
            name="starting_location",
            description="A detailed description of this location. "
            "What does it look like? What sounds, smells, sights are present? "
            "Who or what might be found here?",
        ),
    ],
    # STEP 4: Define basic consumable items
    # These should be available to all character classes
    items=[
        ItemDefinition(
            name="item_1",
            description="Restores health when consumed. Describe the effect and appearance.",
            rarity=Rarity.COMMON,  # COMMON, RARE, LEGENDARY
            value=15,  # Gold value
        ),
        ItemDefinition(
            name="item_2",
            description="A unique item for your world. Could be food, tools, or quest items.",
            rarity=Rarity.COMMON,
            value=10,
        ),
    ],
    # STEP 5: Define weapons for your character classes
    # Create at least one weapon for each class you plan to include
    weapons=[
        # Example: Melee one-handed weapon
        WeaponDefinition(
            name="melee_weapon_1",
            description="A standard melee weapon.",
            type=WeaponType.MELEE,  # MELEE or RANGED
            hands_required=HandsRequired.ONE_HANDED,  # ONE_HANDED or TWO_HANDED
            damage_dice_count=1,  # Number of dice to roll
            damage_dice_sides=DamageDiceSides.D8,  # D4, D6, D8, D10, or D12
            rarity=Rarity.COMMON,
            value=50,
        ),
        # Example: Melee two-handed weapon
        WeaponDefinition(
            name="melee_weapon_2",
            description="A powerful two-handed weapon.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.TWO_HANDED,
            damage_dice_count=1,  # Higher damage dice for two-handed
            damage_dice_sides=DamageDiceSides.D12,
            rarity=Rarity.COMMON,
            value=75,
        ),
        # Example: Light melee weapon
        WeaponDefinition(
            name="melee_weapon_3",
            description="A quick, nimble weapon.",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.ONE_HANDED,
            damage_dice_count=1,  # Lower damage dice for light weapons
            damage_dice_sides=DamageDiceSides.D4,
            rarity=Rarity.COMMON,
            value=25,
        ),
        # Example: Ranged weapon
        WeaponDefinition(
            name="ranged_weapon_1",
            description="A weapon for attacking from distance.",
            type=WeaponType.RANGED,
            hands_required=HandsRequired.TWO_HANDED,  # Most ranged weapons are two-handed
            damage_dice_count=1,
            damage_dice_sides=DamageDiceSides.D8,
            rarity=Rarity.COMMON,
            value=40,
        ),
    ],
    # STEP 6: Define armor pieces
    # Types: LIGHT, MEDIUM, HEAVY, SHIELD
    # AC values: LIGHT (11-12), MEDIUM (13-15), HEAVY (16-18), SHIELD (+1 to +3 bonus)
    armor=[
        # Example: Light armor - good for rogues, rangers, light classes
        ArmorDefinition(
            name="light_armor_1",
            description="Light, flexible armor that doesn't restrict movement.",
            type=ArmorType.LIGHT,
            ac=11,  # Base AC for light armor (11-12 typical)
            rarity=Rarity.COMMON,
            value=50,
        ),
        # Example: Medium armor - balanced protection and mobility
        ArmorDefinition(
            name="medium_armor_1",
            description="Balanced armor providing good protection without too much weight.",
            type=ArmorType.MEDIUM,
            ac=14,  # Base AC for medium armor (13-15 typical)
            rarity=Rarity.COMMON,
            value=100,
        ),
        # Example: Heavy armor - maximum protection for warriors
        ArmorDefinition(
            name="heavy_armor_1",
            description="Heavy, full-body armor. Maximum protection but restricts movement.",
            type=ArmorType.HEAVY,
            ac=17,  # Base AC for heavy armor (16-18 typical)
            rarity=Rarity.RARE,
            value=300,
        ),
        # Example: Shield - provides AC bonus when equipped with one-handed weapon
        ArmorDefinition(
            name="shield_1",
            description="A sturdy shield for blocking attacks.",
            type=ArmorType.SHIELD,
            ac=2,  # AC bonus when shield is equipped (+1 to +3 typical, +2 standard)
            rarity=Rarity.COMMON,
            value=40,
        ),
    ],
    # STEP 7: NPCs can be left empty - they're created during gameplay
    # NPCs are typically generated dynamically, but you can predefine some if desired
    npcs=[
        # Example NPC (uncomment and customize if needed):
        # NPCDefinition(
        #     name="Hostile Bandit",
        #     description="A rough-looking bandit wielding a rusty blade",
        #     character_class="Bandit",
        #     character_species="Human",
        #     hp=25,
        #     max_hp=25,
        #     ac=12,  # Light armor
        #     attack_mod=2,  # Attack bonus
        #     damage_dice_count=1,
        #     damage_dice_sides=DamageDiceSides.D6,
        #     initiative_mod=1,  # Initiative bonus (dexterity-based typically)
        #     level=2,
        #     xp=50,
        #     gold=15,
        #     disposition=Disposition.HOSTILE,
        # ),
    ],
    # STEP 8: Define 2-4 character classes
    # Each class should have unique stats, equipment, and flavor
    character_classes={
        "character_class_1": CharacterClassPreset(
            name="character_class_1",
            description="description_of_character_class_1",
            character_species="character_species_1",  # The race/species of this class
            # Stats: Total should be around 60-70 for balanced gameplay
            # Distribute based on class role
            stats={
                "strength": 10,  # Physical power (melee damage)
                "dexterity": 10,  # Agility and speed
                "constitution": 10,  # Health and endurance
                "intelligence": 10,  # Magic and knowledge
                "wisdom": 10,  # Perception and insight
                "charisma": 10,  # Social skills and leadership
            },
            base_hp=50,  # Starting health (35-50 typical)
            starting_gold=50,  # Starting money
            # Equipment lists (must match weapon/armor names defined above)
            equipment_weapons=["melee_weapon_1", "melee_weapon_2"],
            equipment_armor=["chestplate_1", "helmet_1"],
            equipment_items=["item_1", "item_2"],
            # Auto-equip (optional - what's equipped at game start)
            auto_equip_weapon="melee_weapon_1",
            auto_equip_armor=["chestplate_1", "helmet_1"],
        ),
        "character_class_2": CharacterClassPreset(
            name="character_class_2",
            description="description_of_character_class_2",
            character_species="character_species_2",
            stats={
                "strength": 10,
                "dexterity": 10,  # High dexterity for rogues
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            },
            base_hp=40,  # Lower HP for agile classes
            starting_gold=50,
            equipment_weapons=["melee_weapon_3", "ranged_weapon_1"],
            equipment_armor=["chestplate_1", "boots_1"],
            equipment_items=["item_1", "item_2"],
            auto_equip_weapon="melee_weapon_3",
            auto_equip_armor=["chestplate_1", "boots_1"],
        ),
    },
    # STEP 9: Set the starting location (must match a location name above)
    starting_location_name="starting_location",
)

# STEP 10: Register your preset so it appears in the game
PresetRegistry.register(YOUR_PRESET_NAME)
