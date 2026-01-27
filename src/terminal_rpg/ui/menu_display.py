"""
Menu and campaign creation display functions.
UI displays for main menu, campaign setup, and game loading screens.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..campaign_presets import CampaignPreset, CharacterClassPreset
from ..storage.models import Campaign, Player, World

console = Console()


def display_welcome() -> None:
    """Display ASCII art welcome message using Rich panels."""
    welcome_art = """
╔════════════════════════════════════════════╗
║                                            ║
║         TERMINAL  RPG  ADVENTURE           ║
║                                            ║
║            HARRY DUBKE | 2026              ║
║                                            ║
╚════════════════════════════════════════════╝
    """

    console.print(
        Panel(
            Text(welcome_art, style="bold cyan", justify="center"),
            border_style="bright_magenta",
            padding=(1, 2),
        )
    )
    console.print()


def display_preset_info(preset: CampaignPreset) -> None:
    """
    Display campaign preset details including world and available classes.

    Args:
        preset: CampaignPreset to display
    """
    console.print()
    console.print(
        Panel(
            preset.world.description,
            title=f"[bold yellow]🌍 {preset.display_name}[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    console.print("\n[bold cyan]Available Classes:[/bold cyan]")
    for class_name in preset.character_classes:
        console.print(f"  • {class_name}")
    console.print()


def display_world_info(world: World) -> None:
    """
    Display world details in a Rich panel.

    Args:
        world: World object to display
    """
    console.print()
    console.print(
        Panel(
            world.description,
            title=f"[bold yellow]🌍 {world.name}[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    console.print()


def display_class_info_from_preset(class_name: str, class_preset: CharacterClassPreset) -> None:
    """
    Display class details from a CharacterClassPreset including stats and equipment.

    Args:
        class_name: Name of the class
        class_preset: CharacterClassPreset dataclass
    """
    console.print()

    # Class description
    console.print(
        Panel(
            class_preset.description,
            title=f"[bold cyan]{class_name}[/bold cyan] ({class_preset.character_species})",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # Stats table
    stats_table = Table(title="Ability Scores", show_header=True, header_style="bold magenta")
    stats_table.add_column("Attribute", style="cyan", width=15)
    stats_table.add_column("Score", justify="center", style="green", width=10)

    stats_table.add_row("Strength", str(class_preset.stats["strength"]))
    stats_table.add_row("Dexterity", str(class_preset.stats["dexterity"]))
    stats_table.add_row("Constitution", str(class_preset.stats["constitution"]))
    stats_table.add_row("Intelligence", str(class_preset.stats["intelligence"]))
    stats_table.add_row("Wisdom", str(class_preset.stats["wisdom"]))
    stats_table.add_row("Charisma", str(class_preset.stats["charisma"]))

    console.print(stats_table)
    console.print()

    # HP and Gold
    constitution = class_preset.stats["constitution"]
    max_hp = class_preset.base_hp + (constitution * 2)
    console.print(
        f"[bold green]HP:[/bold green] {max_hp}  |  [bold yellow]Gold:[/bold yellow] {class_preset.starting_gold}"
    )
    console.print()

    # Equipment
    console.print("[bold cyan]Starting Equipment:[/bold cyan]")
    console.print(f"  [yellow]⚔️  Weapons:[/yellow] {', '.join(class_preset.equipment_weapons)}")
    console.print(f"  [blue]🛡️  Armor:[/blue] {', '.join(class_preset.equipment_armor)}")
    console.print(f"  [magenta]🎒 Items:[/magenta] {', '.join(class_preset.equipment_items)}")
    console.print()


def display_game_start_summary(campaign: Campaign, player: Player, world: World) -> None:
    """
    Display final summary before starting game.
    Shows character sheet and equipment.

    Args:
        campaign: Created campaign
        player: Created player
        world: Selected world
    """
    console.print()
    console.print("=" * 70, style="bold green")
    console.print()

    # Character sheet header
    console.print(
        Panel(
            f"[bold white]{player.name}[/bold white]\n"
            f"[cyan]{player.character_class}[/cyan] ({player.character_species})\n"
            f"Level {player.level}",
            title="[bold green]✨ Character Created ✨[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Campaign info
    console.print(f"\n[bold yellow]Campaign:[/bold yellow] {campaign.name}")
    console.print(f"[bold yellow]World:[/bold yellow] {world.name}")
    console.print()

    # Stats table
    stats_table = Table(title="Character Stats", show_header=True, header_style="bold cyan")
    stats_table.add_column("Attribute", style="cyan", width=15)
    stats_table.add_column("Value", justify="center", style="white", width=10)

    stats_table.add_row("HP", f"{player.hp}/{player.max_hp}")
    stats_table.add_row("Gold", str(player.gold))
    stats_table.add_row("XP", str(player.xp))
    stats_table.add_row("", "")
    stats_table.add_row("Strength", str(player.strength))
    stats_table.add_row("Dexterity", str(player.dexterity))
    stats_table.add_row("Constitution", str(player.constitution))
    stats_table.add_row("Intelligence", str(player.intelligence))
    stats_table.add_row("Wisdom", str(player.wisdom))
    stats_table.add_row("Charisma", str(player.charisma))

    console.print(stats_table)
    console.print()

    # Adventure message
    console.print(
        Panel(
            "[bold white]Your adventure begins now...[/bold white]\n\n"
            "[italic]Press Ctrl+C to exit at any time[/italic]",
            border_style="bright_magenta",
            padding=(1, 2),
        )
    )
    console.print()
    console.print("=" * 70, style="bold green")
    console.print()


def display_location_summary(location, world_name: str, player_name: str) -> None:
    """
    Display current location summary for loaded game.

    Args:
        location: Location object
        world_name: Name of the world
        player_name: Player's character name
    """
    welcome = f"""[bold cyan]Welcome back, {player_name}[/bold cyan]

[bold]Current Location:[/bold] {location.name}
{location.description}

[dim]Type your actions or questions. Type '/quit' to exit.
Quick commands: /inventory, /stats[/dim]"""

    console.print(Panel(welcome, title=f"{world_name}", border_style="cyan"))


def display_recent_messages(messages: list[str], max_messages: int = 3) -> None:
    """
    Display recent conversation history from loaded game.

    Args:
        messages: List of recent messages (user and assistant)
        max_messages: Maximum number of messages to display
    """
    if not messages:
        return

    console.print()
    console.print("[bold yellow]Recent Conversation:[/bold yellow]")
    console.print()

    for msg in messages[-max_messages:]:
        console.print(Panel(msg, border_style="dim", padding=(0, 2)))

    console.print()


def display_leaderboard(leaderboard_data: list[tuple[str, str, int, int, bool]]) -> None:
    """
    Display leaderboard table with top campaigns by XP.

    Args:
        leaderboard_data: List of tuples (campaign_name, player_name, level, xp, is_alive)
    """
    console.print()
    console.print(
        Panel(
            "[bold white]🏆 TOP ADVENTURERS 🏆[/bold white]",
            border_style="bright_yellow",
            padding=(1, 2),
        )
    )
    console.print()

    if not leaderboard_data:
        console.print("[yellow]No campaigns found yet. Start your adventure![/yellow]\n")
        return

    # Create leaderboard table
    table = Table(
        title="Campaign Leaderboard",
        show_header=True,
        header_style="bold bright_yellow",
        border_style="yellow",
    )

    table.add_column("Rank", justify="center", style="bright_yellow", width=6)
    table.add_column("Campaign", style="cyan", width=20)
    table.add_column("Player", style="white", width=20)
    table.add_column("Level", justify="center", style="magenta", width=7)
    table.add_column("XP", justify="right", style="green", width=10)
    table.add_column("Status", justify="center", style="white", width=10)

    for rank, (campaign_name, player_name, level, xp, is_alive) in enumerate(leaderboard_data, 1):
        status = "✅ Alive" if is_alive else "💀 Dead"
        status_style = "green" if is_alive else "red"

        table.add_row(
            str(rank),
            campaign_name,
            player_name,
            str(level),
            f"{xp:,}",
            f"[{status_style}]{status}[/{status_style}]",
        )

    console.print(table)
    console.print()
    console.print("[dim]Press Enter to return to main menu...[/dim]")
    console.print()
