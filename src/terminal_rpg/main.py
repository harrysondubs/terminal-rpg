"""
Terminal RPG - Entry Point
Main game entry point that handles database initialization and menu flow.
"""

import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging (DEBUG level to file only, don't spam console)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("terminal_rpg_debug.log")],
)

# ruff: noqa: E402
from .engines.game import GameEngine
from .engines.new_campaign import create_new_campaign_from_preset, get_available_presets
from .storage.database import Database
from .storage.models import Campaign, Player
from .storage.repositories import CampaignRepository, WorldRepository
from .ui.menu_display import (
    console,
    display_class_info_from_preset,
    display_game_start_summary,
    display_leaderboard,
    display_location_summary,
    display_preset_info,
    display_recent_messages,
    display_welcome,
)
from .ui.prompts import (
    confirm_character_creation_with_nav,
    get_campaign_name_with_nav,
    get_character_description_with_nav,
    get_character_name_with_nav,
    select_class_from_preset_with_nav,
    select_preset_with_nav,
    select_saved_campaign,
    show_start_menu,
)


def main():
    """
    Terminal RPG entry point.
    Handles database initialization and game menu flow.
    """
    try:
        # Database path
        db_path = "games.db"

        # Initialize database schema if it doesn't exist
        if not os.path.exists(db_path):
            console.print("[yellow]Database not found. Initializing...[/yellow]")
            with Database(db_path) as db:
                db.create_schema()
            console.print("[green]Database initialized successfully![/green]\n")

        # Display welcome screen
        display_welcome()

        # Main menu loop
        while True:
            choice = show_start_menu()

            if choice == "exit":
                console.print(
                    "\n[cyan]Farewell, adventurer! May your next journey be legendary.[/cyan]\n"
                )
                break

            elif choice == "new_game":
                with Database(db_path) as db:
                    campaign, player = run_new_game_flow(db)
                    if campaign and player:
                        # Successfully created campaign
                        console.print("[green]Ready to begin your adventure![/green]\n")

                        # Launch game engine
                        game_engine = GameEngine(db, campaign.id)
                        game_engine.run()

                        # After game ends, return to menu
                        console.print("\n[yellow]Returning to main menu...[/yellow]\n")
                        continue

            elif choice == "load_game":
                with Database(db_path) as db:
                    campaign = run_load_game_flow(db)
                    if campaign:
                        # Successfully loaded campaign
                        console.print("[green]Ready to continue your adventure![/green]\n")

                        # Launch game engine
                        game_engine = GameEngine(db, campaign.id)
                        game_engine.run()

                        # After game ends, return to menu
                        console.print("\n[yellow]Returning to main menu...[/yellow]\n")
                        continue

            elif choice == "leaderboard":
                with Database(db_path) as db:
                    run_leaderboard_flow(db)
                    # Return to main menu after viewing leaderboard
                    continue

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Game interrupted. Goodbye![/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]\n")
        raise


def run_new_game_flow(db: Database) -> tuple[Campaign, Player] | tuple[None, None]:
    """
    Execute the new game creation flow with preset system.
    Supports navigation: users can go back to previous steps or cancel.

    Args:
        db: Connected Database instance

    Returns:
        Tuple of (Campaign, Player) if successful, (None, None) if cancelled
    """
    console.print()
    presets = get_available_presets()

    if not presets:
        console.print("[red]No campaign presets available![/red]\n")
        return None, None

    # State variables to store selections
    selected_preset = None
    class_name = None
    class_preset = None
    player_name = None
    campaign_name = None
    player_description = None

    # State machine: step numbers allow forward and backward navigation
    current_step = 1

    while True:
        # Step 1: Preset Selection
        if current_step == 1:
            result = select_preset_with_nav(presets)

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None

            selected_preset = result
            display_preset_info(selected_preset)
            current_step = 2

        # Step 2: Class Selection
        elif current_step == 2:
            result = select_class_from_preset_with_nav(selected_preset)

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None
            elif result == "back":
                current_step = 1
                continue

            class_name, class_preset = result
            display_class_info_from_preset(class_name, class_preset)
            current_step = 3

        # Step 3: Character Name
        elif current_step == 3:
            result = get_character_name_with_nav()

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None
            elif result == "back":
                current_step = 2
                continue

            player_name = result
            current_step = 4

        # Step 4: Campaign Name
        elif current_step == 4:
            result = get_campaign_name_with_nav()

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None
            elif result == "back":
                current_step = 3
                continue

            campaign_name = result
            current_step = 5

        # Step 5: Character Description
        elif current_step == 5:
            result = get_character_description_with_nav()

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None
            elif result == "back":
                current_step = 4
                continue

            player_description = result
            current_step = 6

        # Step 6: Confirmation
        elif current_step == 6:
            result = confirm_character_creation_with_nav(campaign_name, player_name, class_name)

            if result == "cancel":
                console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
                return None, None
            elif result == "back":
                current_step = 5
                continue
            elif result == "confirm":
                # Proceed to creation
                break

    # Create Campaign from Preset
    try:
        with console.status("[bold green]Creating your adventure...", spinner="dots"):
            campaign, player = create_new_campaign_from_preset(
                db, selected_preset, campaign_name, player_name, player_description, class_preset
            )

        console.print("[green]Campaign created successfully![/green]\n")

        # Get world for display
        world_repo = WorldRepository(db)
        world = world_repo.get_by_id(campaign.world_id)

        display_game_start_summary(campaign, player, world)

        return campaign, player

    except ValueError as e:
        console.print(f"[red]Failed to create campaign: {e}[/red]\n")
        return None, None
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]\n")
        return None, None


def run_load_game_flow(db: Database) -> Campaign | None:
    """
    Execute the load game flow.

    Args:
        db: Connected Database instance

    Returns:
        Selected Campaign if successful, None if cancelled or no saves
    """
    from .llm.game.message_history import get_recent_messages_for_display

    # 1. Get all campaigns with world names
    campaign_repo = CampaignRepository(db)
    campaigns_with_worlds = campaign_repo.get_all_active_with_world_names()

    # 2. Handle empty database
    if not campaigns_with_worlds:
        console.print("[yellow]No saved games found.[/yellow]\n")
        return None

    # 3. Show selection menu
    selected_campaign = select_saved_campaign(campaigns_with_worlds)

    # 4. Handle cancellation
    if not selected_campaign:
        console.print("[yellow]Load game cancelled.[/yellow]\n")
        return None

    # 5. Load full game state
    game_state = campaign_repo.load_game_state(selected_campaign.id)

    if not game_state:
        console.print("[red]Error: Could not load game state.[/red]\n")
        return None

    # 6. Display location summary
    console.print()
    display_location_summary(game_state.location, game_state.world.name, game_state.player.name)

    # 7. Get and display recent messages for context
    recent_messages = get_recent_messages_for_display(
        selected_campaign.id,
        db,
        limit=6,  # Last 6 messages (3 exchanges)
    )

    if recent_messages:
        display_recent_messages(recent_messages, max_messages=3)

    console.print("[green]Game loaded successfully![/green]\n")

    return selected_campaign


def run_leaderboard_flow(db: Database) -> None:
    """
    Display the campaign leaderboard showing top players by XP.

    Args:
        db: Connected Database instance
    """
    campaign_repo = CampaignRepository(db)
    leaderboard_data = campaign_repo.get_leaderboard(limit=10)

    display_leaderboard(leaderboard_data)

    # Wait for user to press Enter
    input()


if __name__ == "__main__":
    main()
