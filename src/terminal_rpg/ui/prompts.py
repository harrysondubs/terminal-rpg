"""
Questionary interactions for user input.
"""

import questionary
from typing import Literal
from ..storage.models import World, Campaign
from ..campaign_presets import CampaignPreset, CharacterClassPreset

# Navigation constants
BACK = "← Back"
CANCEL = "✗ Cancel"


def show_start_menu() -> str:
    """
    Display main menu and return user's choice.

    Returns:
        One of: "new_game", "load_game", "leaderboard", "exit"
    """
    choices = [
        "New Game",
        "Load Game",
        "Leaderboard",
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
        "Leaderboard": "leaderboard",
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


def select_saved_campaign(campaigns_with_worlds: list[tuple[Campaign, str]]) -> Campaign | None:
    """
    Display saved campaign selection menu with campaign name, world, and last save time.

    Args:
        campaigns_with_worlds: List of (Campaign, world_name) tuples

    Returns:
        Selected Campaign object or None if cancelled
    """
    if not campaigns_with_worlds:
        return None

    # Build choices with formatted display strings
    choices = []
    for campaign, world_name in campaigns_with_worlds:
        # Format: "Campaign Name | World: Middle-earth | Last Saved: 2025-01-27 14:30"
        last_save_str = campaign.last_save_at.strftime("%Y-%m-%d %H:%M")
        choice_text = f"{campaign.name} | World: {world_name} | Last Saved: {last_save_str}"
        choices.append(choice_text)

    answer = questionary.select(
        "Select a saved game to load:",
        choices=choices
    ).ask()

    # Handle cancellation
    if answer is None:
        return None

    # Find selected campaign by matching the choice text
    selected_index = choices.index(answer)
    selected_campaign = campaigns_with_worlds[selected_index][0]

    return selected_campaign


# Navigation-aware prompts for character creation flow


def select_preset_with_nav(presets: list[CampaignPreset]) -> CampaignPreset | Literal["back", "cancel"]:
    """
    Display campaign preset selection menu with back/cancel navigation.

    Args:
        presets: List of available campaign presets

    Returns:
        Selected CampaignPreset, "back", or "cancel"
    """
    choices = [preset.display_name for preset in presets]
    choices.append(questionary.Separator())
    choices.append(CANCEL)

    answer = questionary.select(
        "Step 1/6: Select a campaign preset:",
        choices=choices
    ).ask()

    if answer is None or answer == CANCEL:
        return "cancel"

    # Find and return selected preset
    for preset in presets:
        if preset.display_name == answer:
            return preset

    return "cancel"


def select_class_from_preset_with_nav(preset: CampaignPreset) -> tuple[str, CharacterClassPreset] | Literal["back", "cancel"]:
    """
    Display class selection menu with back/cancel navigation.

    Args:
        preset: The CampaignPreset containing available classes

    Returns:
        Tuple of (class_name, CharacterClassPreset), "back", or "cancel"
    """
    choices = list(preset.character_classes.keys())
    choices.append(questionary.Separator())
    choices.extend([BACK, CANCEL])

    answer = questionary.select(
        "Step 2/6: Select your character class:",
        choices=choices
    ).ask()

    if answer is None or answer == CANCEL:
        return "cancel"
    if answer == BACK:
        return "back"

    return (answer, preset.character_classes[answer])


def get_character_name_with_nav() -> str | Literal["back", "cancel"]:
    """
    Prompt for character name with back/cancel navigation.

    Returns:
        Character name string, "back", or "cancel"
    """
    try:
        answer = questionary.text(
            "Step 3/6: Enter your character's name (1-50 characters, or '/back' to return):",
            validate=lambda text: (len(text) > 0 and len(text) <= 50) or text.lower() == '/back' or "Name must be 1-50 characters"
        ).ask()

        if answer is None:
            return "cancel"
        
        if answer.lower() == '/back':
            return "back"

        return answer
    except KeyboardInterrupt:
        return "back"


def get_campaign_name_with_nav() -> str | Literal["back", "cancel"]:
    """
    Prompt for campaign name with back/cancel navigation.

    Returns:
        Campaign name string, "back", or "cancel"
    """
    try:
        answer = questionary.text(
            "Step 4/6: Enter a name for your campaign (1-100 characters, or '/back' to return):",
            validate=lambda text: (len(text) > 0 and len(text) <= 100) or text.lower() == '/back' or "Name must be 1-100 characters"
        ).ask()

        if answer is None:
            return "cancel"
        
        if answer.lower() == '/back':
            return "back"

        return answer
    except KeyboardInterrupt:
        return "back"


def get_character_description_with_nav() -> str | Literal["back", "cancel"]:
    """
    Prompt for character description with back/cancel navigation.

    Returns:
        Character description string, "back", or "cancel"
    """
    try:
        answer = questionary.text(
            "Step 5/6: Describe your character - appearance, background, personality (1-500 characters, or '/back' to return):",
            multiline=False,
            validate=lambda text: (len(text) > 0 and len(text) <= 500) or text.lower() == '/back' or "Description must be 1-500 characters"
        ).ask()

        if answer is None:
            return "cancel"
        
        if answer.lower() == '/back':
            return "back"

        return answer
    except KeyboardInterrupt:
        return "back"


def confirm_character_creation_with_nav(
    campaign_name: str,
    player_name: str,
    class_name: str
) -> Literal["confirm", "back", "cancel"]:
    """
    Confirm character creation with back/cancel navigation.

    Args:
        campaign_name: Campaign name
        player_name: Character's name
        class_name: Selected class

    Returns:
        "confirm", "back", or "cancel"
    """
    choices = [
        "✓ Confirm and Create",
        questionary.Separator(),
        BACK,
        CANCEL
    ]

    answer = questionary.select(
        f"Step 6/6: Create campaign '{campaign_name}' with {player_name} the {class_name}?",
        choices=choices
    ).ask()

    if answer is None or answer == CANCEL:
        return "cancel"
    if answer == BACK:
        return "back"
    
    return "confirm"
