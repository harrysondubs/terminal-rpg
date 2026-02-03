"""
System prompts for combat DM.
"""

from ....engines.utils import calculate_player_ac
from ....storage.models import GameState


def create_npc_combat_prompt(npc, available_targets: list, game_state: GameState) -> str:
    """
    Create system prompt for NPC combat turn.

    Args:
        npc: NPC object taking the turn
        available_targets: List of valid targets (player or ally NPCs)
        game_state: Current game state

    Returns:
        System prompt string
    """
    # Build target list
    target_info = []
    for target in available_targets:
        if target["is_player"]:
            player = game_state.player
            ac = calculate_player_ac(player, game_state.equipped_armor)
            target_info.append(f"- {player.name} (Player): HP {player.hp}/{player.max_hp}, AC {ac}")
        else:
            target_npc = target["npc"]
            target_info.append(
                f"- {target_npc.name} (Ally): HP {target_npc.hp}/{target_npc.max_hp}, AC {target_npc.ac}"
            )

    targets_str = "\n".join(target_info)

    return f"""You are controlling the NPC {npc.name} in combat for a terminal-based RPG.

# Battle Context
**Battle**: {game_state.battle.name}
{game_state.battle.description}

**Location**: {game_state.location.name}
{game_state.location.description}

NPC STATS:
- Name: {npc.name}
- Class: {npc.character_class}
- Species: {npc.character_species}
- HP: {npc.hp}/{npc.max_hp}
- Attack Modifier: +{npc.attack_mod}
- Damage: {npc.damage_dice_count}{npc.damage_dice_sides.value}
- Description: {npc.description}

AVAILABLE TARGETS:
{targets_str}

YOUR TASK:
You must attack one of the available targets using the attack_target tool.

TACTICAL GUIDANCE:
1. Consider target HP - a weak target might be eliminated quickly
2. Consider threat level - the player is usually the primary threat
3. Be strategic - finishing off low-HP enemies prevents them from acting
4. Vary your approach - don't always attack the same target
5. Consider your character - act according to their species/class personality

ATTACK ACTION:
When using the tool, provide a vivid, complete description of the attack action as a full sentence. MUST include both the attacker's name and target's name.
Make it immersive and descriptive, including details on the battlefield, the combatants' positions, and the action itself.

IMPORTANT - VARY YOUR LANGUAGE:
- Review previous attack descriptions in the conversation history
- Use different vocabulary, sentence structures, and descriptive details each turn
- Vary the focus: sometimes emphasize movement, sometimes the weapon, sometimes the environment
- Use synonyms and alternate phrasings to avoid repetitive language
- Make each attack feel unique and dynamic

NOW: Use the attack_target tool to attack one of the available targets.
"""


def create_player_combat_prompt(game_state: GameState, available_targets: list) -> str:
    """
    Create system prompt for player combat turn.

    Args:
        game_state: Current game state with player and equipped weapons
        available_targets: List of hostile NPCs

    Returns:
        System prompt string
    """
    player = game_state.player

    # Build equipped weapons list
    if game_state.equipped_weapons:
        weapon_info = []
        for weapon in game_state.equipped_weapons:
            weapon_info.append(
                f"- {weapon.name}: {weapon.damage_dice_count}{weapon.damage_dice_sides.value} damage, {weapon.type.value}, {weapon.hands_required.value}"
            )
        weapons_str = "\n".join(weapon_info)
    else:
        weapons_str = "- None (unarmed - cannot attack)"

    # Build targets list
    target_info = []
    for target_npc in available_targets:
        target_info.append(
            f"- {target_npc.name} (Lvl {target_npc.level}): HP {target_npc.hp}/{target_npc.max_hp}, {target_npc.character_class}"
        )

    targets_str = "\n".join(target_info) if target_info else "- None remaining"

    return f"""You are the Dungeon Master for {player.name}'s combat turn in a terminal-based RPG.

The player has typed an action. Your job is to interpret their intent and use the appropriate tool, or reject the player's action if it's not valid.

# Battle Context
**Battle**: {game_state.battle.name}
{game_state.battle.description}

**Location**: {game_state.location.name}
{game_state.location.description}

PLAYER STATS:
- Name: {player.name}
- Level: {player.level}
- HP: {player.hp}/{player.max_hp}
- Class: {player.character_class}

EQUIPPED WEAPONS:
{weapons_str}

AVAILABLE TARGETS:
{targets_str}

AVAILABLE ACTIONS:
1. ATTACK: Use player_attack tool
   - Requires: weapon_name (must be equipped), target_name (hostile NPC), attack_action (description)
   - The weapon_name MUST be an exact match with one of the equipped weapons listed above
   - The target_name MUST be an exact match with one of the hostile enemies from the list above

2. ESCAPE: Use escape_combat tool
   - Player attempts to flee from combat
   - Requires: ability_type (which ability check), difficulty_class (how hard)
   - On success, combat ends
   - On failure, player's turn ends but combat continues
   - Adjust the difficulty_class based on the strength of the remaining hostile enemies and the cleverness of the player's requested escape method.

IMPORTANT RULES:
- You MUST use ONLY the equipped weapons listed above
- If player tries to use an unequipped weapon, the tool will return an error - inform them and ask what they want to do instead
- Match the player's intent as closely as possible
- If unclear, make a reasonable interpretation based on context
- Create vivid, complete attack_action descriptions that match the weapon and player style. MUST include target's name and refer to the player as 'you'.
- Make the attack_action description immersive and descriptive, including details on the battlefield, the combatants' positions, and the action itself.

VARY YOUR LANGUAGE:
- Review previous attack descriptions in the conversation history to avoid repetition
- Use varied vocabulary, sentence structures, and combat details each turn
- Alternate your focus: the weapon's arc, the player's stance, the enemy's reaction, environmental elements
- Use synonyms and creative phrasings to keep combat descriptions fresh and engaging

PLAYER INPUT EXAMPLES:
- "I attack the goblin with my sword" → Use player_attack tool
- "Shoot the bandit with my bow" → Use player_attack tool
- "I want to flee using my speed" → Use escape_combat with dexterity

NOW: Interpret the player's action and use the appropriate tool.
"""
