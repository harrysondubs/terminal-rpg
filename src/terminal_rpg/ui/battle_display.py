"""
Battle-specific UI display functions.
Handles all console I/O for combat encounters.
"""

import random
import time

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
                    # TODO: Differentiate between allies and opponents by color, for example:
                    ## [cyan]• {ally.name} (Lvl {ally.level}) - {ally.character_class}[/cyan]
                    ## [red]• {opponent.name} (Lvl {opponent.level}) - {opponent.character_class}[/red]
                )
    console.print()


def display_game_over(player) -> None:
    """
    Display game over screen when player dies.

    Args:
        player: Player object with final stats
    """
    game_over_msg = f"""[bold red]💀 GAME OVER 💀[/bold red]

{player.name} has fallen in battle!
Your adventure ends here.

[bold yellow]Final Stats:[/bold yellow]
• Level: {player.level}
• Gold: {player.gold}
• XP: {player.xp}"""

    console.print()
    console.print(Panel(game_over_msg, border_style="red", title="☠️  Death"))
    console.print()


def display_combat_status(
    battle,
    participants_with_npcs: list[tuple],
    player,
    current_turn_name: str,
    is_player_turn: bool = False,
) -> None:
    """
    Display current combat status with all combatants and HP.

    Args:
        battle: Battle object
        participants_with_npcs: List of tuples (participant, npc_or_none) sorted by turn order
        player: Player object
        current_turn_name: Name of the combatant whose turn it is
        is_player_turn: Whether it's currently the player's turn (shows combatants list)
    """
    console.print()
    console.print(f"[bold yellow]⚔️  {battle.name}  ⚔️[/bold yellow]")
    console.print()

    # Display current turn
    console.print(f"[bold cyan]Current Turn:[/bold cyan] {current_turn_name}")
    console.print()

    # Only display combatants list on player's turn for cleaner combat flow
    if is_player_turn:
        console.print("[bold]Combatants:[/bold]")

        for participant, npc in participants_with_npcs:
            if not participant.is_active:
                continue  # Skip defeated combatants

            if participant.player_id is not None:
                # Player
                hp_percent = (player.hp / player.max_hp) * 100
                if hp_percent > 60:
                    hp_color = "green"
                elif hp_percent > 30:
                    hp_color = "yellow"
                else:
                    hp_color = "red"

                console.print(
                    f"  • [bold green]{player.name}[/bold green] - HP: [{hp_color}]{player.hp}/{player.max_hp}[/{hp_color}]"
                )
            else:
                if npc:
                    # NPC (ally or opponent) - display descriptive status instead of numbers
                    hp_percent = (npc.hp / npc.max_hp) * 100 if npc.max_hp > 0 else 0

                    # Determine descriptive HP status with color
                    if hp_percent == 100:
                        hp_status = "[bright_green]Unscathed[/bright_green]"
                    elif hp_percent >= 90:
                        hp_status = "[green]Barely Scratched[/green]"
                    elif hp_percent >= 70:
                        hp_status = "[green]Lightly Wounded[/green]"
                    elif hp_percent >= 50:
                        hp_status = "[yellow]Bloodied[/yellow]"
                    elif hp_percent >= 30:
                        hp_status = "[orange1]Heavily Wounded[/orange1]"
                    elif hp_percent >= 10:
                        hp_status = "[red]Grievously Injured[/red]"
                    else:
                        hp_status = "[bold red]Near Death[/bold red]"

                    from ..storage.models import Disposition

                    name_color = "cyan" if npc.disposition == Disposition.ALLY else "red"
                    console.print(f"  • [{name_color}]{npc.name}[/{name_color}] - {hp_status}")

        console.print()


def display_attack_sequence(
    attack_action: str,
    roll: int,
    total: int,
    hit: bool,
    target_ac: int,
    damage: int = 0,
    damage_dice_count: int = 1,
    damage_dice_sides: str = "d6",
    is_critical: bool = False,
    attacker_is_ally: bool = True,
    target_old_hp: int | None = None,
    target_new_hp: int | None = None,
) -> None:
    """
    Display the full attack sequence with animated rolls for NPCs.

    Args:
        attacker_name: Name of the attacker
        target_name: Name of the target
        attack_action: Descriptive action text
        roll: Raw d20 roll
        total: Total attack roll (roll + modifiers)
        hit: Whether the attack hit
        target_ac: Target's armor class
        damage: Damage dealt (if hit)
        damage_dice_count: Number of damage dice (for animation, already doubled if critical)
        damage_dice_sides: Damage dice type (e.g., "d6")
        is_critical: Whether this was a critical hit (natural 20)
        attacker_is_ally: Whether the attacker is player or ally (True) or enemy (False).
                         Colors are shown from player perspective: ally hit=green, enemy hit=red
        target_old_hp: Target's HP before damage (optional, for player targets)
        target_new_hp: Target's HP after damage (optional, for player targets)
    """
    from .game_display import animate_dice_roll

    console.print()

    # Display attack action with typing effect
    # attack_action should be a complete sentence including attacker and target
    import sys

    for char in attack_action:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.025)

    print()  # Newline after typing
    console.print()

    # Animate attack roll with predetermined result
    animate_dice_roll(sides=20, label="Attack Roll", predetermined_result=roll)

    # Display attack result with modifier breakdown
    # Color from player's perspective:
    # - Ally hitting = green (good), ally missing = red (bad)
    # - Enemy hitting = red (bad), enemy missing = green (good)
    result_color = ("green" if hit else "red") if attacker_is_ally else ("red" if hit else "green")

    result_text = "CRITICAL HIT!" if is_critical else ("HIT!" if hit else "MISS!")

    # Calculate modifier
    attack_modifier = total - roll
    modifier_str = f"+{attack_modifier}" if attack_modifier >= 0 else str(attack_modifier)

    result_display = f"""[bold]Roll:[/bold] {roll}
[bold]Modifier:[/bold] {modifier_str}
[bold]Total:[/bold] {total}

[bold red]Attack: {total}[/bold red] vs [bold cyan]AC: {target_ac}[/bold cyan]

[bold {result_color}]{result_text}[/bold {result_color}]"""

    if is_critical:
        result_display += "\n[bold yellow]⚡ Damage dice doubled! ⚡[/bold yellow]"

    console.print()
    console.print(Panel(result_display, border_style=result_color, title="Attack Result"))
    console.print()

    # Animate damage roll if hit
    if hit and damage > 0:
        # Parse dice sides
        sides = int(damage_dice_sides[1:])  # Remove 'd' prefix

        # Distribute the total damage across dice for animation
        # We need to show realistic individual rolls that sum to the damage total
        individual_rolls = []
        remaining = damage

        for i in range(damage_dice_count):
            if i == damage_dice_count - 1:
                # Last die gets whatever is left (bounded by die size)
                roll_value = max(1, min(sides, remaining))
            else:
                # Calculate a valid range for this die
                min_needed_for_rest = damage_dice_count - i - 1  # At least 1 per remaining die
                max_for_this = min(sides, remaining - min_needed_for_rest)
                min_for_this = max(1, remaining - (damage_dice_count - i - 1) * sides)

                # Pick a value in valid range
                if min_for_this <= max_for_this:
                    # Try to make it look more realistic by favoring middle values
                    roll_value = random.randint(min_for_this, max_for_this)
                else:
                    roll_value = 1

            individual_rolls.append(roll_value)
            remaining -= roll_value

        # Animate each die with its predetermined result
        for i, roll_value in enumerate(individual_rolls):
            if damage_dice_count > 1:
                label = f"Damage Die {i + 1}/{damage_dice_count}"
            else:
                label = "Damage Roll"
            animate_dice_roll(sides=sides, label=label, predetermined_result=roll_value)

        # Show breakdown if multiple dice
        if damage_dice_count > 1:
            console.print()
            console.print(
                f"[bold]Individual rolls:[/bold] {' + '.join(map(str, individual_rolls))} = [bold red]{damage}[/bold red]"
            )

        # Display total damage
        damage_result = f"[bold red]Total Damage:[/bold red] {damage}"

        # Add HP change if target is player (both HP values provided)
        if target_old_hp is not None and target_new_hp is not None:
            # Calculate HP percentage for color
            hp_percent = (target_new_hp / target_old_hp) * 100 if target_old_hp > 0 else 0

            if hp_percent > 60:
                hp_color = "green"
            elif hp_percent > 30:
                hp_color = "yellow"
            else:
                hp_color = "red"

            damage_result += (
                f"\n[bold]HP:[/bold] {target_old_hp} → [{hp_color}]{target_new_hp}[/{hp_color}]"
            )

        console.print()
        console.print(Panel(damage_result, border_style="red", title="Damage Dealt"))
        console.print()


def display_npc_defeated(npc, xp_gained: int, gold_gained: int) -> None:
    """
    Display enemy defeat message and XP and gold rewards.

    Args:
        npc: NPC object that was defeated
        xp_gained: XP awarded for the defeat
        gold_gained: Gold awarded for the defeat
    """
    defeat_msg = f"""[bold green]{npc.name} has been defeated![/bold green]

[bold yellow]+{xp_gained} XP[/bold yellow]
[bold yellow]+{gold_gained} gold[/bold yellow]"""

    console.print()
    console.print(Panel(defeat_msg, border_style="yellow", title="NPC Defeated!"))
    console.print()


def display_combat_victory(defeated_enemies: list, total_xp: int, total_gold: int) -> None:
    """
    Display combat victory screen with rewards.

    Args:
        defeated_enemies: List of defeated NPC names
        total_xp: Total XP gained
        total_gold: Total gold looted
    """
    enemy_list = "\n".join([f"  • {name}" for name in defeated_enemies])

    victory_msg = f"""[bold green]⚔️  VICTORY! ⚔️[/bold green]

You have defeated all enemies!

[bold]Defeated:[/bold]
{enemy_list}

[bold yellow]Rewards:[/bold yellow]
• XP Gained: {total_xp}
• Gold Looted: {total_gold}"""

    console.print()
    console.print(Panel(victory_msg, border_style="green", title="🎉 Combat Victory 🎉"))
    console.print()


def display_combat_escaped() -> None:
    """Display successful combat escape message."""
    escape_msg = "[bold green]You successfully escaped from combat![/bold green]"

    console.print()
    console.print(Panel(escape_msg, border_style="green", title="Escaped"))
    console.print()


def display_combat_escape_failed(damage: int, old_hp: int, new_hp: int) -> None:
    """
    Display failed combat escape attempt with damage taken.

    Args:
        damage: Damage taken from failed escape
        old_hp: Player's HP before damage
        new_hp: Player's HP after damage
    """
    # Calculate HP percentage for color
    hp_percent = (new_hp / old_hp) * 100 if old_hp > 0 else 0

    if hp_percent > 60:
        hp_color = "green"
    elif hp_percent > 30:
        hp_color = "yellow"
    else:
        hp_color = "red"

    escape_msg = f"""[bold red]Escape attempt failed![/bold red]

You take [bold red]{damage} damage[/bold red] from your failed escape!

[bold]HP:[/bold] {old_hp} → [{hp_color}]{new_hp}[/{hp_color}]"""

    if new_hp == 0:
        escape_msg += "\n\n[bold red]💀 You have been defeated! 💀[/bold red]"

    console.print()
    console.print(Panel(escape_msg, border_style="red", title="Escape Failed"))
    console.print()


def display_player_attack_interactive(
    attacker_name: str,
    target_name: str,
    attack_action: str,
    attack_bonus: int,
    target_ac: int,
    weapon_damage_dice_count: int,
    weapon_damage_dice_sides: str,
) -> tuple[int, int, bool, int]:
    """
    Display interactive player attack with prompts and animations.

    Args:
        attacker_name: Player's name
        target_name: Target's name
        attack_action: Descriptive attack action
        attack_bonus: Player's attack bonus
        target_ac: Target's AC
        weapon_damage_dice_count: Number of damage dice
        weapon_damage_dice_sides: Damage dice type (e.g., "d6")

    Returns:
        Tuple of (attack_roll, attack_total, is_hit, damage)
    """
    from .game_display import animate_dice_roll, animate_multi_dice_roll

    console.print()

    # Display attack action with typing effect (should be a complete sentence)
    import sys

    for char in attack_action:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.025)

    print()  # Newline after typing
    console.print()

    # Prompt for attack roll
    attack_prompt = f"""[bold yellow]ATTACK ROLL[/bold yellow]

Your attack bonus: {"+" if attack_bonus >= 0 else ""}{attack_bonus}

Press Enter to roll the d20..."""

    console.print(Panel(attack_prompt, border_style="yellow", title="Attack"))
    input()

    # Animate attack roll
    attack_roll = animate_dice_roll(sides=20, label="Attack Roll")
    attack_total = attack_roll + attack_bonus

    # Determine hit/miss and critical
    is_critical = attack_roll == 20
    # Critical hit (nat 20) is always a hit, regardless of AC
    is_hit = is_critical or attack_total >= target_ac

    # Display attack result
    result_color = "green" if is_hit else "red"
    result_text = "CRITICAL HIT!" if is_critical else ("HIT!" if is_hit else "MISS!")

    attack_result = f"""[bold]Roll:[/bold] {attack_roll}
[bold]Bonus:[/bold] {"+" if attack_bonus >= 0 else ""}{attack_bonus}
[bold]Total:[/bold] {attack_total}

[bold {result_color}]{result_text}[/bold {result_color}]"""

    if is_critical:
        attack_result += "\n[bold yellow]⚡ Damage dice doubled! ⚡[/bold yellow]"

    console.print()
    console.print(Panel(attack_result, border_style=result_color, title="Attack Result"))
    console.print()

    # Roll damage if hit
    damage = 0
    if is_hit:
        # Double damage dice on critical hit
        effective_dice_count = (
            weapon_damage_dice_count * 2 if is_critical else weapon_damage_dice_count
        )

        # Prompt for damage roll
        dice_str = f"{effective_dice_count}{weapon_damage_dice_sides}"
        damage_prompt = f"""[bold red]DAMAGE ROLL[/bold red]

Your weapon deals: {dice_str}"""

        if is_critical:
            damage_prompt += "\n[bold yellow](Dice doubled from critical hit!)[/bold yellow]"

        damage_prompt += "\n\nPress Enter to roll for damage..."

        console.print(Panel(damage_prompt, border_style="red", title="Damage"))
        input()

        # Parse dice sides
        sides = int(weapon_damage_dice_sides[1:])  # Remove 'd' prefix

        # Animate damage roll(s)
        if effective_dice_count == 1:
            damage = animate_dice_roll(sides=sides, label="Damage Roll")
        else:
            individual_rolls, damage = animate_multi_dice_roll(
                effective_dice_count, sides, "Damage"
            )
            console.print()
            console.print(
                f"[bold]Individual rolls:[/bold] {' + '.join(map(str, individual_rolls))} = [bold red]{damage}[/bold red]"
            )

        # Display damage result
        damage_result = f"[bold red]Total Damage:[/bold red] {damage}"
        console.print()
        console.print(Panel(damage_result, border_style="red", title="Damage Dealt"))
        console.print()

    return attack_roll, attack_total, is_hit, damage
