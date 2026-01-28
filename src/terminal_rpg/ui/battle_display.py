"""
Battle-specific UI display functions.
Handles all console I/O for combat encounters.
"""

from rich.console import Console
from rich.panel import Panel

from ..engines.utils import calculate_ability_modifier
from .game_display import animate_dice_roll

console = Console()


def display_battle_start(battle, allies: list, opponents: list) -> None:
    """
    Display the start of a battle encounter with battle info and combatants.

    Args:
        battle: Battle object with name and description
        allies: List of NPC objects that are allies
        opponents: List of NPC objects that are opponents/enemies
    """
    console.print()

    # Build content
    content_lines = []

    # Battle description
    content_lines.append(f"[bold white]{battle.description}[/bold white]")
    content_lines.append("")

    # Allies section (if any)
    if allies:
        content_lines.append("[bold green]⚔️  Allies:[/bold green]")
        for ally in allies:
            content_lines.append(
                f"  [green]• {ally.name} (Lvl {ally.level}) - {ally.character_class}[/green]"
            )
            content_lines.append(f"    [dim]{ally.description}[/dim]")
        content_lines.append("")

    # Opponents section
    content_lines.append("[bold red]⚔️  Opponents:[/bold red]")
    if opponents:
        for opponent in opponents:
            content_lines.append(
                f"  [red]• {opponent.name} (Lvl {opponent.level}) - {opponent.character_class}[/red]"
            )
            content_lines.append(f"    [dim]{opponent.description}[/dim]")
    else:
        content_lines.append("  [dim]None[/dim]")

    # Join and display
    full_content = "\n".join(content_lines)

    console.print(
        Panel(
            full_content,
            title=f"[bold yellow]⚔️  {battle.name}  ⚔️[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )
    console.print()


def display_initiative_header() -> None:
    """Display the initiative rolling header."""
    console.print()
    console.print("[bold yellow]Rolling initiative...[/bold yellow]")
    console.print()


def display_npc_initiative(npc_name: str, initiative_roll: int) -> None:
    """
    Display an NPC's initiative roll.

    Args:
        npc_name: Name of the NPC
        initiative_roll: The NPC's initiative value
    """
    console.print(f"  [cyan]{npc_name}:[/cyan] {initiative_roll}")


def display_player_initiative_prompt(player) -> tuple[int, int]:
    """
    Display initiative prompt for player and handle the roll.

    Args:
        player: Player object with dexterity stat

    Returns:
        Tuple of (roll, total_initiative)
    """
    dex_modifier = calculate_ability_modifier(player.dexterity)
    modifier_str = f"+{dex_modifier}" if dex_modifier >= 0 else str(dex_modifier)

    console.print()
    initiative_prompt = f"""[bold yellow]INITIATIVE ROLL[/bold yellow]

Roll to determine combat turn order!

[bold]Your Dexterity:[/bold] {player.dexterity} (modifier: {modifier_str})

Press Enter to roll the d20..."""

    console.print(Panel(initiative_prompt, border_style="yellow", title="Initiative"))

    # Wait for player input
    input()

    # Roll the dice with animation
    roll = animate_dice_roll(sides=20, label="Rolling Initiative")
    total = roll + dex_modifier

    # Display result
    result_display = f"""[bold]Roll:[/bold] {roll}
[bold]Modifier:[/bold] {modifier_str}
[bold]Initiative:[/bold] {total}"""

    console.print()
    console.print(Panel(result_display, border_style="green", title="Your Initiative"))
    console.print()

    return roll, total


def display_turn_order(participants_with_npcs: list[tuple], player_name: str) -> None:
    """
    Display the final turn order for the battle.

    Args:
        participants_with_npcs: List of tuples (participant, npc_or_none)
        player_name: Name of the player character
    """
    console.print("[bold yellow]Turn Order:[/bold yellow]")
    for idx, (participant, npc) in enumerate(participants_with_npcs, start=1):
        if participant.player_id is not None:
            console.print(
                f"  {idx}. [bold green]{player_name}[/bold green] (Initiative: {participant.initiative_roll})"
            )
        else:
            if npc:
                console.print(
                    f"  {idx}. [cyan]{npc.name}[/cyan] (Initiative: {participant.initiative_roll})"
                )
    console.print()
