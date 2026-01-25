"""
Player gold adjustment tool for DM.
"""

from rich.console import Console
from rich.panel import Panel

from ....storage.database import Database
from ....storage.models import GameState
from ....storage.repositories import PlayerRepository


console = Console()


# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "adjust_player_gold",
    "description": "Adjust the player's gold amount. Use positive numbers to give gold, negative numbers to take gold. The player must have sufficient gold for negative adjustments.",
    "input_schema": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "integer",
                "description": "Amount of gold to add (positive) or remove (negative)"
            }
        },
        "required": ["amount"]
    }
}


def execute(amount: int, game_state: GameState, db: Database) -> str:
    """
    Adjust player's gold amount.

    Args:
        amount: Gold to add (positive) or remove (negative)
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message
    """
    player = game_state.player
    new_gold = player.gold + amount

    # Check if player has enough gold for negative adjustments
    if new_gold < 0:
        warning_msg = f"[bold red]Insufficient Gold![/bold red]\n\nCannot remove {abs(amount)} gold.\n{player.name} only has {player.gold} gold."
        console.print()
        console.print(Panel(warning_msg, border_style="red", title="⚠️  Transaction Failed"))
        console.print()
        return f"Warning: Cannot remove {abs(amount)} gold. {player.name} only has {player.gold} gold."

    # Update player's gold
    player_repo = PlayerRepository(db)
    player_repo.update_gold(player.id, new_gold)

    # Update game state
    old_gold = player.gold
    player.gold = new_gold

    # Display visual feedback to player
    console.print()

    if amount > 0:
        # Gold gained
        display_msg = f"[bold yellow]💰 Gold Gained![/bold yellow]\n\n[green]+{amount} gold[/green]\n\n{old_gold} → [bold yellow]{new_gold}[/bold yellow] gold"
        console.print(Panel(display_msg, border_style="yellow", title="Gold"))
        result = f"Added {amount} gold to {player.name}'s inventory. New balance: {new_gold} gold."
    else:
        # Gold spent/lost
        display_msg = f"[bold yellow]💸 Gold Reduced[/bold yellow]\n\n[red]{amount} gold[/red]\n\n{old_gold} → [bold yellow]{new_gold}[/bold yellow] gold"
        console.print(Panel(display_msg, border_style="yellow", title="Gold"))
        result = f"Removed {abs(amount)} gold from {player.name}'s inventory. New balance: {new_gold} gold."

    console.print()
    return result
