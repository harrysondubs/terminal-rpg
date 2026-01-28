"""
Battle generation tools for DM.
"""

from ....storage.database import Database
from ....storage.models import NPC, Battle, DamageDiceSides, Disposition, GameState
from ....storage.repositories import BattleParticipantRepository, BattleRepository, NPCRepository

# ===== GENERATE BATTLE TOOL =====
GENERATE_BATTLE_TOOL = {
    "name": "generate_battle",
    "description": "Create a new battle encounter. Use this to set up a combat scenario with a name and description. After creating the battle, use generate_battle_npcs to add enemies to it.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the battle encounter (e.g., 'Goblin Ambush', 'Dragon's Lair')",
            },
            "description": {
                "type": "string",
                "description": "A description of the battle scenario and setting",
            },
        },
        "required": ["name", "description"],
    },
}


def generate_battle_execute(
    name: str, description: str, game_state: GameState, db: Database
) -> str:
    """
    Create a new battle encounter.

    Args:
        name: Name of the battle
        description: Description of the battle scenario
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message with battle_id
    """
    # Validate inputs
    if not name or not name.strip():
        return "Error: Battle name cannot be empty."

    if not description or not description.strip():
        return "Error: Battle description cannot be empty."

    name = name.strip()
    description = description.strip()

    battle_repo = BattleRepository(db)

    # Create new battle
    new_battle = Battle(
        world_id=game_state.world.id,
        campaign_id=game_state.campaign.id,
        name=name,
        description=description,
    )

    try:
        created_battle = battle_repo.create(new_battle)
        return f"Successfully created battle '{created_battle.name}' (ID: {created_battle.id}). Use generate_battle_npcs with battle_id={created_battle.id} to add enemies to this battle."
    except Exception as e:
        return f"Error creating battle: {str(e)}"


# ===== GENERATE BATTLE NPCS TOOL =====
GENERATE_BATTLE_NPCS_TOOL = {
    "name": "generate_battle_npcs",
    "description": "Create NPCs for the battle encounter. Creates the enemies/allies for the combat scenario based on the descriptions provided.",
    "input_schema": {
        "type": "object",
        "properties": {
            "npcs": {
                "type": "array",
                "description": "Array of NPC objects to create and add to the battle",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the NPC",
                        },
                        "description": {
                            "type": "string",
                            "description": "Physical description and characteristics of the NPC",
                        },
                        "character_class": {
                            "type": "string",
                            "description": "The NPC's class (e.g., 'Warrior', 'Mage', 'Rogue')",
                        },
                        "character_species": {
                            "type": "string",
                            "description": "The NPC's species/race (e.g., 'Goblin', 'Human', 'Dragon')",
                        },
                        "max_hp": {
                            "type": "integer",
                            "description": "Maximum hit points",
                        },
                        "ac": {
                            "type": "integer",
                            "description": "Armor class (defense rating)",
                        },
                        "attack_mod": {
                            "type": "integer",
                            "description": "Attack modifier (bonus to attack rolls)",
                        },
                        "damage_dice_count": {
                            "type": "integer",
                            "description": "Number of damage dice to roll",
                        },
                        "damage_dice_sides": {
                            "type": "string",
                            "description": "Type of damage dice",
                            "enum": ["d4", "d6", "d8", "d10", "d12"],
                        },
                        "initiative_mod": {
                            "type": "integer",
                            "description": "Initiative modifier (bonus to initiative rolls)",
                        },
                        "disposition": {
                            "type": "string",
                            "description": "NPC's disposition toward the player",
                            "enum": ["hostile", "ally"],
                        },
                        "gold": {
                            "type": "integer",
                            "description": "Amount of gold the NPC carries",
                        },
                        "level": {
                            "type": "integer",
                            "description": "NPC's level",
                        },
                    },
                    "required": [
                        "name",
                        "description",
                        "character_class",
                        "character_species",
                        "max_hp",
                        "ac",
                        "attack_mod",
                        "damage_dice_count",
                        "damage_dice_sides",
                        "initiative_mod",
                        "disposition",
                        "gold",
                        "level",
                    ],
                },
            },
        },
        "required": ["npcs"],
    },
}


def generate_battle_npcs_execute(
    battle_id: int, npcs: list[dict], game_state: GameState, db: Database
) -> str:
    """
    Create NPCs and link them to a battle.

    Args:
        battle_id: ID of the battle to add NPCs to
        npcs: List of NPC data dictionaries
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message with count of NPCs created
    """
    # Validate inputs
    if not npcs or len(npcs) == 0:
        return "Error: Must provide at least one NPC."

    battle_repo = BattleRepository(db)
    npc_repo = NPCRepository(db)
    participant_repo = BattleParticipantRepository(db)

    # Verify battle exists
    battle = battle_repo.get_by_id(battle_id)
    if not battle:
        return f"Error: Battle with ID {battle_id} not found."

    created_npcs = []
    errors = []

    for idx, npc_data in enumerate(npcs):
        try:
            # Validate required fields
            required_fields = [
                "name",
                "description",
                "character_class",
                "character_species",
                "max_hp",
                "ac",
                "attack_mod",
                "damage_dice_count",
                "damage_dice_sides",
                "initiative_mod",
                "disposition",
                "gold",
                "level",
            ]

            for field in required_fields:
                if field not in npc_data:
                    raise ValueError(f"Missing required field: {field}")

            # Convert damage_dice_sides to enum
            try:
                damage_dice = DamageDiceSides(npc_data["damage_dice_sides"].lower())
            except (ValueError, KeyError):
                raise ValueError(
                    f"Invalid damage_dice_sides: {npc_data.get('damage_dice_sides')}. Must be one of: d4, d6, d8, d10, d12"
                ) from None

            # Convert disposition to enum
            try:
                disposition = Disposition(npc_data["disposition"].lower())
            except (ValueError, KeyError):
                raise ValueError(
                    f"Invalid disposition: {npc_data.get('disposition')}. Must be 'hostile' or 'ally'"
                ) from None

            # Create NPC object (hp starts at max_hp, xp = level * 10)
            new_npc = NPC(
                world_id=game_state.world.id,
                campaign_id=game_state.campaign.id,
                name=npc_data["name"],
                description=npc_data["description"],
                character_class=npc_data["character_class"],
                character_species=npc_data["character_species"],
                hp=npc_data["max_hp"],  # Start at full health
                max_hp=npc_data["max_hp"],
                ac=npc_data["ac"],
                attack_mod=npc_data["attack_mod"],
                damage_dice_count=npc_data["damage_dice_count"],
                damage_dice_sides=damage_dice,
                initiative_mod=npc_data["initiative_mod"],
                disposition=disposition,
                gold=npc_data["gold"],
                level=npc_data["level"],
                xp=npc_data["level"] * 10,  # XP reward based on level
            )

            # Create NPC in database
            created_npc = npc_repo.create(new_npc)

            # Link NPC to battle
            participant_repo.add_participant(
                battle_id=battle_id,
                npc_id=created_npc.id,
                is_active=True,
            )

            created_npcs.append(created_npc.name)

        except Exception as e:
            errors.append(f"NPC #{idx + 1} ({npc_data.get('name', 'unknown')}): {str(e)}")

    # Build response
    if not created_npcs and errors:
        return "Error: Failed to create any NPCs.\n" + "\n".join(errors)

    response_parts = [
        f"Successfully created {len(created_npcs)} NPC(s) for battle '{battle.name}':",
        ", ".join(created_npcs),
    ]

    if errors:
        response_parts.append("\nWarnings:")
        response_parts.extend(errors)

    return "\n".join(response_parts)
