"""
Game-specific UI display and input handling.
Handles all console I/O for the game loop.
"""

import random
import time

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from ..storage.models import GameState

console = Console()


class GameDisplay:
    """
    Handles all console input/output for the game loop.
    Separates UI concerns from game logic and API calls.
    """

    def __init__(self):
        """Initialize the game display."""
        self.console = console

    def display_welcome(self, game_state: GameState, is_new_game: bool = True) -> None:
        """
        Display welcome message and current location.

        Args:
            game_state: Current game state
            is_new_game: Whether this is a new game (vs loaded game)
        """
        # Skip welcome for loaded games (they already saw recent conversation)
        if not is_new_game:
            return

        player = game_state.player
        location = game_state.location

        welcome = f"""[bold cyan]Welcome, {player.name}[/bold cyan]

[bold]Current Location:[/bold] {location.name}
{location.description}

[dim]Type your actions or questions. Type '/quit' to exit.
Quick commands: /inventory, /stats[/dim]"""

        self.console.print(Panel(welcome, title=f"{game_state.world.name}", border_style="cyan"))

    def get_user_input(self) -> str:
        """
        Get input from user with game prompt.

        Returns:
            User's input string (stripped)
        """
        self.console.print()
        return self.console.input("[bold cyan]>[/bold cyan] ").strip()

    def display_dm_response(self, response_text: str) -> None:
        """
        Display the DM's response in a formatted panel.

        Args:
            response_text: Text response from the DM
        """
        if response_text:
            self.console.print()
            self.console.print(
                Panel(Markdown(response_text), border_style="green", title="Dungeon Master")
            )

    def display_thinking_status(self):
        """
        Return a context manager for showing 'DM is thinking' status.

        Returns:
            Rich status context manager
        """
        return self.console.status("[bold green]The DM is thinking...", spinner="dots")

    def display_farewell(self, player_name: str) -> None:
        """
        Display farewell message when player quits.

        Args:
            player_name: Name of the player character
        """
        self.console.print(f"[cyan]Farewell, {player_name}![/cyan]")

    def display_pause_message(self) -> None:
        """Display message when game is paused (Ctrl+C)."""
        self.console.print(
            "\n[yellow]Game paused. Type '/quit' to exit or press Enter to continue.[/yellow]"
        )

    def display_error(self, error_message: str, is_critical: bool = False) -> None:
        """
        Display an error message.

        Args:
            error_message: The error message to display
            is_critical: Whether this is a critical error that stops execution
        """
        color = "red" if is_critical else "yellow"
        self.console.print(f"[{color}]{error_message}[/{color}]")

    def display_inventory(self, game_state: GameState) -> None:
        """
        Display player's current inventory.

        Args:
            game_state: Current game state
        """
        from .character_display import display_player_inventory

        display_player_inventory(game_state)

    def display_stats(self, game_state: GameState) -> None:
        """
        Display player's current stats.

        Args:
            game_state: Current game state
        """
        from .character_display import display_player_stats

        display_player_stats(game_state.player)

    def display_continue_message(self) -> None:
        """Display message when continuing after an error."""
        self.console.print("[yellow]An error occurred. The game will continue.[/yellow]")

    def display_api_error(self, error_str: str) -> None:
        """
        Display an API-related error message.

        Args:
            error_str: Error string from API
        """
        self.console.print(f"[red]API Error: {error_str}[/red]")

    def display_level_up(self, player, new_level: int) -> str:
        """
        Display level-up prompt and get ability choice from player.

        Args:
            player: Player object with current stats
            new_level: The new level the player has reached

        Returns:
            Chosen ability name (e.g., 'strength', 'dexterity')
        """

        # Display congratulations
        congrats_msg = f"""[bold green]🎉 LEVEL UP! 🎉[/bold green]

Congratulations! You've reached [bold yellow]Level {new_level}[/bold yellow]!

You may increase one ability score by +1."""

        self.console.print()
        self.console.print(Panel(congrats_msg, border_style="green", title="Level Up!"))
        self.console.print()

        # Display current ability scores
        abilities = {
            "strength": player.strength,
            "dexterity": player.dexterity,
            "constitution": player.constitution,
            "intelligence": player.intelligence,
            "wisdom": player.wisdom,
            "charisma": player.charisma,
        }

        ability_display = "[bold]Current Ability Scores:[/bold]\n\n"
        for ability, score in abilities.items():
            from ..engines.utils import calculate_ability_modifier

            modifier = calculate_ability_modifier(score)
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            ability_display += (
                f"  • [cyan]{ability.capitalize()}:[/cyan] {score} (modifier: {modifier_str})\n"
            )

        self.console.print(Panel(ability_display, border_style="cyan"))

        # Loop until valid choice is confirmed
        while True:
            self.console.print()
            self.console.print(
                "[bold yellow]Which ability would you like to increase?[/bold yellow]"
            )
            self.console.print(
                "[dim]Choose from: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma[/dim]"
            )
            self.console.print()

            choice = self.console.input("[bold cyan]>[/bold cyan] ").strip().lower()

            if choice not in abilities:
                self.console.print("[red]Invalid choice. Please choose a valid ability.[/red]")
                continue

            # Show confirmation
            old_value = abilities[choice]
            new_value = old_value + 1

            self.console.print()
            confirm_msg = f"Increase [bold cyan]{choice.capitalize()}[/bold cyan] from [yellow]{old_value}[/yellow] to [green]{new_value}[/green]?"
            self.console.print(confirm_msg)
            self.console.print(
                "[dim](Type 'confirm' to accept, or 'back' to choose a different ability)[/dim]"
            )
            self.console.print()

            confirm = self.console.input("[bold cyan]>[/bold cyan] ").strip().lower()

            if confirm == "confirm":
                return choice
            elif confirm == "back":
                continue
            else:
                self.console.print("[red]Invalid input. Type 'confirm' or 'back'.[/red]")
                continue


def animate_dice_roll(
    sides: int = 20, label: str = "Rolling", predetermined_result: int | None = None
) -> int:
    """
    Display an animated dice roll that starts fast and slows down.

    Creates suspense by showing random numbers rapidly at first,
    then gradually slowing down before revealing the final result.

    Args:
        sides: Number of sides on the die (default: 20 for d20)
        label: Label to display during the roll (default: "Rolling")
        predetermined_result: Optional predetermined result to animate toward (for displaying pre-rolled values)

    Returns:
        The final dice roll result (1 to sides)
    """
    # Determine the final result first
    if predetermined_result is not None:
        final_roll = predetermined_result
    else:
        final_roll = random.randint(1, sides)

    # Animation parameters: start fast, end slow
    # delays in seconds for each frame
    frame_delays = [
        0.05,
        0.05,
        0.05,
        0.05,  # Fast start
        0.08,
        0.08,
        0.08,  # Getting slower
        0.12,
        0.12,  # Slower
        0.18,
        0.18,  # Even slower
        0.25,
        0.30,  # Final slow rolls
    ]

    with Live(console=console, refresh_per_second=20, transient=False) as live:
        # Show random numbers for suspense
        for delay in frame_delays:
            random_num = random.randint(1, sides)
            display = Text()
            display.append(f"🎲 {label}... ", style="bold yellow")
            display.append(f"{random_num}", style="bold white")
            live.update(display)
            time.sleep(delay)

        # Show final result with a brief pause
        final_display = Text()
        final_display.append(f"🎲 {label}... ", style="bold yellow")

        # Check for critical roll (20) or fumble (1) on d20
        if sides == 20 and final_roll == 20:
            final_display.append(f"{final_roll}", style="bold green")
            final_display.append(" ✨ CRITICAL ROLL!", style="bold cyan blink")
        elif sides == 20 and final_roll == 1:
            final_display.append(f"{final_roll}", style="bold red")
            final_display.append(" 💀 FUMBLE!", style="bold red blink")
        else:
            final_display.append(f"{final_roll}", style="bold green")

        live.update(final_display)
        time.sleep(0.4)  # Brief pause to see the result

    # Live display with transient=False leaves the final result visible
    # Add a blank line for spacing before the Roll Result panel
    console.print()

    return final_roll


def animate_multi_dice_roll(
    dice_count: int, sides: int, label: str = "Damage"
) -> tuple[list[int], int]:
    """
    Display an animated multi-dice roll with individual results.

    Args:
        dice_count: Number of dice to roll
        sides: Number of sides on each die
        label: Label to display during the roll

    Returns:
        Tuple of (individual_rolls, total)
    """
    individual_rolls = []

    for i in range(dice_count):
        roll_label = f"{label} Die {i + 1}/{dice_count}" if dice_count > 1 else label

        roll = animate_dice_roll(sides=sides, label=roll_label)
        individual_rolls.append(roll)

    total = sum(individual_rolls)
    return individual_rolls, total
