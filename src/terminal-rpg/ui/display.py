"""
Rich terminal output for game UI displays.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from ..storage.models import World, Campaign, Player

console = Console()


def display_welcome() -> None:
    """Display ASCII art welcome message using Rich panels."""
    welcome_art = """
╔════════════════════════════════════════════╗
║                                            ║
║         TERMINAL  RPG  ADVENTURE           ║
║                                            ║
║    ⚔️  Forge Your Legend in Text  ⚔️      ║
║                                            ║
╚════════════════════════════════════════════╝
    """

    console.print(Panel(
        Text(welcome_art, style="bold cyan", justify="center"),
        border_style="bright_magenta",
        padding=(1, 2)
    ))
    console.print()


def display_world_info(world: World) -> None:
    """
    Display world details in a Rich panel.

    Args:
        world: World object to display
    """
    console.print()
    console.print(Panel(
        world.description,
        title=f"[bold yellow]🌍 {world.name}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
    console.print()


def display_class_info(class_name: str, class_data: dict) -> None:
    """
    Display class details including stats and equipment.

    Args:
        class_name: Name of the class
        class_data: Class preset dictionary
    """
    console.print()

    # Class description
    console.print(Panel(
        class_data['description'],
        title=f"[bold cyan]{class_name}[/bold cyan] ({class_data['character_race']})",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Stats table
    stats_table = Table(title="Ability Scores", show_header=True, header_style="bold magenta")
    stats_table.add_column("Attribute", style="cyan", width=15)
    stats_table.add_column("Score", justify="center", style="green", width=10)

    stats = class_data['stats']
    stats_table.add_row("Strength", str(stats['strength']))
    stats_table.add_row("Dexterity", str(stats['dexterity']))
    stats_table.add_row("Constitution", str(stats['constitution']))
    stats_table.add_row("Intelligence", str(stats['intelligence']))
    stats_table.add_row("Wisdom", str(stats['wisdom']))
    stats_table.add_row("Charisma", str(stats['charisma']))

    console.print(stats_table)
    console.print()

    # HP and Gold
    constitution = stats['constitution']
    max_hp = class_data['base_hp'] + (constitution * 2)
    console.print(f"[bold green]HP:[/bold green] {max_hp}  |  [bold yellow]Gold:[/bold yellow] {class_data['starting_gold']}")
    console.print()

    # Equipment
    console.print("[bold cyan]Starting Equipment:[/bold cyan]")
    console.print(f"  [yellow]⚔️  Weapons:[/yellow] {', '.join(class_data['equipment']['weapons'])}")
    console.print(f"  [blue]🛡️  Armor:[/blue] {', '.join(class_data['equipment']['armor'])}")
    console.print(f"  [magenta]🎒 Items:[/magenta] {', '.join(class_data['equipment']['items'])}")
    console.print()


def display_game_start_summary(
    campaign: Campaign,
    player: Player,
    world: World
) -> None:
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
    console.print(Panel(
        f"[bold white]{player.name}[/bold white]\n"
        f"[cyan]{player.character_class}[/cyan] ({player.character_race})\n"
        f"Level {player.level}",
        title="[bold green]✨ Character Created ✨[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))

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
    console.print(Panel(
        "[bold white]Your adventure begins now...[/bold white]\n\n"
        "[italic]Press Ctrl+C to exit at any time[/italic]",
        border_style="bright_magenta",
        padding=(1, 2)
    ))
    console.print()
    console.print("=" * 70, style="bold green")
    console.print()
