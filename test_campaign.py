"""
Test script to verify campaign creation logic without interactive prompts.
"""

import sys
import os

# Add the terminal_rpg directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'src', 'terminal_rpg'))

from storage.database import Database
from engines.new_campaign import (
    get_available_worlds,
    create_character_class_presets,
    create_new_campaign
)

def test_campaign_creation():
    """Test creating a campaign with a Fighter character"""
    db_path = "src/games.db"

    with Database(db_path) as db:
        # 1. Get worlds
        worlds = get_available_worlds(db)
        print(f"✓ Found {len(worlds)} worlds")
        print(f"  World: {worlds[0].name}")

        # 2. Get class presets
        classes = create_character_class_presets()
        print(f"✓ Found {len(classes)} classes: {', '.join(classes.keys())}")

        # 3. Create a test campaign with Fighter
        fighter_preset = classes["Fighter"]
        print(f"\n✓ Testing campaign creation with Fighter...")
        print(f"  Race: {fighter_preset['character_race']}")
        print(f"  Stats: STR {fighter_preset['stats']['strength']}, CON {fighter_preset['stats']['constitution']}")
        print(f"  Equipment: {len(fighter_preset['equipment']['weapons'])} weapons, {len(fighter_preset['equipment']['armor'])} armor pieces")

        campaign, player = create_new_campaign(
            db,
            world_id=worlds[0].id,
            campaign_name="Test Campaign - Fighter",
            player_name="Thorin",
            player_description="A mighty warrior from the northern mountains",
            class_preset=fighter_preset
        )

        print(f"\n✓ Campaign created successfully!")
        print(f"  Campaign ID: {campaign.id}")
        print(f"  Campaign Name: {campaign.name}")
        print(f"  Player ID: {player.id}")
        print(f"  Player Name: {player.name}")
        print(f"  Player Class: {player.character_class}")
        print(f"  Player Race: {player.character_race}")
        print(f"  HP: {player.hp}/{player.max_hp}")
        print(f"  Gold: {player.gold}")
        print(f"  Strength: {player.strength}")

        # 4. Verify inventory
        from storage.repositories import PlayerRepository
        player_repo = PlayerRepository(db)

        equipped_weapons = player_repo.get_equipped_weapons(player.id)
        equipped_armor = player_repo.get_equipped_armor(player.id)
        inventory_items = player_repo.get_inventory_items(player.id)

        print(f"\n✓ Inventory verification:")
        print(f"  Equipped weapons: {len(equipped_weapons)}")
        for weapon in equipped_weapons:
            print(f"    - {weapon.name} (Attack: {weapon.attack})")

        print(f"  Equipped armor: {len(equipped_armor)}")
        for armor in equipped_armor:
            print(f"    - {armor.name} (Defense: {armor.defense})")

        print(f"  Items: {len(inventory_items)}")
        for item, qty in inventory_items:
            print(f"    - {item.name} (x{qty})")

        print(f"\n✅ All tests passed!")

if __name__ == "__main__":
    test_campaign_creation()
