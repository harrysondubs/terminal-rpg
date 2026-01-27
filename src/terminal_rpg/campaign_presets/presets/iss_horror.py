"""
The ISS Horror campaign preset.
A hard-science horror campaign set aboard the International Space Station.
Starting character classes are minimalistic and focused on survival.
"""

from ...storage.models import (
    ArmorType,
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

ISS_HORROR_PRESET = CampaignPreset(
    # STEP 1: Set the unique ID and display name for your campaign
    id="iss_horror",  # Must be unique, lowercase with underscores
    display_name="Horror on the ISS",  # What players will see in the menu
    # STEP 2: Define the world
    world=WorldDefinition(
        name="Horror on the ISS",
        description="A hard-science horror campaign set aboard the International Space Station. "
        "Something happened during the last scheduled experiment; crew logs are incomplete, contradictory, paranoid. "
        "Now, the station's orbit is decaying faster than models predicted and contact with ground control has grown increasingly erratic. "
        "Hard science rules the day, and every actions has an equal and opposite reaction. "
        "Resources are finite: oxygen reserves, power cells, medical supplies, and sanity all tick downward. "
        "Outside, Earth turns silently below. Inside, the station's recycled air tastes metallic. The walls groan and pop. "
        "Every decision has consequences. Save one person, sacrifice another. Vent a module, lose critical supplies. "
        "Trust your crewmates, or trust your survival instincts. In space, no one can hear you scream, but your crew can hear everything else.",
    ),
    # STEP 3: Create a starting location
    locations=[
        LocationDefinition(
            name="U.S. Lab | Destiny Module",
            description="The Destiny laboratory module serves as the station's primary research facility. Rack upon rack of equipment lines the curved walls; "
            "microscopes, specimen freezers, glove boxes, all illuminated by harsh LED strips that flicker intermittently. "
            "A single nadir-facing window, only 508mm across, frames the earth below. "
            "The air circulation creates a constant low hum, punctuated by the rhythmic clicking of cooling pumps and the occasional groan of metal expanding in sunlight. "
            "It smells of disinfectant, ozone, and something organic that shouldn't be there. "
            "Laptops float tethered to workstations, their screens frozen on half-written reports and biometric warnings. "
            "The temperature reads 2 degrees below normal. One of the overhead panels has been removed, revealing a tangle of wires and ducting. "
            "Coffee globules drift lazily near the ceiling... someone left in a hurry. The emergency comms panel blinks red, unanswered."
            "**Adjacent Modules** The Destiny Module is connected to Unity Module (Node 1) and Harmony Module (Node 2), "
            "locations which must be passed through to access other parts of the station.",
        ),
    ],
    # STEP 4: Define basic consumable items
    # These should be available to all character classes
    items=[
        ItemDefinition(
            name="Omega Speedmaster Skywalker X-33 Wristwatch",
            description="A highly precise titanium wristwatch with a thermo-compensated quartz chronograph movement",
            rarity=Rarity.RARE,  # COMMON, RARE, LEGENDARY
            value=3000,  # Gold value
        ),
        ItemDefinition(
            name="Sturmanskie Sputnik Wristwatch",
            description="A heritage wristwatch worn by Russian Cosmonauts since the 1960's",
            rarity=Rarity.RARE,
            value=1850,
        ),
        ItemDefinition(
            name="Family Photo",
            description="A photo of the ISS crewmember with their family back on earth",
            rarity=Rarity.COMMON,
            value=1,
        ),
    ],
    # STEP 5: Define weapons for your character classes
    weapons=[
        WeaponDefinition(
            name="Lab Scalpel",
            description="A small, handheld scalpel with a razor-sharp edge, perfect for cutting through organic specimens",
            type=WeaponType.MELEE,  # MELEE or RANGED
            hands_required=HandsRequired.ONE_HANDED,  # ONE_HANDED or TWO_HANDED
            attack=5,  # Attack power (5-20 is typical range)
            rarity=Rarity.COMMON,
            value=12,
        ),
        WeaponDefinition(
            name="Fire Extinguisher",
            description="A heavy fire extinguisher with a nozzle and hose, filled with a pressurized foam solution",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.TWO_HANDED,
            attack=12,  # Higher attack for two-handed
            rarity=Rarity.COMMON,
            value=25,
        ),
        WeaponDefinition(
            name="Wrench",
            description="A heavy wrench with a metal handle and a rubber grip",
            type=WeaponType.MELEE,
            hands_required=HandsRequired.ONE_HANDED,
            attack=8,  # Lower attack for light weapons
            rarity=Rarity.COMMON,
            value=18,
        ),
    ],
    # STEP 6: Define armor pieces
    # Types: HELMET, CHESTPLATE, BOOTS
    armor=[
        ArmorDefinition(
            name="ISS Polo Shirt",
            description="A standard-issue polo shirt for ISS crewmembers",
            type=ArmorType.CHESTPLATE,
            defense=1,
            rarity=Rarity.COMMON,
            value=10,
        ),
    ],
    # STEP 7: NPCs can be left empty - they're created during gameplay
    npcs=[],
    # STEP 8: Define 2-4 character classes
    character_classes={
        "American ISS Commander (NASA)": CharacterClassPreset(
            name="American ISS Commander (NASA)",
            description="A former US Navy pilot with a strong background in spaceflight and leadership",
            character_species="Human",
            stats={
                "strength": 12,
                "dexterity": 9,
                "constitution": 11,
                "intelligence": 12,
                "wisdom": 8,
                "charisma": 14,
            },
            base_hp=45,
            starting_gold=10,
            equipment_weapons=["Fire Extinguisher"],
            equipment_armor=["ISS Polo Shirt"],
            equipment_items=["Omega Speedmaster Skywalker X-33 Wristwatch", "Family Photo"],
            auto_equip_weapon="Fire Extinguisher",
            auto_equip_armor=["ISS Polo Shirt"],
        ),
        "Russian Systems Operations Officer (Roscosmos)": CharacterClassPreset(
            name="Russian Systems Operations Officer (Roscosmos)",
            description="A burly Russian systems operations officer experience working with their hands on complex mechanical systems",
            character_species="Human",
            stats={
                "strength": 14,
                "dexterity": 8,
                "constitution": 14,
                "intelligence": 9,
                "wisdom": 11,
                "charisma": 8,
            },
            base_hp=50,
            starting_gold=10,
            equipment_weapons=["Wrench"],
            equipment_armor=["ISS Polo Shirt"],
            equipment_items=["Sturmanskie Sputnik Wristwatch", "Family Photo"],
            auto_equip_weapon="Wrench",
            auto_equip_armor=["ISS Polo Shirt"],
        ),
        "European Science Officer (ESA)": CharacterClassPreset(
            name="European Science Officer (ESA)",
            description="A European science officer with a strong background in science and biology, and a knack for solving problems",
            character_species="Human",
            stats={
                "strength": 8,
                "dexterity": 12,
                "constitution": 9,
                "intelligence": 15,
                "wisdom": 12,
                "charisma": 8,
            },
            base_hp=40,
            starting_gold=15,
            equipment_weapons=["Lab Scalpel"],
            equipment_armor=["ISS Polo Shirt"],
            equipment_items=["Omega Speedmaster Skywalker X-33 Wristwatch", "Family Photo"],
            auto_equip_weapon="Lab Scalpel",
            auto_equip_armor=["ISS Polo Shirt"],
        ),
        "Rhesus Macaques (Lab Primates)": CharacterClassPreset(
            name="Rhesus Macaques (Lab Primates)",
            description="A rhesus macaque brought aboard the ISS for scientific research",
            character_species="Rhesus Macaque (Primate)",
            stats={
                "strength": 12,
                "dexterity": 14,
                "constitution": 8,
                "intelligence": 10,
                "wisdom": 6,
                "charisma": 14,
            },
            base_hp=30,
            starting_gold=0,
            equipment_weapons=["Lab Scalpel"],
            equipment_armor=["ISS Polo Shirt"],
            equipment_items=[],
            auto_equip_weapon="Lab Scalpel",
            auto_equip_armor=["ISS Polo Shirt"],
        ),
    },
    # STEP 9: Set the starting location (must match a location name above)
    starting_location_name="U.S. Lab | Destiny Module",
)

# STEP 10: Register your preset so it appears in the game
PresetRegistry.register(ISS_HORROR_PRESET)
