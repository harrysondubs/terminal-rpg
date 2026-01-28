"""
System prompts for battle generation.
"""

from ....storage.models import GameState


def create_generate_battle_prompt(
    context: str, opponents: str, allies: str | None, game_state: GameState
) -> str:
    """
    Create system prompt for generating a battle from context.

    Args:
        context: Battle context/setting description
        opponents: Description of enemy combatants
        allies: Optional description of allied combatants
        game_state: Current game state

    Returns:
        System prompt string
    """
    ally_info = f"\n- Allies: {allies}" if allies else "\n- No allies mentioned"

    return f"""You are generating a battle encounter for a terminal-based RPG game.

PLAYER CONTEXT:
- Name: {game_state.player.name}
- Level: {game_state.player.level}
- Class: {game_state.player.character_class}
- Location: {game_state.location.name}

BATTLE REQUEST:
- Context: {context}
- Opponents: {opponents}{ally_info}

YOUR TASK:
Create a battle encounter using the generate_battle tool. You must:

1. Extract a concise battle name (2-5 words) that captures the essence of the encounter
   Examples: "Goblin Ambush", "Dragon's Lair", "Bandit Roadblock", "Temple Guardian Fight"

2. Write a vivid battle description (2-3 sentences) that sets the scene
   - Describe the environment and atmosphere
   - Mention the enemies/threats present
   - Create tension and urgency

IMPORTANT:
- Use the generate_battle tool to create this encounter
- Keep the name short and memorable
- Make the description engaging and atmospheric
"""


def create_generate_npcs_prompt(
    context: str,
    opponents: str,
    allies: str | None,
    game_state: GameState,
) -> str:
    """
    Create system prompt for generating NPCs for a battle.

    Args:
        context: Battle context/setting description
        opponents: Description of enemy combatants
        allies: Optional description of allied combatants
        game_state: Current game state

    Returns:
        System prompt string
    """
    player = game_state.player

    ally_info = f"\n- Allies: {allies}" if allies else "\n- No allies"

    return f"""You are generating NPCs (combatants) for a battle in a terminal-based RPG game.

PLAYER CONTEXT:
- Name: {player.name}
- Level: {player.level}
- HP: {player.hp}/{player.max_hp}
- Class: {player.character_class}

BATTLE CONTEXT:
- Context: {context}
- Opponents: {opponents}{ally_info}

YOUR TASK:
Create NPCs using the generate_battle_npcs tool.

STAT GUIDELINES BY PLAYER LEVEL (Level {player.level}):

Level 1-2 (Novice):
- Enemy HP: 8-15
- Enemy AC: 10-13
- Enemy Attack Mod: +2 to +4
- Enemy Damage: 1d6 or 2d4
- Enemy Initiative Mod: 0 to +2
- Quantity: 2-3 weak enemies OR 1 moderate enemy

Level 3-5 (Experienced):
- Enemy HP: 15-30
- Enemy AC: 12-15
- Enemy Attack Mod: +3 to +6
- Enemy Damage: 1d8+2 or 2d6
- Enemy Initiative Mod: +1 to +3
- Quantity: 2-4 enemies of mixed strength

Level 6-8 (Veteran):
- Enemy HP: 25-50
- Enemy AC: 14-17
- Enemy Attack Mod: +5 to +8
- Enemy Damage: 2d8 or 1d12+4
- Enemy Initiative Mod: +2 to +4
- Quantity: 3-5 enemies OR 1-2 powerful enemies

Level 9+ (Heroic):
- Enemy HP: 40-80+
- Enemy AC: 16-20
- Enemy Attack Mod: +7 to +12
- Enemy Damage: 2d10+5 or 3d8
- Enemy Initiative Mod: +3 to +6
- Quantity: 4-6 enemies OR 2-3 elite enemies

NPC CREATION RULES:

1. DISPOSITION:
   - Opponents/enemies: "hostile"
   - Allies: "ally"

2. NAMES: Give each NPC a unique, descriptive name
   - Enemies: "Goblin Scout", "Bandit Captain", "Fire Drake"
   - Allies: "Guard Captain Marcus", "Elven Archer Lyra"

3. DESCRIPTIONS: Write 1-2 sentences describing appearance/demeanor

4. CLASSES: Match class to creature type
   - Warriors: Melee fighters, guards, soldiers
   - Rogues: Scouts, thieves, assassins
   - Mages: Spellcasters, shamans, cultists
   - Beasts: Animals, monsters (use creature type as class)

5. SPECIES: Be specific
   - Humanoids: Human, Elf, Dwarf, Goblin, Orc
   - Creatures: Wolf, Drake, Skeleton, etc.

6. GOLD: Scale with level
   - Low level (1-3): 5-20 gold
   - Mid level (4-6): 15-50 gold
   - High level (7+): 30-100+ gold

7. XP: Set to level * 10 (this is automatic, but use appropriate level)

8. BALANCE: Make combat challenging but winnable
   - Scale stats to player level
   - Consider player HP when setting total enemy HP
   - Mix enemy types (some weak, some strong)

EXAMPLE NPC (for Level 3 player):
{{
    "name": "Goblin Raider",
    "description": "A snarling goblin with crude leather armor and a rusty blade.",
    "character_class": "Warrior",
    "character_species": "Goblin",
    "max_hp": 18,
    "ac": 12,
    "attack_mod": 4,
    "damage_dice_count": 1,
    "damage_dice_sides": "d6",
    "initiative_mod": 2,
    "disposition": "hostile",
    "gold": 10,
    "level": 2
}}

NOW: Create the NPCs array using the generate_battle_npcs tool.
Parse the opponents and allies descriptions and create appropriate NPCs for each.
"""
