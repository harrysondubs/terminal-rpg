"""
Core game loop - entry point for gameplay.
Orchestrates the game session by coordinating UI, API, and game state.
"""

import logging

from ..engines.xp_utils import calculate_hp_increase
from ..llm.game.dm_game import DMGame
from ..storage.database import Database
from ..storage.repositories import CampaignLogRepository, CampaignRepository, PlayerRepository
from ..ui.game_display import GameDisplay

logger = logging.getLogger(__name__)


class GameEngine:
    """
    Main game engine that coordinates the DM API, UI display, and game flow.
    Acts as the orchestrator between the three layers: UI, API/LLM, and Storage.
    """

    def __init__(self, db: Database, campaign_id: int):
        """
        Initialize game engine.

        Args:
            db: Connected Database instance
            campaign_id: Campaign to load
        """
        self.db = db
        self.campaign_id = campaign_id
        self.dm_api = DMGame(db, campaign_id)
        self.display = GameDisplay()
        self.game_state = None
        self.running = False

    def run(self):
        """Start the game loop."""
        # Load game state
        campaign_repo = CampaignRepository(self.db)
        self.game_state = campaign_repo.load_game_state(self.campaign_id)

        if not self.game_state:
            self.display.display_error("Error: Could not load game state", is_critical=True)
            return

        # Determine if this is a new or loaded game
        log_repo = CampaignLogRepository(self.db)
        existing_logs = log_repo.get_by_campaign(self.campaign_id, limit=1)
        is_new_game = not existing_logs

        # Display welcome
        self.display.display_welcome(self.game_state, is_new_game=is_new_game)

        # Main loop
        self.running = True
        while self.running:
            try:
                self._game_loop_iteration()
            except KeyboardInterrupt:
                self._handle_pause()
            except Exception as e:
                logger.error(f"Error in game loop: {e}", exc_info=True)
                self.display.display_error(f"Error: {e}")
                self.display.display_continue_message()

    def _game_loop_iteration(self):
        """Single iteration of game loop: get input, process, display response."""
        # Check for pending level-up before getting user input
        if self.game_state.pending_level_up:
            self._handle_level_up()

        # Get user input
        user_input = self.display.get_user_input()

        if not user_input:
            return

        # Route command
        if self._handle_command(user_input):
            return  # Command was handled, continue loop

        # Get response from DM API
        # Note: We start the spinner here, but tools may need to pause it for interactivity
        status = self.display.display_thinking_status()
        status.__enter__()

        try:
            response_text, error = self.dm_api.get_response(user_input, self.game_state, status)
        finally:
            status.__exit__(None, None, None)

        # Handle API errors
        if error:
            self.display.display_api_error(error)
            self.display.display_dm_response(
                "I apologize, but I'm having trouble connecting right now. Please try again."
            )
            return

        # Display response
        self.display.display_dm_response(response_text)

    def _handle_command(self, user_input: str) -> bool:
        """
        Handle special commands (quit, inventory, stats, etc.).

        Args:
            user_input: User's input string

        Returns:
            True if command was handled, False if input should be sent to DM
        """
        command = user_input.lower()

        # Quit commands
        if command in ["/quit", "/exit"]:
            self.running = False
            self.display.display_farewell(self.game_state.player.name)
            return True

        # Inventory commands
        if command in ["/inventory", "/i"]:
            self.display.display_inventory(self.game_state)
            return True

        # Stats commands
        if command in ["/stats", "/s"]:
            self.display.display_stats(self.game_state)
            return True

        # Not a command, let DM handle it
        return False

    def _handle_pause(self):
        """Handle game pause (Ctrl+C)."""
        self.display.display_pause_message()
        user_input = self.display.get_user_input().strip().lower()
        if user_input in ["/quit", "/exit"]:
            self.running = False

    def _handle_level_up(self):
        """
        Handle level-up flow: ability selection and stat increases.
        Called when game_state.pending_level_up is True.
        """
        player = self.game_state.player
        new_level = player.level

        # Display level-up UI and get ability choice
        chosen_ability = self.display.display_level_up(player, new_level)

        # Get old ability value
        old_value = getattr(player, chosen_ability)
        new_value = old_value + 1

        # Calculate HP increase based on constitution
        # If constitution was increased, use the new value for calculation
        constitution = player.constitution
        if chosen_ability == "constitution":
            constitution = new_value

        hp_increase = calculate_hp_increase(constitution)

        # Update ability score in game state
        setattr(player, chosen_ability, new_value)

        # Update max HP and current HP (heal by increase amount)
        old_max_hp = player.max_hp
        new_max_hp = old_max_hp + hp_increase
        player.max_hp = new_max_hp
        player.hp = min(player.hp + hp_increase, new_max_hp)  # Heal but don't exceed max

        # Persist changes to database
        player_repo = PlayerRepository(self.db)
        player_repo.update_ability_score(player.id, chosen_ability, new_value)
        player_repo.update_max_hp(player.id, new_max_hp)
        player_repo.update_hp(player.id, player.hp)

        # Display summary
        from ..engines.utils import calculate_ability_modifier

        new_modifier = calculate_ability_modifier(new_value)
        modifier_str = f"+{new_modifier}" if new_modifier >= 0 else str(new_modifier)

        summary = f"""[bold green]Level Up Complete![/bold green]

[bold]New Level:[/bold] {new_level}

[bold cyan]{chosen_ability.capitalize()}:[/bold cyan] {old_value} → [green]{new_value}[/green] (modifier: {modifier_str})

[bold red]Max HP:[/bold red] {old_max_hp} → [green]{new_max_hp}[/green] (+{hp_increase})
[bold red]Current HP:[/bold red] {player.hp}"""

        from rich.panel import Panel

        self.display.console.print()
        self.display.console.print(
            Panel(summary, border_style="green", title="✨ Character Improvement ✨")
        )
        self.display.console.print()

        # Clear the level-up flag
        self.game_state.pending_level_up = False
