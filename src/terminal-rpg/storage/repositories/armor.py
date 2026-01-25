"""
Armor repository for Armor entity CRUD operations.
"""

import sqlite3
from typing import Optional

from .base import BaseRepository
from ..models import Armor, Rarity, ArmorType


class ArmorRepository(BaseRepository):
    """Repository for Armor entity CRUD operations"""

    def create(self, armor: Armor) -> Armor:
        """Insert armor, return with ID populated"""
        armor.id = self._execute_insert(
            """INSERT INTO armor
               (world_id, campaign_id, name, description, type, defense, rarity, value)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (armor.world_id, armor.campaign_id, armor.name, armor.description,
             armor.type.value, armor.defense, armor.rarity.value, armor.value)
        )
        return armor

    def get_by_id(self, armor_id: int) -> Optional[Armor]:
        """Fetch single armor by ID"""
        row = self._fetch_by_id('armor', armor_id)
        return self._row_to_armor(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: Optional[int] = None) -> list[Armor]:
        """Get armor available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM armor WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id)
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM armor WHERE world_id = ? AND campaign_id IS NULL",
                (world_id,)
            ).fetchall()
        return [self._row_to_armor(row) for row in rows]

    def update(self, armor: Armor) -> None:
        """Update existing armor"""
        self.db.conn.execute(
            """UPDATE armor SET
               world_id = ?, campaign_id = ?, name = ?, description = ?,
               type = ?, defense = ?, rarity = ?, value = ?
               WHERE id = ?""",
            (armor.world_id, armor.campaign_id, armor.name, armor.description,
             armor.type.value, armor.defense, armor.rarity.value, armor.value, armor.id)
        )
        self.db.conn.commit()

    def delete(self, armor_id: int) -> None:
        """Delete armor"""
        self._delete_by_id('armor', armor_id)

    def _row_to_armor(self, row: sqlite3.Row) -> Armor:
        """Convert database row to Armor dataclass"""
        return Armor(
            id=row['id'],
            world_id=row['world_id'],
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            type=ArmorType(row['type']),
            defense=row['defense'],
            rarity=Rarity(row['rarity']),
            value=row['value']
        )
