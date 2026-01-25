"""
Database seeding script for RPG game.
Populates the database with an example world, locations, items, and NPCs.
"""

import os
from .database import Database
from .repositories import (
    WorldRepository,
    LocationRepository,
    ItemRepository,
    WeaponRepository,
    ArmorRepository,
    NPCRepository,
)
from .models import (
    World,
    Location,
    Item,
    Weapon,
    Armor,
    NPC,
    Rarity,
    WeaponType,
    HandsRequired,
    ArmorType,
)


def seed_database(db_path="game.db", force=False):
    """
    Populate database with initial game content.

    Args:
        db_path: Path to the SQLite database file
        force: If True, overwrites existing database without prompting
    """
    # Check if database exists
    if os.path.exists(db_path) and not force:
        response = input(f"⚠️  Database '{db_path}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("❌ Seeding cancelled.")
            return
        os.remove(db_path)
    elif force and os.path.exists(db_path):
        os.remove(db_path)

    print(f"🎲 Initializing database: {db_path}")

    with Database(db_path) as db:
        db.create_schema()
        print("✓ Database schema created")

        # Seed data in dependency order
        world = _seed_world(db)
        locations = _seed_locations(db, world.id)
        items = _seed_items(db, world.id)
        weapons = _seed_weapons(db, world.id)
        armor = _seed_armor(db, world.id)
        npcs = _seed_npcs(db, world.id)

        print("\n🎉 Database seeded successfully!")
        print(f"   World: {world.name}")
        print(f"   Locations: {len(locations)}")
        print(f"   Items: {len(items)}")
        print(f"   Weapons: {len(weapons)}")
        print(f"   Armor: {len(armor)}")
        print(f"   NPCs: {len(npcs)}")
        print("\n💡 Ready to start your adventure!")


def _seed_world(db: Database) -> World:
    """Create the example world"""
    world_repo = WorldRepository(db)

    world = world_repo.create(World(
        name="The Forgotten Realms",
        description="A vast fantasy world shrouded in mystery and ancient magic. "
                    "Brave adventurers explore forgotten dungeons, battle fearsome creatures, "
                    "and uncover legendary treasures. Will you become a hero of legend?"
    ))

    print(f"✓ Created world: {world.name}")
    return world


def _seed_locations(db: Database, world_id: int) -> list[Location]:
    """Create starting locations"""
    location_repo = LocationRepository(db)
    locations = []

    # Starting tavern
    locations.append(location_repo.create(Location(
        world_id=world_id,
        name="The Prancing Pony Inn",
        description="A warm and welcoming tavern with a crackling fireplace. "
                    "The smell of roasted meat and fresh bread fills the air. "
                    "Adventurers gather here to share tales, find companions, and hear rumors of treasure. "
                    "The innkeeper, a jovial halfling named Baldo, greets you with a wide smile."
    )))

    # Nearby forest
    locations.append(location_repo.create(Location(
        world_id=world_id,
        name="Whispering Woods",
        description="Ancient trees tower above you, their leaves rustling with secrets. "
                    "Dappled sunlight filters through the canopy, illuminating a winding path. "
                    "You hear the distant calls of birds and the occasional snap of a twig. "
                    "This forest is known to harbor both friendly creatures and lurking dangers."
    )))

    # Dangerous dungeon
    locations.append(location_repo.create(Location(
        world_id=world_id,
        name="Ruins of Shadowkeep",
        description="The crumbling remains of an ancient fortress loom before you. "
                    "Dark stone walls are covered in creeping vines and mysterious runes. "
                    "A sense of foreboding hangs in the air. Local legends speak of untold riches "
                    "hidden within, guarded by creatures that should have died long ago."
    )))

    # Mystical location
    locations.append(location_repo.create(Location(
        world_id=world_id,
        name="Crystal Caverns",
        description="Luminescent crystals jut from the cavern walls, casting an ethereal blue glow. "
                    "The sound of dripping water echoes through the chambers. "
                    "These caves are said to be touched by ancient magic, and those who enter "
                    "sometimes emerge changed, for better or worse."
    )))

    # Town
    locations.append(location_repo.create(Location(
        world_id=world_id,
        name="Millhaven Village",
        description="A quaint village nestled in a peaceful valley. "
                    "Farmers tend their fields, blacksmiths hammer at their forges, "
                    "and children play in the town square. The villagers are friendly but cautious, "
                    "having learned to be wary of strangers after recent goblin raids."
    )))

    print(f"✓ Created {len(locations)} locations")
    return locations


def _seed_items(db: Database, world_id: int) -> list[Item]:
    """Create consumable items"""
    item_repo = ItemRepository(db)
    items = []

    # Healing items
    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Minor Health Potion",
        description="A small vial of crimson liquid. Restores 25 HP when consumed.",
        rarity=Rarity.COMMON,
        value=15
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Health Potion",
        description="A flask of glowing red liquid. Restores 50 HP when consumed.",
        rarity=Rarity.COMMON,
        value=35
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Greater Health Potion",
        description="A large bottle of shimmering ruby liquid. Restores 100 HP when consumed.",
        rarity=Rarity.RARE,
        value=75
    )))

    # Utility items
    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Torch",
        description="A simple wooden torch wrapped in oil-soaked cloth. Lights the way in darkness.",
        rarity=Rarity.COMMON,
        value=5
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Rope (50 ft)",
        description="Sturdy hempen rope. Useful for climbing, binding, or making traps.",
        rarity=Rarity.COMMON,
        value=10
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Lockpicks",
        description="A set of fine metal tools for picking locks. Requires a steady hand.",
        rarity=Rarity.COMMON,
        value=25
    )))

    # Magical items
    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Scroll of Fireball",
        description="An ancient parchment inscribed with arcane runes. "
                    "Reading it unleashes a devastating ball of fire.",
        rarity=Rarity.RARE,
        value=100
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Crystal of Recall",
        description="A small, perfectly smooth crystal that glows faintly. "
                    "Crushing it teleports you to the last safe location you visited.",
        rarity=Rarity.RARE,
        value=150
    )))

    items.append(item_repo.create(Item(
        world_id=world_id,
        name="Elixir of Strength",
        description="A thick, golden liquid that tastes of honey and lightning. "
                    "Temporarily increases your strength dramatically.",
        rarity=Rarity.LEGENDARY,
        value=250
    )))

    print(f"✓ Created {len(items)} items")
    return items


def _seed_weapons(db: Database, world_id: int) -> list[Weapon]:
    """Create weapons of various types"""
    weapon_repo = WeaponRepository(db)
    weapons = []

    # Common melee weapons
    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Rusty Dagger",
        description="A small, worn blade. Better than nothing, barely.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.ONE_HANDED,
        attack=5,
        rarity=Rarity.COMMON,
        value=10
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Iron Sword",
        description="A well-balanced blade of solid iron. A reliable weapon for any warrior.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.ONE_HANDED,
        attack=12,
        rarity=Rarity.COMMON,
        value=50
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Battle Axe",
        description="A heavy, double-bladed axe. Requires two hands but deals devastating damage.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.TWO_HANDED,
        attack=18,
        rarity=Rarity.COMMON,
        value=75
    )))

    # Common ranged weapons
    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Wooden Bow",
        description="A simple bow carved from flexible oak. Good for hunting and combat.",
        type=WeaponType.RANGED,
        hands_required=HandsRequired.TWO_HANDED,
        attack=10,
        rarity=Rarity.COMMON,
        value=40
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Crossbow",
        description="A mechanical bow that fires heavy bolts with great force and accuracy.",
        type=WeaponType.RANGED,
        hands_required=HandsRequired.TWO_HANDED,
        attack=14,
        rarity=Rarity.COMMON,
        value=80
    )))

    # Rare weapons
    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Elven Longsword",
        description="A masterwork blade forged by elven smiths. "
                    "Light as a feather yet sharp enough to cut through steel.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.ONE_HANDED,
        attack=20,
        rarity=Rarity.RARE,
        value=200
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Warhammer of Thunder",
        description="A massive hammer crackling with electrical energy. "
                    "Each strike echoes with the sound of thunder.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.TWO_HANDED,
        attack=25,
        rarity=Rarity.RARE,
        value=300
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Enchanted Longbow",
        description="A bow made from ancient yew and strung with silver thread. "
                    "Arrows fired from it never miss their mark.",
        type=WeaponType.RANGED,
        hands_required=HandsRequired.TWO_HANDED,
        attack=22,
        rarity=Rarity.RARE,
        value=250
    )))

    # Legendary weapons
    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Dragonbane",
        description="A legendary greatsword forged from dragon scales and blessed by ancient magic. "
                    "It glows with an inner fire and is said to have slain a dozen dragons.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.TWO_HANDED,
        attack=35,
        rarity=Rarity.LEGENDARY,
        value=1000
    )))

    weapons.append(weapon_repo.create(Weapon(
        world_id=world_id,
        name="Shadowstrike Daggers",
        description="A pair of midnight-black daggers that seem to drink in light. "
                    "Whispered to have been wielded by the Assassin King himself.",
        type=WeaponType.MELEE,
        hands_required=HandsRequired.ONE_HANDED,
        attack=28,
        rarity=Rarity.LEGENDARY,
        value=800
    )))

    print(f"✓ Created {len(weapons)} weapons")
    return weapons


def _seed_armor(db: Database, world_id: int) -> list[Armor]:
    """Create armor pieces for all slots"""
    armor_repo = ArmorRepository(db)
    armor_pieces = []

    # Common armor - Leather set
    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Leather Cap",
        description="A simple leather helmet. Provides minimal protection.",
        type=ArmorType.HELMET,
        defense=2,
        rarity=Rarity.COMMON,
        value=15
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Leather Armor",
        description="Sturdy leather armor, hardened and treated. Light and flexible.",
        type=ArmorType.CHESTPLATE,
        defense=5,
        rarity=Rarity.COMMON,
        value=40
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Leather Boots",
        description="Well-worn leather boots. Comfortable for long journeys.",
        type=ArmorType.BOOTS,
        defense=2,
        rarity=Rarity.COMMON,
        value=15
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Leather Leggings",
        description="Reinforced leather leg protection.",
        type=ArmorType.LEGGINGS,
        defense=3,
        rarity=Rarity.COMMON,
        value=25
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Wooden Shield",
        description="A round shield made of oak planks. Simple but effective.",
        type=ArmorType.SHIELD,
        defense=4,
        rarity=Rarity.COMMON,
        value=20
    )))

    # Rare armor - Iron/Steel set
    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Steel Helmet",
        description="A polished steel helm with a protective visor.",
        type=ArmorType.HELMET,
        defense=8,
        rarity=Rarity.RARE,
        value=100
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Steel Plate Armor",
        description="Heavy steel plate armor. Offers excellent protection but restricts movement.",
        type=ArmorType.CHESTPLATE,
        defense=15,
        rarity=Rarity.RARE,
        value=250
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Steel Boots",
        description="Heavy boots plated with steel. Your footsteps echo with authority.",
        type=ArmorType.BOOTS,
        defense=6,
        rarity=Rarity.RARE,
        value=80
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Steel Greaves",
        description="Articulated steel leg armor that protects without sacrificing mobility.",
        type=ArmorType.LEGGINGS,
        defense=10,
        rarity=Rarity.RARE,
        value=150
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Kite Shield",
        description="A large steel shield with your family crest emblazoned on it.",
        type=ArmorType.SHIELD,
        defense=12,
        rarity=Rarity.RARE,
        value=200
    )))

    # Legendary armor
    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Crown of the Ancient King",
        description="A golden crown set with precious gems. Radiates an aura of power and majesty. "
                    "Wearing it grants the wisdom of ancient rulers.",
        type=ArmorType.HELMET,
        defense=15,
        rarity=Rarity.LEGENDARY,
        value=500
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Dragon Scale Mail",
        description="Armor crafted from the scales of a red dragon. "
                    "Nearly impenetrable and grants immunity to fire.",
        type=ArmorType.CHESTPLATE,
        defense=25,
        rarity=Rarity.LEGENDARY,
        value=1500
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Boots of Swiftness",
        description="Enchanted boots that make you feel light as air. "
                    "Your movement speed is doubled while wearing these.",
        type=ArmorType.BOOTS,
        defense=10,
        rarity=Rarity.LEGENDARY,
        value=600
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Leggings of the Mountain",
        description="Heavy armor as unyielding as stone. Nothing can knock you down while wearing these.",
        type=ArmorType.LEGGINGS,
        defense=18,
        rarity=Rarity.LEGENDARY,
        value=800
    )))

    armor_pieces.append(armor_repo.create(Armor(
        world_id=world_id,
        name="Aegis of the Dawn",
        description="A shimmering golden shield that seems to glow with inner light. "
                    "It reflects harmful magic back at attackers.",
        type=ArmorType.SHIELD,
        defense=20,
        rarity=Rarity.LEGENDARY,
        value=1200
    )))

    print(f"✓ Created {len(armor_pieces)} armor pieces")
    return armor_pieces


def _seed_npcs(db: Database, world_id: int) -> list[NPC]:
    """Create NPCs and enemies"""
    npc_repo = NPCRepository(db)
    npcs = []

    # Low-level enemies
    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Goblin Scout",
        character_class="Rogue",
        character_race="Goblin",
        hp=25,
        max_hp=25,
        level=1,
        xp=10,
        gold=5
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Giant Rat",
        character_class="Beast",
        character_race="Rat",
        hp=15,
        max_hp=15,
        level=1,
        xp=5,
        gold=0
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Bandit Thug",
        character_class="Fighter",
        character_race="Human",
        hp=35,
        max_hp=35,
        level=2,
        xp=20,
        gold=15
    )))

    # Mid-level enemies
    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Orc Warrior",
        character_class="Berserker",
        character_race="Orc",
        hp=60,
        max_hp=60,
        level=4,
        xp=50,
        gold=30
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Dark Wizard",
        character_class="Mage",
        character_race="Human",
        hp=45,
        max_hp=45,
        level=5,
        xp=75,
        gold=50
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Forest Troll",
        character_class="Brute",
        character_race="Troll",
        hp=80,
        max_hp=80,
        level=6,
        xp=100,
        gold=40
    )))

    # High-level enemies
    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Vampire Lord",
        character_class="Necromancer",
        character_race="Vampire",
        hp=120,
        max_hp=120,
        level=10,
        xp=250,
        gold=200
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Fire Elemental",
        character_class="Elemental",
        character_race="Fire Spirit",
        hp=100,
        max_hp=100,
        level=9,
        xp=200,
        gold=0
    )))

    # Boss enemies
    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Ancient Red Dragon",
        character_class="Dragon",
        character_race="Dragon",
        hp=300,
        max_hp=300,
        level=20,
        xp=1000,
        gold=5000
    )))

    npcs.append(npc_repo.create(NPC(
        world_id=world_id,
        name="Lich King Malazar",
        character_class="Lich",
        character_race="Undead",
        hp=250,
        max_hp=250,
        level=18,
        xp=800,
        gold=3000
    )))

    print(f"✓ Created {len(npcs)} NPCs")
    return npcs


if __name__ == "__main__":
    """Run seeding when executed directly"""
    import sys

    # Check for force flag
    force = "--force" in sys.argv or "-f" in sys.argv

    # Check for custom db path
    db_path = "game.db"
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            db_path = arg
            break

    seed_database(db_path=db_path, force=force)
