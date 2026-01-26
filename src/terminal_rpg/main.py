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
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('terminal_rpg_debug.log')
    ]
)

from .storage.database import Database
from .storage.models import Campaign, Player
from .storage.repositories import WorldRepository
from .engines.new_campaign import (
    get_available_presets,
    create_new_campaign_from_preset
)
from .engines.game import GameEngine
from .ui.display import (
    console,
    display_welcome,
    display_preset_info,
    display_class_info_from_preset,
    display_game_start_summary
)
from .ui.prompts import (
    show_start_menu,
    select_preset,
    select_class_from_preset,
    get_campaign_name,
    get_character_name,
    get_character_description,
    confirm_character_creation
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
                console.print("\n[cyan]Farewell, adventurer! May your next journey be legendary.[/cyan]\n")
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
                console.print("\n[yellow]Load game feature not yet implemented.[/yellow]\n")
                continue

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Game interrupted. Goodbye![/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/red]\n")
        raise


def run_new_game_flow(db: Database) -> tuple[Campaign, Player] | tuple[None, None]:
    """
    Execute the new game creation flow with preset system.

    Args:
        db: Connected Database instance

    Returns:
        Tuple of (Campaign, Player) if successful, (None, None) if cancelled
    """
    # 1. Preset Selection
    console.print()
    presets = get_available_presets()

    if not presets:
        console.print("[red]No campaign presets available![/red]\n")
        return None, None

    selected_preset = select_preset(presets)

    if not selected_preset:
        console.print("[yellow]Campaign creation cancelled.[/yellow]\n")
        return None, None

    display_preset_info(selected_preset)

    # 2. Class Selection (from preset)
    class_result = select_class_from_preset(selected_preset)

    if not class_result:
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    class_name, class_preset = class_result
    display_class_info_from_preset(class_name, class_preset)

    # 3. Campaign Naming
    campaign_name = get_campaign_name()

    if not campaign_name:
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    # 4. Character Naming
    player_name = get_character_name()

    if not player_name:
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    # 5. Character Description
    player_description = get_character_description()

    if not player_description:
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    # 6. Confirmation
    if not confirm_character_creation(campaign_name, player_name, class_name):
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    # 7. Create Campaign from Preset
    try:
        with console.status("[bold green]Creating your adventure...", spinner="dots"):
            campaign, player = create_new_campaign_from_preset(
                db,
                selected_preset,
                campaign_name,
                player_name,
                player_description,
                class_preset
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


if __name__ == "__main__":
    main()
