"""
Core game loop - entry point for gameplay.
"""

from ..llm.game.dm_game import DMGame
from ..storage.database import Database


class GameEngine:
    """
    Main game engine that coordinates the DM and game flow.
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

    def run(self):
        """Start the game."""
        dm_game = DMGame(self.db, self.campaign_id)
        dm_game.start()
