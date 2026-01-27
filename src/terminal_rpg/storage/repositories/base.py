"""
Base repository with common CRUD operations to reduce code duplication.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Database

from ..models import datetime_from_db


class BaseRepository:
    """Base repository with common CRUD operations to reduce code duplication"""

    def __init__(self, db: "Database"):
        self.db = db

    def _execute_insert(self, query: str, params: tuple) -> int:
        """Execute INSERT query, return last inserted row ID"""
        cursor = self.db.conn.execute(query, params)
        self.db.conn.commit()
        return cursor.lastrowid

    def _fetch_by_id(self, table_name: str, id_value: int):
        """Fetch single row by ID, returns sqlite3.Row or None"""
        row = self.db.conn.execute(
            f"SELECT * FROM {table_name} WHERE id = ?", (id_value,)
        ).fetchone()
        return row

    def _delete_by_id(self, table_name: str, id_value: int) -> None:
        """Delete row by ID"""
        self.db.conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (id_value,))
        self.db.conn.commit()

    def _add_to_join_table(
        self,
        table_name: str,
        id_col1: str,
        id_col2: str,
        id_val1: int,
        id_val2: int,
        quantity: int = 1,
    ) -> None:
        """Add or update quantity in a join table (player_items, player_weapons, player_armor)"""
        # Check if entry exists
        existing = self.db.conn.execute(
            f"SELECT quantity FROM {table_name} WHERE {id_col1} = ? AND {id_col2} = ?",
            (id_val1, id_val2),
        ).fetchone()

        if existing:
            # Update quantity
            new_quantity = existing["quantity"] + quantity
            self.db.conn.execute(
                f"UPDATE {table_name} SET quantity = ? WHERE {id_col1} = ? AND {id_col2} = ?",
                (new_quantity, id_val1, id_val2),
            )
        else:
            # Insert new
            self.db.conn.execute(
                f"INSERT INTO {table_name} ({id_col1}, {id_col2}, quantity) VALUES (?, ?, ?)",
                (id_val1, id_val2, quantity),
            )

        self.db.conn.commit()

    def _fetch_timestamp(self, table_name: str, id_value: int, timestamp_col: str = "created_at"):
        """Fetch a timestamp column from a row"""
        row = self.db.conn.execute(
            f"SELECT {timestamp_col} FROM {table_name} WHERE id = ?", (id_value,)
        ).fetchone()
        return datetime_from_db(row[timestamp_col]) if row else None
