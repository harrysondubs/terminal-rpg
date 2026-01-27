"""
Weapon repository for Weapon entity CRUD operations.
"""

import sqlite3

from ..models import HandsRequired, Rarity, Weapon, WeaponType
from .base import BaseRepository


class WeaponRepository(BaseRepository):
    """Repository for Weapon entity CRUD operations"""

    def create(self, weapon: Weapon) -> Weapon:
        """Insert weapon, return with ID populated"""
        weapon.id = self._execute_insert(
            """INSERT INTO weapons
               (world_id, campaign_id, name, description, type, hands_required, attack, rarity, value)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                weapon.world_id,
                weapon.campaign_id,
                weapon.name,
                weapon.description,
                weapon.type.value,
                weapon.hands_required.value,
                weapon.attack,
                weapon.rarity.value,
                weapon.value,
            ),
        )
        return weapon

    def get_by_id(self, weapon_id: int) -> Weapon | None:
        """Fetch single weapon by ID"""
        row = self._fetch_by_id("weapons", weapon_id)
        return self._row_to_weapon(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: int | None = None) -> list[Weapon]:
        """Get weapons available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM weapons WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM weapons WHERE world_id = ? AND campaign_id IS NULL", (world_id,)
            ).fetchall()
        return [self._row_to_weapon(row) for row in rows]

    def update(self, weapon: Weapon) -> None:
        """Update existing weapon"""
        self.db.conn.execute(
            """UPDATE weapons SET
               world_id = ?, campaign_id = ?, name = ?, description = ?,
               type = ?, hands_required = ?, attack = ?, rarity = ?, value = ?
               WHERE id = ?""",
            (
                weapon.world_id,
                weapon.campaign_id,
                weapon.name,
                weapon.description,
                weapon.type.value,
                weapon.hands_required.value,
                weapon.attack,
                weapon.rarity.value,
                weapon.value,
                weapon.id,
            ),
        )
        self.db.conn.commit()

    def delete(self, weapon_id: int) -> None:
        """Delete weapon"""
        self._delete_by_id("weapons", weapon_id)

    def _row_to_weapon(self, row: sqlite3.Row) -> Weapon:
        """Convert database row to Weapon dataclass"""
        return Weapon(
            id=row["id"],
            world_id=row["world_id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            type=WeaponType(row["type"]),
            hands_required=HandsRequired(row["hands_required"]),
            attack=row["attack"],
            rarity=Rarity(row["rarity"]),
            value=row["value"],
        )
