"""
NPC repository for NPC entity CRUD operations.
"""

import sqlite3

from ..models import NPC, DamageDiceSides, Disposition, datetime_from_db
from .base import BaseRepository


class NPCRepository(BaseRepository):
    """Repository for NPC entity CRUD operations"""

    def create(self, npc: NPC) -> NPC:
        """Insert NPC, return with ID populated"""
        npc.id = self._execute_insert(
            """INSERT INTO npcs
               (world_id, campaign_id, name, description, character_class, character_species,
                level, hp, max_hp, ac, attack_mod, damage_dice_count, damage_dice_sides, initiative_mod, xp, gold, disposition)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                npc.world_id,
                npc.campaign_id,
                npc.name,
                npc.description,
                npc.character_class,
                npc.character_species,
                npc.level,
                npc.hp,
                npc.max_hp,
                npc.ac,
                npc.attack_mod,
                npc.damage_dice_count,
                npc.damage_dice_sides.value,
                npc.initiative_mod,
                npc.xp,
                npc.gold,
                npc.disposition.value,
            ),
        )
        npc.created_at = self._fetch_timestamp("npcs", npc.id)
        return npc

    def get_by_id(self, npc_id: int) -> NPC | None:
        """Fetch single NPC by ID"""
        row = self._fetch_by_id("npcs", npc_id)
        return self._row_to_npc(row) if row else None

    def get_by_world(self, world_id: int, campaign_id: int | None = None) -> list[NPC]:
        """Get NPCs available in a world (optionally filtered by campaign)"""
        if campaign_id is not None:
            rows = self.db.conn.execute(
                "SELECT * FROM npcs WHERE world_id = ? AND (campaign_id IS NULL OR campaign_id = ?)",
                (world_id, campaign_id),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM npcs WHERE world_id = ? AND campaign_id IS NULL", (world_id,)
            ).fetchall()
        return [self._row_to_npc(row) for row in rows]

    def update(self, npc: NPC) -> None:
        """Update existing NPC"""
        self.db.conn.execute(
            """UPDATE npcs SET
               world_id = ?, campaign_id = ?, name = ?, description = ?, character_class = ?,
               character_species = ?, level = ?, hp = ?, max_hp = ?, ac = ?, attack_mod = ?,
               damage_dice_count = ?, damage_dice_sides = ?, initiative_mod = ?, xp = ?, gold = ?, disposition = ?
               WHERE id = ?""",
            (
                npc.world_id,
                npc.campaign_id,
                npc.name,
                npc.description,
                npc.character_class,
                npc.character_species,
                npc.level,
                npc.hp,
                npc.max_hp,
                npc.ac,
                npc.attack_mod,
                npc.damage_dice_count,
                npc.damage_dice_sides.value,
                npc.initiative_mod,
                npc.xp,
                npc.gold,
                npc.disposition.value,
                npc.id,
            ),
        )
        self.db.conn.commit()

    def delete(self, npc_id: int) -> None:
        """Delete NPC"""
        self._delete_by_id("npcs", npc_id)

    def _row_to_npc(self, row: sqlite3.Row) -> NPC:
        """Convert database row to NPC dataclass"""
        return NPC(
            id=row["id"],
            world_id=row["world_id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            character_class=row["character_class"],
            character_species=row["character_species"],
            level=row["level"],
            hp=row["hp"],
            max_hp=row["max_hp"],
            ac=row["ac"],
            attack_mod=row["attack_mod"],
            damage_dice_count=row["damage_dice_count"],
            damage_dice_sides=DamageDiceSides(row["damage_dice_sides"]),
            initiative_mod=row["initiative_mod"],
            xp=row["xp"],
            gold=row["gold"],
            disposition=Disposition(row["disposition"]),
            created_at=datetime_from_db(row["created_at"]),
        )
