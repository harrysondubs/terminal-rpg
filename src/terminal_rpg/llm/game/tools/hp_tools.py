"""
Player HP adjustment tool for DM.
"""

from rich.console import Console
from rich.panel import Panel

from ....storage.database import Database
from ....storage.models import GameState
from ....storage.repositories import PlayerRepository

console = Console()


# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "adjust_player_hp",
    "description": "Adjust the player's hit points. Use positive numbers to heal, negative numbers for damage. HP cannot exceed max HP or go below 0. If HP reaches 0, the player dies.",
    "input_schema": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "HP to add (positive for healing) or remove (negative for damage)",
            }
        },
        "required": ["amount"],
    },
}


def execute(amount: int, game_state: GameState, db: Database) -> str:
    """
    Adjust player's HP.

    Args:
        amount: HP to add (positive) or remove (negative)
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message
    """
    player = game_state.player
    old_hp = player.hp
    new_hp = player.hp + amount

    # Clamp HP between 0 and max_hp
    if new_hp > player.max_hp:
        new_hp = player.max_hp
    elif new_hp < 0:
        new_hp = 0

    # Update player's HP
    player_repo = PlayerRepository(db)
    player_repo.update_hp(player.id, new_hp)

    # Update game state
    player.hp = new_hp

    # Display visual feedback to player
    console.print()

    # Check for game over
    if new_hp == 0:
        from ....ui.battle_display import display_game_over

        display_game_over(player)
        return f"💀 GAME OVER 💀\n\n{player.name} has fallen in battle! Your adventure ends here.\n\nFinal Stats:\n- Level: {player.level}\n- Gold: {player.gold}\n- XP: {player.xp}"

    # Create HP bar representation
    hp_percent = (new_hp / player.max_hp) * 100
    bar_length = 20
    filled_length = int(bar_length * new_hp / player.max_hp)

    # Color based on HP percentage
    if hp_percent > 60:
        hp_color = "green"
    elif hp_percent > 30:
        hp_color = "yellow"
    else:
        hp_color = "red"

    hp_bar = "█" * filled_length + "░" * (bar_length - filled_length)

    # Return appropriate message based on healing or damage
    if amount > 0:
        # Healing
        display_msg = f"[bold green]💚 Healed![/bold green]\n\n[green]+{amount} HP[/green]\n\n{old_hp}/{player.max_hp} → [bold {hp_color}]{new_hp}/{player.max_hp}[/bold {hp_color}] HP\n\n[{hp_color}]{hp_bar}[/{hp_color}]"
        console.print(Panel(display_msg, border_style="green", title="Health"))

        if new_hp == player.max_hp:
            result = f"Healed {player.name} for {amount} HP. Now at full health: {new_hp}/{player.max_hp} HP."
        else:
            result = f"Healed {player.name} for {amount} HP. Current HP: {new_hp}/{player.max_hp}."
    else:
        # Damage
        display_msg = f"[bold red]💔 Damage Taken![/bold red]\n\n[red]{amount} HP[/red]\n\n{old_hp}/{player.max_hp} → [bold {hp_color}]{new_hp}/{player.max_hp}[/bold {hp_color}] HP\n\n[{hp_color}]{hp_bar}[/{hp_color}]"
        console.print(Panel(display_msg, border_style="red", title="Health"))
        result = f"{player.name} took {abs(amount)} damage! Current HP: {new_hp}/{player.max_hp}."

    console.print()
    return result
