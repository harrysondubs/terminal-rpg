"""
CampaignLog repository for CampaignLog entity CRUD operations.
"""

import sqlite3

from ..models import CampaignLog, LogType, datetime_from_db
from .base import BaseRepository


class CampaignLogRepository(BaseRepository):
    """Repository for CampaignLog entity CRUD operations"""

    def create(self, log: CampaignLog) -> CampaignLog:
        """Insert campaign log entry, return with ID populated"""
        log.id = self._execute_insert(
            """INSERT INTO campaign_logs
               (campaign_id, world_id, location_id, battle_id, type, content)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                log.campaign_id,
                log.world_id,
                log.location_id,
                log.battle_id,
                log.type.value,
                log.content,
            ),
        )
        log.created_at = self._fetch_timestamp("campaign_logs", log.id)
        return log

    def get_by_id(self, log_id: int) -> CampaignLog | None:
        """Fetch single campaign log entry by ID"""
        row = self._fetch_by_id("campaign_logs", log_id)
        return self._row_to_log(row) if row else None

    def get_by_campaign(self, campaign_id: int, limit: int | None = None) -> list[CampaignLog]:
        """Get all logs for a campaign, optionally limited to most recent N entries"""
        if limit:
            rows = self.db.conn.execute(
                "SELECT * FROM campaign_logs WHERE campaign_id = ? ORDER BY created_at DESC LIMIT ?",
                (campaign_id, limit),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM campaign_logs WHERE campaign_id = ? ORDER BY created_at DESC",
                (campaign_id,),
            ).fetchall()
        return [self._row_to_log(row) for row in rows]

    def get_by_location(self, location_id: int) -> list[CampaignLog]:
        """Get all logs for a specific location"""
        rows = self.db.conn.execute(
            "SELECT * FROM campaign_logs WHERE location_id = ? ORDER BY created_at DESC",
            (location_id,),
        ).fetchall()
        return [self._row_to_log(row) for row in rows]

    def get_by_battle(self, battle_id: int) -> list[CampaignLog]:
        """Get all logs for a specific battle"""
        rows = self.db.conn.execute(
            "SELECT * FROM campaign_logs WHERE battle_id = ? ORDER BY created_at DESC", (battle_id,)
        ).fetchall()
        return [self._row_to_log(row) for row in rows]

    def get_by_type(self, campaign_id: int, log_type: LogType) -> list[CampaignLog]:
        """Get all logs of a specific type for a campaign"""
        rows = self.db.conn.execute(
            "SELECT * FROM campaign_logs WHERE campaign_id = ? AND type = ? ORDER BY created_at DESC",
            (campaign_id, log_type.value),
        ).fetchall()
        return [self._row_to_log(row) for row in rows]

    def delete(self, log_id: int) -> None:
        """Delete campaign log entry"""
        self._delete_by_id("campaign_logs", log_id)

    def delete_by_campaign(self, campaign_id: int) -> None:
        """Delete all logs for a campaign"""
        self.db.conn.execute("DELETE FROM campaign_logs WHERE campaign_id = ?", (campaign_id,))
        self.db.conn.commit()

    def _row_to_log(self, row: sqlite3.Row) -> CampaignLog:
        """Convert database row to CampaignLog dataclass"""
        return CampaignLog(
            id=row["id"],
            campaign_id=row["campaign_id"],
            world_id=row["world_id"],
            location_id=row["location_id"],
            battle_id=row["battle_id"],
            type=LogType(row["type"]),
            content=row["content"],
            created_at=datetime_from_db(row["created_at"]),
        )
