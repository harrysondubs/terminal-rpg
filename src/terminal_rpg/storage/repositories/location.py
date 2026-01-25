"""
Location repository for Location entity CRUD operations.
"""

import sqlite3
from typing import Optional

from .base import BaseRepository
from ..models import Location, datetime_from_db


class LocationRepository(BaseRepository):
    """Repository for Location entity CRUD operations"""

    def create(self, location: Location) -> Location:
        """Insert location, return with ID populated"""
        location.id = self._execute_insert(
            """INSERT INTO locations
               (world_id, campaign_id, name, description)
               VALUES (?, ?, ?, ?)""",
            (location.world_id, location.campaign_id, location.name, location.description)
        )
        location.created_at = self._fetch_timestamp('locations', location.id)
        return location

    def get_by_id(self, location_id: int) -> Optional[Location]:
        """Fetch single location by ID"""
        row = self._fetch_by_id('locations', location_id)
        return self._row_to_location(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: Optional[int] = None) -> list[Location]:
        """Get locations available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM locations WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id)
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM locations WHERE world_id = ? AND campaign_id IS NULL",
                (world_id,)
            ).fetchall()
        return [self._row_to_location(row) for row in rows]

    def update(self, location: Location) -> None:
        """Update existing location"""
        self.db.conn.execute(
            """UPDATE locations SET
               world_id = ?, campaign_id = ?, name = ?, description = ?
               WHERE id = ?""",
            (location.world_id, location.campaign_id, location.name, location.description, location.id)
        )
        self.db.conn.commit()

    def delete(self, location_id: int) -> None:
        """Delete location"""
        self._delete_by_id('locations', location_id)

    def _row_to_location(self, row: sqlite3.Row) -> Location:
        """Convert database row to Location dataclass"""
        return Location(
            id=row['id'],
            world_id=row['world_id'],
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            created_at=datetime_from_db(row['created_at'])
        )
