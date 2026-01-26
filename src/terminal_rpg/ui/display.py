"""
Rich terminal output for game UI displays.
"""

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from ..storage.models import World, Campaign, Player
from ..campaign_presets import CampaignPreset, CharacterClassPreset

console = Console()


def display_welcome() -> None:
    """Display ASCII art welcome message using Rich panels."""
    welcome_art = """
╔════════════════════════════════════════════╗
║                                            ║
║         TERMINAL  RPG  ADVENTURE           ║
║                                            ║
║          by Harry Dubke | 2026             ║
║                                            ║
╚════════════════════════════════════════════╝
    """

    console.print(Panel(
        Text(welcome_art, style="bold cyan", justify="center"),
        border_style="bright_magenta",
        padding=(1, 2)
    ))
    console.print()


def display_preset_info(preset: CampaignPreset) -> None:
    """
    Display campaign preset details including world and available classes.

    Args:
        preset: CampaignPreset to display
    """
    console.print()
    console.print(Panel(
        preset.world.description,
        title=f"[bold yellow]🌍 {preset.display_name}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))

    console.print(f"\n[bold cyan]Available Classes:[/bold cyan]")
    for class_name in preset.character_classes.keys():
        console.print(f"  • {class_name}")
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


def display_class_info_from_preset(class_name: str, class_preset: CharacterClassPreset) -> None:
    """
    Display class details from a CharacterClassPreset including stats and equipment.

    Args:
        class_name: Name of the class
        class_preset: CharacterClassPreset dataclass
    """
    console.print()

    # Class description
    console.print(Panel(
        class_preset.description,
        title=f"[bold cyan]{class_name}[/bold cyan] ({class_preset.character_race})",
        border_style="cyan",
        padding=(1, 2)
    ))

    # Stats table
    stats_table = Table(title="Ability Scores", show_header=True, header_style="bold magenta")
    stats_table.add_column("Attribute", style="cyan", width=15)
    stats_table.add_column("Score", justify="center", style="green", width=10)

    stats_table.add_row("Strength", str(class_preset.stats['strength']))
    stats_table.add_row("Dexterity", str(class_preset.stats['dexterity']))
    stats_table.add_row("Constitution", str(class_preset.stats['constitution']))
    stats_table.add_row("Intelligence", str(class_preset.stats['intelligence']))
    stats_table.add_row("Wisdom", str(class_preset.stats['wisdom']))
    stats_table.add_row("Charisma", str(class_preset.stats['charisma']))

    console.print(stats_table)
    console.print()

    # HP and Gold
    constitution = class_preset.stats['constitution']
    max_hp = class_preset.base_hp + (constitution * 2)
    console.print(f"[bold green]HP:[/bold green] {max_hp}  |  [bold yellow]Gold:[/bold yellow] {class_preset.starting_gold}")
    console.print()

    # Equipment
    console.print("[bold cyan]Starting Equipment:[/bold cyan]")
    console.print(f"  [yellow]⚔️  Weapons:[/yellow] {', '.join(class_preset.equipment_weapons)}")
    console.print(f"  [blue]🛡️  Armor:[/blue] {', '.join(class_preset.equipment_armor)}")
    console.print(f"  [magenta]🎒 Items:[/magenta] {', '.join(class_preset.equipment_items)}")
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
    from ..storage.models import GameState
    
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
            content_lines.append(f"    Attack: {weapon.attack} | Type: {weapon.type} | Hands: {weapon.hands_required}")
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
            content_lines.append(f"    Defense: {armor.defense} | Type: {armor.type}")
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
