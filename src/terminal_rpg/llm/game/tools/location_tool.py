"""
Location change tool for DM.
"""

from ....storage.database import Database
from ....storage.models import GameState
from ....storage.repositories import CampaignRepository, LocationRepository


# Tool definition for Claude API
TOOL_DEFINITION = {
    "name": "change_location",
    "description": "Move the player to a different location in the game world. Use this when the player travels to a new area. You must use the exact location name from the world.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location_name": {
                "type": "string",
                "description": "The exact name of the location to move to"
            }
        },
        "required": ["location_name"]
    }
}


def execute(location_name: str, game_state: GameState, db: Database) -> str:
    """
    Change player's current location.

    Args:
        location_name: Name of destination location
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message
    """
    location_repo = LocationRepository(db)
    campaign_repo = CampaignRepository(db)

    # Find location by name in current world
    locations = location_repo.get_by_world(
        game_state.world.id,
        campaign_id=game_state.campaign.id
    )

    target_location = None
    for loc in locations:
        if loc.name.lower() == location_name.lower():
            target_location = loc
            break

    if not target_location:
        return f"Error: Location '{location_name}' not found in {game_state.world.name}."

    # Update campaign's current location
    campaign_repo.update_current_location(game_state.campaign.id, target_location.id)

    # Update game state
    game_state.location = target_location

    return f"Successfully moved to {target_location.name}."
