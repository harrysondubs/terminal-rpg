"""
Battle participant repository for BattleParticipant entity CRUD operations.
"""

import sqlite3

from ..models import BattleParticipant, datetime_from_db
from .base import BaseRepository


class BattleParticipantRepository(BaseRepository):
    """Repository for BattleParticipant entity CRUD operations"""

    def add_participant(
        self,
        battle_id: int,
        npc_id: int | None = None,
        player_id: int | None = None,
        turn_order: int | None = None,
        is_active: bool = True,
        initiative_roll: int | None = None,
    ) -> BattleParticipant:
        """Add a participant to a battle"""
        if (npc_id is None and player_id is None) or (npc_id is not None and player_id is not None):
            raise ValueError("Exactly one of npc_id or player_id must be provided")

        self.db.conn.execute(
            """INSERT INTO battle_participants
               (battle_id, npc_id, player_id, turn_order, is_active, initiative_roll)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (battle_id, npc_id, player_id, turn_order, is_active, initiative_roll),
        )
        self.db.conn.commit()

        # Fetch the created participant
        row = self.db.conn.execute(
            """SELECT * FROM battle_participants
               WHERE battle_id = ? AND npc_id IS ? AND player_id IS ?""",
            (battle_id, npc_id, player_id),
        ).fetchone()

        return self._row_to_participant(row)

    def get_by_battle(self, battle_id: int) -> list[BattleParticipant]:
        """Get all participants in a battle, ordered by turn_order"""
        rows = self.db.conn.execute(
            """SELECT * FROM battle_participants
               WHERE battle_id = ?
               ORDER BY turn_order ASC NULLS LAST, created_at ASC""",
            (battle_id,),
        ).fetchall()
        return [self._row_to_participant(row) for row in rows]

    def get_by_npc(self, npc_id: int) -> list[BattleParticipant]:
        """Get all battle participations for an NPC"""
        rows = self.db.conn.execute(
            "SELECT * FROM battle_participants WHERE npc_id = ?", (npc_id,)
        ).fetchall()
        return [self._row_to_participant(row) for row in rows]

    def get_by_player(self, player_id: int) -> list[BattleParticipant]:
        """Get all battle participations for a player"""
        rows = self.db.conn.execute(
            "SELECT * FROM battle_participants WHERE player_id = ?", (player_id,)
        ).fetchall()
        return [self._row_to_participant(row) for row in rows]

    def get_by_battle_and_participant(
        self, battle_id: int, npc_id: int | None = None, player_id: int | None = None
    ) -> BattleParticipant | None:
        """Get a specific participant in a battle"""
        if npc_id is not None:
            row = self.db.conn.execute(
                """SELECT * FROM battle_participants
                   WHERE battle_id = ? AND npc_id = ?""",
                (battle_id, npc_id),
            ).fetchone()
        elif player_id is not None:
            row = self.db.conn.execute(
                """SELECT * FROM battle_participants
                   WHERE battle_id = ? AND player_id = ?""",
                (battle_id, player_id),
            ).fetchone()
        else:
            return None

        return self._row_to_participant(row) if row else None

    def update_turn_order(
        self, battle_id: int, npc_id: int | None, player_id: int | None, turn_order: int
    ) -> None:
        """Update the turn order for a participant"""
        if npc_id is not None:
            self.db.conn.execute(
                """UPDATE battle_participants SET turn_order = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND npc_id = ?""",
                (turn_order, battle_id, npc_id),
            )
        else:
            self.db.conn.execute(
                """UPDATE battle_participants SET turn_order = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND player_id = ?""",
                (turn_order, battle_id, player_id),
            )
        self.db.conn.commit()

    def update_initiative(
        self, battle_id: int, npc_id: int | None, player_id: int | None, initiative_roll: int
    ) -> None:
        """Update the initiative roll for a participant"""
        if npc_id is not None:
            self.db.conn.execute(
                """UPDATE battle_participants SET initiative_roll = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND npc_id = ?""",
                (initiative_roll, battle_id, npc_id),
            )
        else:
            self.db.conn.execute(
                """UPDATE battle_participants SET initiative_roll = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND player_id = ?""",
                (initiative_roll, battle_id, player_id),
            )
        self.db.conn.commit()

    def update_is_active(
        self, battle_id: int, npc_id: int | None, player_id: int | None, is_active: bool
    ) -> None:
        """Update whether a participant is still active in battle"""
        if npc_id is not None:
            self.db.conn.execute(
                """UPDATE battle_participants SET is_active = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND npc_id = ?""",
                (is_active, battle_id, npc_id),
            )
        else:
            self.db.conn.execute(
                """UPDATE battle_participants SET is_active = ?, updated_at = datetime('now')
                   WHERE battle_id = ? AND player_id = ?""",
                (is_active, battle_id, player_id),
            )
        self.db.conn.commit()

    def remove_participant(
        self, battle_id: int, npc_id: int | None = None, player_id: int | None = None
    ) -> None:
        """Remove a participant from a battle"""
        if npc_id is not None:
            self.db.conn.execute(
                "DELETE FROM battle_participants WHERE battle_id = ? AND npc_id = ?",
                (battle_id, npc_id),
            )
        else:
            self.db.conn.execute(
                "DELETE FROM battle_participants WHERE battle_id = ? AND player_id = ?",
                (battle_id, player_id),
            )
        self.db.conn.commit()

    def remove_all_by_battle(self, battle_id: int) -> None:
        """Remove all participants from a battle"""
        self.db.conn.execute("DELETE FROM battle_participants WHERE battle_id = ?", (battle_id,))
        self.db.conn.commit()

    def _row_to_participant(self, row: sqlite3.Row) -> BattleParticipant:
        """Convert database row to BattleParticipant dataclass"""
        return BattleParticipant(
            battle_id=row["battle_id"],
            npc_id=row["npc_id"],
            player_id=row["player_id"],
            turn_order=row["turn_order"],
            is_active=bool(row["is_active"]),
            initiative_roll=row["initiative_roll"],
            created_at=datetime_from_db(row["created_at"]),
            updated_at=datetime_from_db(row["updated_at"]),
        )
