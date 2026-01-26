"""
Questionary interactions for user input.
"""

import questionary
from ..storage.models import World
from ..campaign_presets import CampaignPreset, CharacterClassPreset


def show_start_menu() -> str:
    """
    Display main menu and return user's choice.

    Returns:
        One of: "new_game", "load_game", "exit"
    """
    choices = [
        "New Game",
        "Load Game",
        "Exit"
    ]

    answer = questionary.select(
        "Welcome to Terminal RPG. Select an option below to continue:",
        choices=choices
    ).ask()

    # Handle cancellation
    if answer is None:
        return "exit"

    # Map answer to return value
    mapping = {
        "New Game": "new_game",
        "Load Game": "load_game",
        "Exit": "exit"
    }

    return mapping.get(answer, "exit")


def select_world(worlds: list[World]) -> World | None:
    """
    Display world selection menu.

    Args:
        worlds: List of available worlds

    Returns:
        Selected World object or None if cancelled/create new
    """
    # Build choices list with world names + "Create Your Own"
    choices = [world.name for world in worlds]
    choices.append("Create Your Own")

    answer = questionary.select(
        "Select your world:",
        choices=choices
    ).ask()

    # Handle cancellation
    if answer is None:
        return None

    # If "Create Your Own", return None (placeholder)
    if answer == "Create Your Own":
        return None

    # Find and return selected world
    for world in worlds:
        if world.name == answer:
            return world

    return None


def select_class(classes: dict[str, dict]) -> tuple[str, dict] | None:
    """
    Display class selection menu with descriptions.

    Args:
        classes: Dictionary of class presets

    Returns:
        Tuple of (class_name, class_data) or None if cancelled
    """
    # Build choices with class names
    choices = list(classes.keys())

    answer = questionary.select(
        "Select your character class:",
        choices=choices
    ).ask()

    # Handle cancellation
    if answer is None:
        return None

    # Return selected class name and its data dict
    return (answer, classes[answer])


def get_campaign_name() -> str | None:
    """
    Prompt for campaign name with validation.

    Returns:
        Campaign name string (1-100 characters) or None if cancelled
    """
    return questionary.text(
        "Enter a name for your campaign:",
        validate=lambda text: len(text) > 0 and len(text) <= 100 or "Name must be 1-100 characters"
    ).ask()


def get_character_name() -> str | None:
    """
    Prompt for character name with validation.

    Returns:
        Character name string (1-50 characters) or None if cancelled
    """
    return questionary.text(
        "Enter your character's name:",
        validate=lambda text: len(text) > 0 and len(text) <= 50 or "Name must be 1-50 characters"
    ).ask()


def get_character_description() -> str | None:
    """
    Prompt for character description/background.

    Returns:
        Character description string (1-500 characters) or None if cancelled
    """
    return questionary.text(
        "Describe your character (appearance, background, personality):",
        multiline=False,  # Set to False for better terminal compatibility
        validate=lambda text: len(text) > 0 and len(text) <= 500 or "Description must be 1-500 characters"
    ).ask()


def select_preset(presets: list[CampaignPreset]) -> CampaignPreset | None:
    """
    Display campaign preset selection menu.

    Args:
        presets: List of available campaign presets

    Returns:
        Selected CampaignPreset or None if cancelled
    """
    choices = [preset.display_name for preset in presets]

    answer = questionary.select(
        "Select a campaign preset:",
        choices=choices
    ).ask()

    if answer is None:
        return None

    # Find and return selected preset
    for preset in presets:
        if preset.display_name == answer:
            return preset

    return None


def select_class_from_preset(preset: CampaignPreset) -> tuple[str, CharacterClassPreset] | None:
    """
    Display class selection menu for a specific preset.

    Args:
        preset: The CampaignPreset containing available classes

    Returns:
        Tuple of (class_name, CharacterClassPreset) or None if cancelled
    """
    choices = list(preset.character_classes.keys())

    answer = questionary.select(
        f"Select your character class:",
        choices=choices
    ).ask()

    if answer is None:
        return None

    return (answer, preset.character_classes[answer])


def confirm_character_creation(campaign_name: str, player_name: str, class_name: str) -> bool:
    """
    Confirm character creation before saving.

    Args:
        campaign_name: Campaign name
        player_name: Character's name
        class_name: Selected class

    Returns:
        True if confirmed, False otherwise
    """
    result = questionary.confirm(
        f"Create campaign '{campaign_name}' with {player_name} the {class_name}?"
    ).ask()

    # Handle cancellation (returns None)
    return result if result is not None else False
