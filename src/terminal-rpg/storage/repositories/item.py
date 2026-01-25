"""
Item repository for Item entity CRUD operations.
"""

import sqlite3
from typing import Optional

from .base import BaseRepository
from ..models import Item, Rarity


class ItemRepository(BaseRepository):
    """Repository for Item entity CRUD operations"""

    def create(self, item: Item) -> Item:
        """Insert item, return with ID populated"""
        item.id = self._execute_insert(
            """INSERT INTO items (world_id, campaign_id, name, description, rarity, value)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (item.world_id, item.campaign_id, item.name, item.description,
             item.rarity.value, item.value)
        )
        return item

    def get_by_id(self, item_id: int) -> Optional[Item]:
        """Fetch single item by ID"""
        row = self._fetch_by_id('items', item_id)
        return self._row_to_item(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: Optional[int] = None) -> list[Item]:
        """Get items available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM items WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id)
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM items WHERE world_id = ? AND campaign_id IS NULL",
                (world_id,)
            ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def update(self, item: Item) -> None:
        """Update existing item"""
        self.db.conn.execute(
            """UPDATE items SET
               world_id = ?, campaign_id = ?, name = ?, description = ?, rarity = ?, value = ?
               WHERE id = ?""",
            (item.world_id, item.campaign_id, item.name, item.description,
             item.rarity.value, item.value, item.id)
        )
        self.db.conn.commit()

    def delete(self, item_id: int) -> None:
        """Delete item"""
        self._delete_by_id('items', item_id)

    def _row_to_item(self, row: sqlite3.Row) -> Item:
        """Convert database row to Item dataclass"""
        return Item(
            id=row['id'],
            world_id=row['world_id'],
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            rarity=Rarity(row['rarity']),
            value=row['value']
        )
