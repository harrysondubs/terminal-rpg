"""
Terminal RPG - Entry Point
Main game entry point that handles database initialization and menu flow.
"""

import os
from .storage.database import Database
from .storage.seed import seed_database
from .storage.models import Campaign, Player
from .engines.new_campaign import (
    get_available_worlds,
    create_character_class_presets,
    create_new_campaign
)
from .ui.display import (
    console,
    display_welcome,
    display_world_info,
    display_class_info,
    display_game_start_summary
)
from .ui.prompts import (
    show_start_menu,
    select_world,
    select_class,
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
        db_path = "game.db"

        # Initialize database if it doesn't exist
        if not os.path.exists(db_path):
            console.print("[yellow]Database not found. Initializing...[/yellow]")
            seed_database(db_path, force=True)
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
                        console.print("[green]Ready to begin your adventure![/green]")
                        # TODO: Launch game engine here
                        console.print("[yellow]Game engine not yet implemented. Returning to main menu.[/yellow]\n")
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
    Execute the new game creation flow.

    Args:
        db: Connected Database instance

    Returns:
        Tuple of (Campaign, Player) if successful, (None, None) if cancelled
    """
    # 1. World Selection
    console.print()
    worlds = get_available_worlds(db)

    if not worlds:
        console.print("[red]No worlds available! Please seed the database.[/red]\n")
        return None, None

    selected_world = select_world(worlds)

    if not selected_world:
        console.print("[yellow]World creation not yet implemented.[/yellow]\n")
        return None, None

    display_world_info(selected_world)

    # 2. Class Selection
    classes = create_character_class_presets()
    class_result = select_class(classes)

    if not class_result:
        console.print("[yellow]Character creation cancelled.[/yellow]\n")
        return None, None

    class_name, class_data = class_result
    display_class_info(class_name, class_data)

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

    # 7. Create Campaign
    try:
        with console.status("[bold green]Creating your adventure...", spinner="dots"):
            campaign, player = create_new_campaign(
                db,
                selected_world.id,
                campaign_name,
                player_name,
                player_description,
                class_data
            )

        console.print("[green]Campaign created successfully![/green]\n")
        display_game_start_summary(campaign, player, selected_world)

        return campaign, player

    except ValueError as e:
        console.print(f"[red]Failed to create campaign: {e}[/red]\n")
        return None, None
    except Exception as e:
        console.print(f"[red]An unexpected error occurred: {e}[/red]\n")
        return None, None


if __name__ == "__main__":
    main()
