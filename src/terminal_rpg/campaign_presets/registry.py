"""
Registry for campaign presets.
Manages registration and discovery of available campaign presets.
"""

from .models import CampaignPreset


class PresetRegistry:
    """
    Global registry for campaign presets.
    Presets self-register on module import.
    """

    _presets: dict[str, CampaignPreset] = {}

    @classmethod
    def register(cls, preset: CampaignPreset) -> None:
        """
        Register a campaign preset for availability.

        Args:
            preset: The CampaignPreset to register

        Raises:
            ValueError: If preset ID is already registered
        """
        if preset.id in cls._presets:
            raise ValueError(f"Preset with id '{preset.id}' is already registered")

        cls._presets[preset.id] = preset

    @classmethod
    def get_all(cls) -> list[CampaignPreset]:
        """
        Get all registered campaign presets.

        Returns:
            List of all registered CampaignPreset objects
        """
        return list(cls._presets.values())

    @classmethod
    def get_by_id(cls, preset_id: str) -> CampaignPreset | None:
        """
        Get a specific preset by ID.

        Args:
            preset_id: The preset ID to look up

        Returns:
            The CampaignPreset if found, None otherwise
        """
        return cls._presets.get(preset_id)

    @classmethod
    def discover_presets(cls) -> None:
        """
        Auto-discover preset modules in the campaign_presets directory.
        This is called by importing preset modules which trigger registration.

        Note: In this implementation, presets are auto-imported via __init__.py,
        so this method is mainly for explicit re-discovery if needed.
        """
        # Presets are imported in __init__.py, so they're already registered
        # This method exists for potential future use cases
        pass
