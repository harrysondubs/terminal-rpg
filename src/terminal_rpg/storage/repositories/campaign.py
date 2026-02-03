"""
Campaign repository for campaign entity CRUD operations.
"""

import sqlite3
from typing import TYPE_CHECKING

from ..models import Campaign, GameState, datetime_from_db, datetime_to_db
from .base import BaseRepository

if TYPE_CHECKING:
    pass


class CampaignRepository(BaseRepository):
    """Repository for Campaign entity CRUD operations"""

    def create(self, campaign: Campaign) -> Campaign:
        """Insert campaign, return with ID populated"""
        campaign.id = self._execute_insert(
            "INSERT INTO campaigns (name, world_id, current_location_id) VALUES (?, ?, ?)",
            (campaign.name, campaign.world_id, campaign.current_location_id),
        )
        # Fetch both timestamps
        row = self.db.conn.execute(
            "SELECT created_at, last_save_at FROM campaigns WHERE id = ?", (campaign.id,)
        ).fetchone()
        campaign.created_at = datetime_from_db(row["created_at"])
        campaign.last_save_at = datetime_from_db(row["last_save_at"])
        return campaign

    def get_by_id(self, campaign_id: int) -> Campaign | None:
        """Fetch single campaign by ID"""
        row = self._fetch_by_id("campaigns", campaign_id)
        return self._row_to_campaign(row) if row else None

    def get_by_world(self, world_id: int) -> list[Campaign]:
        """Fetch all campaigns for a world"""
        rows = self.db.conn.execute(
            "SELECT * FROM campaigns WHERE world_id = ?", (world_id,)
        ).fetchall()
        return [self._row_to_campaign(row) for row in rows]

    def update(self, campaign: Campaign) -> None:
        """Update existing campaign"""
        self.db.conn.execute(
            "UPDATE campaigns SET name = ?, world_id = ?, last_save_at = ? WHERE id = ?",
            (campaign.name, campaign.world_id, datetime_to_db(campaign.last_save_at), campaign.id),
        )
        self.db.conn.commit()

    def update_last_save(self, campaign_id: int) -> None:
        """Update last_save_at timestamp to current time"""
        self.db.conn.execute(
            "UPDATE campaigns SET last_save_at = datetime('now') WHERE id = ?", (campaign_id,)
        )
        self.db.conn.commit()

    def update_current_location(self, campaign_id: int, location_id: int) -> None:
        """Update campaign's current location"""
        self.db.conn.execute(
            "UPDATE campaigns SET current_location_id = ?, last_save_at = datetime('now') WHERE id = ?",
            (location_id, campaign_id),
        )
        self.db.conn.commit()

    def delete(self, campaign_id: int) -> None:
        """Delete campaign (cascades to all related data)"""
        self._delete_by_id("campaigns", campaign_id)

    def get_all_active_with_world_names(self) -> list[tuple[Campaign, str]]:
        """
        Fetch all campaigns with their world names for display in load menu.
        Only returns campaigns where the player's HP is greater than 0 (alive).

        Returns:
            List of tuples (Campaign, world_name) ordered by last_save_at DESC
        """
        rows = self.db.conn.execute(
            """
            SELECT c.*, w.name as world_name
            FROM campaigns c
            JOIN worlds w ON c.world_id = w.id
            JOIN players p ON c.id = p.campaign_id
            WHERE p.hp > 0
            ORDER BY c.last_save_at DESC
        """
        ).fetchall()

        result = []
        for row in rows:
            campaign = self._row_to_campaign(row)
            world_name = row["world_name"]
            result.append((campaign, world_name))

        return result

    def load_game_state(self, campaign_id: int) -> GameState | None:
        """Load complete game state for a campaign"""
        # Import here to avoid circular imports
        from .battle import BattleRepository
        from .battle_participant import BattleParticipantRepository
        from .location import LocationRepository
        from .player import PlayerRepository
        from .world import WorldRepository

        campaign = self.get_by_id(campaign_id)
        if not campaign:
            return None

        # Get related repositories
        world_repo = WorldRepository(self.db)
        player_repo = PlayerRepository(self.db)
        location_repo = LocationRepository(self.db)
        battle_repo = BattleRepository(self.db)
        participant_repo = BattleParticipantRepository(self.db)

        # Load all data
        world = world_repo.get_by_id(campaign.world_id)
        player = player_repo.get_by_campaign_id(campaign_id)

        if not player:
            return None

        # Load or set current location
        location = None
        if campaign.current_location_id:
            location = location_repo.get_by_id(campaign.current_location_id)

        # If no current location set, find "The Prancing Pony Inn" or use first location
        if not location:
            locations = location_repo.get_by_world(campaign.world_id, campaign_id=campaign_id)

            # Try to find "The Prancing Pony Inn"
            for loc in locations:
                if loc.name == "The Prancing Pony Inn":
                    location = loc
                    break

            # If not found, use first location
            if not location and locations:
                location = locations[0]

            # Update campaign with chosen location
            if location:
                self.update_current_location(campaign_id, location.id)
                campaign.current_location_id = location.id

        if not location:
            return None

        # Check for active battle
        # Find battles where the player is an active participant
        active_battle = None
        player_participants = participant_repo.get_by_player(player.id)
        for participant in player_participants:
            if participant.is_active:
                battle = battle_repo.get_by_id(participant.battle_id)
                if battle:
                    active_battle = battle
                    break  # Player should only be in one active battle at a time

        equipped_weapons = player_repo.get_equipped_weapons(player.id)
        equipped_armor = player_repo.get_equipped_armor(player.id)
        inventory_items = player_repo.get_inventory_items(player.id)
        inventory_weapons = player_repo.get_inventory_weapons(player.id)
        inventory_armor = player_repo.get_inventory_armor(player.id)

        return GameState(
            campaign=campaign,
            world=world,
            player=player,
            location=location,
            equipped_weapons=equipped_weapons,
            equipped_armor=equipped_armor,
            inventory_items=inventory_items,
            inventory_weapons=inventory_weapons,
            inventory_armor=inventory_armor,
            battle=active_battle,  # Include active battle if found
        )

    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, str, int, int, bool]]:
        """
        Get top campaigns ranked by player XP for the leaderboard.

        Args:
            limit: Maximum number of entries to return (default 10)

        Returns:
            List of tuples (campaign_name, player_name, level, xp, is_alive)
            ordered by XP descending
        """
        rows = self.db.conn.execute(
            """
            SELECT
                c.name as campaign_name,
                p.name as player_name,
                p.level,
                p.xp,
                CASE WHEN p.hp > 0 THEN 1 ELSE 0 END as is_alive
            FROM campaigns c
            JOIN players p ON c.id = p.campaign_id
            ORDER BY p.xp DESC
            LIMIT ?
        """,
            (limit,),
        ).fetchall()

        return [
            (
                row["campaign_name"],
                row["player_name"],
                row["level"],
                row["xp"],
                bool(row["is_alive"]),
            )
            for row in rows
        ]

    def _row_to_campaign(self, row: sqlite3.Row) -> Campaign:
        """Convert database row to Campaign dataclass"""
        return Campaign(
            id=row["id"],
            name=row["name"],
            world_id=row["world_id"],
            current_location_id=row["current_location_id"],
            created_at=datetime_from_db(row["created_at"]),
            last_save_at=datetime_from_db(row["last_save_at"]),
        )
