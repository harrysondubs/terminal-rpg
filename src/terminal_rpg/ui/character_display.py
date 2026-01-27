"""
Character-related display functions.
Reusable components for displaying character stats, inventory, and equipment.
"""

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..storage.models import Player

console = Console()


def display_player_stats(player: Player) -> None:
    """
    Display player's current stats (HP and ability scores).

    Args:
        player: Player object
    """
    console.print()
    
    # Character header text with Rich markup
    header_text = Text.from_markup(
        f"[bold white]{player.name}[/bold white]\n"
        f"[cyan]{player.character_class}[/cyan] ({player.character_race})\n"
        f"Level {player.level}\n"
    )

    # Stats table
    stats_table = Table(show_header=True, header_style="bold cyan", box=None)
    stats_table.add_column("Attribute", style="cyan", width=15)
    stats_table.add_column("Value", justify="center", style="white", width=10)

    # HP with color coding
    hp_color = "green" if player.hp > player.max_hp * 0.5 else "yellow" if player.hp > player.max_hp * 0.25 else "red"
    stats_table.add_row("HP", f"[{hp_color}]{player.hp}[/{hp_color}]/{player.max_hp}")
    stats_table.add_row("Gold", f"[yellow]{player.gold}[/yellow]")
    stats_table.add_row("XP", str(player.xp))
    stats_table.add_row("", "")
    stats_table.add_row("Strength", str(player.strength))
    stats_table.add_row("Dexterity", str(player.dexterity))
    stats_table.add_row("Constitution", str(player.constitution))
    stats_table.add_row("Intelligence", str(player.intelligence))
    stats_table.add_row("Wisdom", str(player.wisdom))
    stats_table.add_row("Charisma", str(player.charisma))

    # Group everything together
    content = Group(
        header_text,
        stats_table
    )

    # Wrap everything in a single panel
    console.print(Panel(
        content,
        title="[bold cyan]📊 Character Stats[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()


def display_player_inventory(game_state) -> None:
    """
    Display player's complete inventory including gold, items, weapons, and armor.
    Shows which weapons and armor are equipped.

    Args:
        game_state: GameState object containing player and inventory data
    """
    player = game_state.player
    console.print()
    
    # Build the content as a string
    content_lines = []
    
    # Header
    content_lines.append(f"[bold white]{player.name}'s Inventory[/bold white]")
    content_lines.append(f"[yellow]Gold:[/yellow] {player.gold}")
    content_lines.append("")

    # Weapons section
    content_lines.append("[bold cyan]⚔️  Weapons:[/bold cyan]")
    if game_state.inventory_weapons:
        equipped_weapon_ids = {w.id for w in game_state.equipped_weapons}
        
        for weapon, quantity in game_state.inventory_weapons:
            equipped_mark = " [green](equipped)[/green]" if weapon.id in equipped_weapon_ids else ""
            qty_str = f" x{quantity}" if quantity > 1 else ""
            content_lines.append(f"  • [yellow]{weapon.name}[/yellow]{qty_str}{equipped_mark}")
            content_lines.append(f"    {weapon.description}")
            content_lines.append(f"    Attack: {weapon.attack} | Type: {weapon.type.value} | Hands: {weapon.hands_required.value}")
    else:
        content_lines.append("  [dim]None[/dim]")

    content_lines.append("")

    # Armor section
    content_lines.append("[bold cyan]🛡️  Armor:[/bold cyan]")
    if game_state.inventory_armor:
        equipped_armor_ids = {a.id for a in game_state.equipped_armor}
        
        for armor, quantity in game_state.inventory_armor:
            equipped_mark = " [green](equipped)[/green]" if armor.id in equipped_armor_ids else ""
            qty_str = f" x{quantity}" if quantity > 1 else ""
            content_lines.append(f"  • [blue]{armor.name}[/blue]{qty_str}{equipped_mark}")
            content_lines.append(f"    {armor.description}")
            content_lines.append(f"    Defense: {armor.defense} | Type: {armor.type.value}")
    else:
        content_lines.append("  [dim]None[/dim]")

    content_lines.append("")

    # Items section
    content_lines.append("[bold cyan]🎒 Items:[/bold cyan]")
    if game_state.inventory_items:
        for item, quantity in game_state.inventory_items:
            qty_str = f" x{quantity}" if quantity > 1 else ""
            content_lines.append(f"  • [magenta]{item.name}[/magenta]{qty_str}")
            content_lines.append(f"    {item.description}")
            content_lines.append(f"    Value: {item.value} gold")
    else:
        content_lines.append("  [dim]None[/dim]")

    # Join all content and wrap in a single panel
    full_content = "\n".join(content_lines)

    console.print(Panel(
        full_content,
        title="[bold yellow]🎒 Inventory[/bold yellow]",
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
