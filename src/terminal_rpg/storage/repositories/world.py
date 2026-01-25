"""
World repository for world entity CRUD operations.
"""

import sqlite3
from typing import Optional

from .base import BaseRepository
from ..models import World, datetime_from_db


class WorldRepository(BaseRepository):
    """Repository for World entity CRUD operations"""

    def create(self, world: World) -> World:
        """Insert world, return with ID populated"""
        world.id = self._execute_insert(
            "INSERT INTO worlds (name, description) VALUES (?, ?)",
            (world.name, world.description)
        )
        world.created_at = self._fetch_timestamp('worlds', world.id)
        return world

    def get_by_id(self, world_id: int) -> Optional[World]:
        """Fetch single world by ID"""
        row = self._fetch_by_id('worlds', world_id)
        return self._row_to_world(row) if row else None

    def get_all(self) -> list[World]:
        """Fetch all worlds"""
        rows = self.db.conn.execute("SELECT * FROM worlds").fetchall()
        return [self._row_to_world(row) for row in rows]

    def update(self, world: World) -> None:
        """Update existing world"""
        self.db.conn.execute(
            "UPDATE worlds SET name = ?, description = ? WHERE id = ?",
            (world.name, world.description, world.id)
        )
        self.db.conn.commit()

    def delete(self, world_id: int) -> None:
        """Delete world (will fail if campaigns exist due to RESTRICT)"""
        self._delete_by_id('worlds', world_id)

    def _row_to_world(self, row: sqlite3.Row) -> World:
        """Convert database row to World dataclass"""
        return World(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            created_at=datetime_from_db(row['created_at'])
        )
