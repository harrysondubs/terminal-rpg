"""
Campaign repository for campaign entity CRUD operations.
"""

import sqlite3
from typing import Optional, TYPE_CHECKING

from .base import BaseRepository
from ..models import Campaign, GameState, datetime_from_db, datetime_to_db

if TYPE_CHECKING:
    from .world import WorldRepository
    from .player import PlayerRepository


class CampaignRepository(BaseRepository):
    """Repository for Campaign entity CRUD operations"""

    def create(self, campaign: Campaign) -> Campaign:
        """Insert campaign, return with ID populated"""
        campaign.id = self._execute_insert(
            "INSERT INTO campaigns (name, world_id) VALUES (?, ?)",
            (campaign.name, campaign.world_id)
        )
        # Fetch both timestamps
        row = self.db.conn.execute(
            "SELECT created_at, last_save_at FROM campaigns WHERE id = ?", (campaign.id,)
        ).fetchone()
        campaign.created_at = datetime_from_db(row['created_at'])
        campaign.last_save_at = datetime_from_db(row['last_save_at'])
        return campaign

    def get_by_id(self, campaign_id: int) -> Optional[Campaign]:
        """Fetch single campaign by ID"""
        row = self._fetch_by_id('campaigns', campaign_id)
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
            (campaign.name, campaign.world_id, datetime_to_db(campaign.last_save_at), campaign.id)
        )
        self.db.conn.commit()

    def update_last_save(self, campaign_id: int) -> None:
        """Update last_save_at timestamp to current time"""
        self.db.conn.execute(
            "UPDATE campaigns SET last_save_at = datetime('now') WHERE id = ?",
            (campaign_id,)
        )
        self.db.conn.commit()

    def delete(self, campaign_id: int) -> None:
        """Delete campaign (cascades to all related data)"""
        self._delete_by_id('campaigns', campaign_id)

    def load_game_state(self, campaign_id: int) -> Optional[GameState]:
        """Load complete game state for a campaign"""
        # Import here to avoid circular imports
        from .world import WorldRepository
        from .player import PlayerRepository

        campaign = self.get_by_id(campaign_id)
        if not campaign:
            return None

        # Get related repositories
        world_repo = WorldRepository(self.db)
        player_repo = PlayerRepository(self.db)

        # Load all data
        world = world_repo.get_by_id(campaign.world_id)
        player = player_repo.get_by_campaign_id(campaign_id)

        if not player:
            return None

        equipped_weapons = player_repo.get_equipped_weapons(player.id)
        equipped_armor = player_repo.get_equipped_armor(player.id)
        inventory_items = player_repo.get_inventory_items(player.id)
        inventory_weapons = player_repo.get_inventory_weapons(player.id)
        inventory_armor = player_repo.get_inventory_armor(player.id)

        return GameState(
            campaign=campaign,
            world=world,
            player=player,
            equipped_weapons=equipped_weapons,
            equipped_armor=equipped_armor,
            inventory_items=inventory_items,
            inventory_weapons=inventory_weapons,
            inventory_armor=inventory_armor
        )

    def _row_to_campaign(self, row: sqlite3.Row) -> Campaign:
        """Convert database row to Campaign dataclass"""
        return Campaign(
            id=row['id'],
            name=row['name'],
            world_id=row['world_id'],
            created_at=datetime_from_db(row['created_at']),
            last_save_at=datetime_from_db(row['last_save_at'])
        )
