"""
Location management tools for DM.
"""

from ....storage.database import Database
from ....storage.models import GameState
from ....storage.repositories import CampaignRepository, LocationRepository

# ===== CHANGE LOCATION TOOL =====
CHANGE_LOCATION_TOOL = {
    "name": "change_location",
    "description": "Move the player to a different location in the game world. Use this when the player travels to a new area. You must use the exact location name from the world.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location_name": {
                "type": "string",
                "description": "The exact name of the location to move to",
            }
        },
        "required": ["location_name"],
    },
}


def change_location_execute(location_name: str, game_state: GameState, db: Database) -> str:
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

    # Check if trying to move to current location
    if game_state.location and game_state.location.name.lower() == location_name.lower():
        return f"Warning: The player is already at {game_state.location.name}. Cannot move to the current location."

    # Find location by name in current world
    locations = location_repo.get_by_world(game_state.world.id, campaign_id=game_state.campaign.id)

    target_location = None
    for loc in locations:
        if loc.name.lower() == location_name.lower():
            target_location = loc
            break

    if not target_location:
        return f"Error: Location '{location_name}' not found in {game_state.world.name}. Use the view_locations tool to see all available locations."

    # Update campaign's current location
    campaign_repo.update_current_location(game_state.campaign.id, target_location.id)

    # Update game state
    game_state.location = target_location

    return f"Successfully moved to {target_location.name}."


# ===== VIEW LOCATIONS TOOL =====
VIEW_LOCATIONS_TOOL = {
    "name": "view_locations",
    "description": "View all available locations in the current world. Use this to see where the player can travel.",
    "input_schema": {"type": "object", "properties": {}, "required": []},
}


def view_locations_execute(game_state: GameState, db: Database) -> str:
    """
    View all locations in the current world.

    Args:
        game_state: Current game state
        db: Database connection

    Returns:
        Formatted list of all available locations
    """
    location_repo = LocationRepository(db)

    # Get all locations for current world and campaign
    locations = location_repo.get_by_world(game_state.world.id, campaign_id=game_state.campaign.id)

    if not locations:
        return f"No locations found in {game_state.world.name}."

    # Format the response
    current_location_id = game_state.location.id if game_state.location else None

    location_list = []
    for loc in locations:
        if loc.id == current_location_id:
            location_list.append(f"- {loc.name} (CURRENT LOCATION)")
        else:
            location_list.append(f"- {loc.name}")
        if loc.description:
            location_list.append(f"  Description: {loc.description}")

    header = f"Available locations in {game_state.world.name}:\n"
    return header + "\n".join(location_list)


# ===== CREATE LOCATION TOOL =====
CREATE_LOCATION_TOOL = {
    "name": "create_location",
    "description": "Create a new location in the game world. Use this when the story requires a new place for the player to visit that doesn't exist yet.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location_name": {"type": "string", "description": "Name of the new location"},
            "description": {"type": "string", "description": "Description of the new location"},
        },
        "required": ["location_name", "description"],
    },
}


def create_location_execute(
    location_name: str, description: str, game_state: GameState, db: Database
) -> str:
    """
    Create a new location.

    Args:
        location_name: Name of the new location
        description: Description of the new location
        game_state: Current game state
        db: Database connection

    Returns:
        Success/failure message
    """
    from ....storage.models import Location

    # Validate inputs
    if not location_name or not location_name.strip():
        return "Error: Location name cannot be empty."

    if not description or not description.strip():
        return "Error: Location description cannot be empty."

    location_name = location_name.strip()
    description = description.strip()

    location_repo = LocationRepository(db)

    # Check if location with this name already exists
    existing_locations = location_repo.get_by_world(
        game_state.world.id, campaign_id=game_state.campaign.id
    )

    for loc in existing_locations:
        if loc.name.lower() == location_name.lower():
            return f"Error: A location named '{location_name}' already exists in {game_state.world.name}. Use a different name or use the change_location tool to move to this location."

    # Create new location
    new_location = Location(
        world_id=game_state.world.id,
        name=location_name,
        description=description,
        campaign_id=game_state.campaign.id,
    )

    try:
        created_location = location_repo.create(new_location)
        return f"Successfully created location: {created_location.name}. You can now use change_location to move the player there."
    except Exception as e:
        return f"Error creating location: {str(e)}"
