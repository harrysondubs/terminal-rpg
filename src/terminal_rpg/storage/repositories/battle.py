"""
Battle repository for Battle entity CRUD operations.
"""

import sqlite3

from ..models import Battle, datetime_from_db
from .base import BaseRepository


class BattleRepository(BaseRepository):
    """Repository for Battle entity CRUD operations"""

    def create(self, battle: Battle) -> Battle:
        """Insert battle, return with ID populated"""
        battle.id = self._execute_insert(
            """INSERT INTO battles
               (world_id, campaign_id, name, description, current_turn_index)
               VALUES (?, ?, ?, ?, ?)""",
            (
                battle.world_id,
                battle.campaign_id,
                battle.name,
                battle.description,
                battle.current_turn_index,
            ),
        )
        battle.created_at = self._fetch_timestamp("battles", battle.id)
        return battle

    def get_by_id(self, battle_id: int) -> Battle | None:
        """Fetch single battle by ID"""
        row = self._fetch_by_id("battles", battle_id)
        return self._row_to_battle(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: int | None = None) -> list[Battle]:
        """Get battles available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM battles WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM battles WHERE world_id = ? AND campaign_id IS NULL", (world_id,)
            ).fetchall()
        return [self._row_to_battle(row) for row in rows]

    def update(self, battle: Battle) -> None:
        """Update existing battle"""
        self.db.conn.execute(
            """UPDATE battles SET
               world_id = ?, campaign_id = ?, name = ?, description = ?, current_turn_index = ?
               WHERE id = ?""",
            (
                battle.world_id,
                battle.campaign_id,
                battle.name,
                battle.description,
                battle.current_turn_index,
                battle.id,
            ),
        )
        self.db.conn.commit()

    def delete(self, battle_id: int) -> None:
        """Delete battle"""
        self._delete_by_id("battles", battle_id)

    def update_turn_index(self, battle_id: int, turn_index: int) -> None:
        """
        Update the current turn index for a battle.
        Used during combat to track whose turn it is.

        Args:
            battle_id: Battle ID
            turn_index: Index of the current participant's turn
        """
        self.db.conn.execute(
            "UPDATE battles SET current_turn_index = ? WHERE id = ?",
            (turn_index, battle_id),
        )
        self.db.conn.commit()

    def _row_to_battle(self, row: sqlite3.Row) -> Battle:
        """Convert database row to Battle dataclass"""
        # Check if current_turn_index column exists (for backwards compatibility)
        try:
            current_turn_index = row["current_turn_index"]
        except (KeyError, IndexError):
            current_turn_index = 0  # Default for old databases

        return Battle(
            id=row["id"],
            world_id=row["world_id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            current_turn_index=current_turn_index,
            created_at=datetime_from_db(row["created_at"]),
        )
