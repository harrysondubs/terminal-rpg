"""
Ability check tool for DM - handles skill checks with dice rolls.
"""

from enum import Enum
from typing import Dict

from rich.console import Console
from rich.panel import Panel

from ....engines.dice import calculate_ability_modifier, roll_d20
from ....storage.models import GameState


console = Console()


class AbilityType(Enum):
    """Enum for ability types"""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "ability_check",
    "description": "Request an ability check from the player. Use this when the player attempts an action that requires a skill check. The player will roll a d20 and add their ability modifier. Common DCs: 10 (Easy), 15 (Medium), 20 (Hard), 25 (Very Hard), 30 (Nearly Impossible).",
    "input_schema": {
        "type": "object",
        "properties": {
            "ability_type": {
                "type": "string",
                "enum": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
                "description": "The ability to check against"
            },
            "difficulty_class": {
                "type": "integer",
                "description": "The DC (difficulty class) - target number the player must meet or beat. Range: 1-30",
                "minimum": 1,
                "maximum": 30
            },
            "context": {
                "type": "string",
                "description": "Brief description of what the player is attempting (e.g., 'climb the wall', 'persuade the guard', 'recall ancient lore')"
            }
        },
        "required": ["ability_type", "difficulty_class", "context"]
    }
}


def execute(ability_type: str, difficulty_class: int, context: str, game_state: GameState) -> str:
    """
    Execute an ability check with interactive dice roll.

    Args:
        ability_type: Which ability to check (strength, dexterity, etc.)
        difficulty_class: Target DC to meet or beat
        context: Description of what player is attempting
        game_state: Current game state

    Returns:
        Result message indicating success or failure
    """
    player = game_state.player
    ability_type_enum = AbilityType(ability_type)

    # Get the relevant ability score
    ability_scores: Dict[AbilityType, int] = {
        AbilityType.STRENGTH: player.strength,
        AbilityType.DEXTERITY: player.dexterity,
        AbilityType.CONSTITUTION: player.constitution,
        AbilityType.INTELLIGENCE: player.intelligence,
        AbilityType.WISDOM: player.wisdom,
        AbilityType.CHARISMA: player.charisma,
    }

    ability_score = ability_scores[ability_type_enum]
    modifier = calculate_ability_modifier(ability_score)
    modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)

    # Display check prompt to player
    check_display = f"""[bold yellow]{ability_type.upper()} CHECK[/bold yellow]

[italic]{context}[/italic]

[bold]Your {ability_type.capitalize()}:[/bold] {ability_score} (modifier: {modifier_str})

Press Enter to roll the d20..."""

    console.print()
    console.print(Panel(check_display, border_style="yellow", title="Ability Check"))

    # Wait for player input
    input()

    # Roll the dice
    roll = roll_d20()
    total = roll + modifier

    # Determine success/failure (don't show DC to player)
    success = total >= difficulty_class

    # Display result
    result_color = "green" if success else "red"
    result_text = "SUCCESS" if success else "FAILURE"

    result_display = f"""[bold]Roll:[/bold] {roll}
[bold]Modifier:[/bold] {modifier_str}
[bold]Total:[/bold] {total}

[bold {result_color}]{result_text}![/bold {result_color}]"""

    console.print()
    console.print(Panel(result_display, border_style=result_color, title="Roll Result"))
    console.print()

    # Return result to DM
    if success:
        return f"Ability check PASSED! {player.name} rolled {roll} + {modifier_str} = {total} vs DC {difficulty_class} for {context}."
    else:
        return f"Ability check FAILED. {player.name} rolled {roll} + {modifier_str} = {total} vs DC {difficulty_class} for {context}."
