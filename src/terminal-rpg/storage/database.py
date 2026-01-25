"""
SQLite database connection management and schema creation.
"""

import sqlite3
from typing import Optional


class Database:
    """
    Manages SQLite database connection and schema creation.
    """

    def __init__(self, db_path="games.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Open connection and configure SQLite"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like row access
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return self

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry"""
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic rollback on error"""
        if exc_type:
            if self.conn:
                self.conn.rollback()
        self.close()

    def create_schema(self):
        """Create all tables with proper constraints and indexes"""
        if not self.conn:
            raise RuntimeError("Database not connected. Call connect() first.")

        cursor = self.conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS worlds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                world_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                last_save_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                character_class TEXT NOT NULL,
                character_race TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                hp INTEGER NOT NULL,
                max_hp INTEGER NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                gold INTEGER NOT NULL DEFAULT 0,
                strength INTEGER NOT NULL DEFAULT 0,
                dexterity INTEGER NOT NULL DEFAULT 0,
                constitution INTEGER NOT NULL DEFAULT 0,
                intelligence INTEGER NOT NULL DEFAULT 0,
                wisdom INTEGER NOT NULL DEFAULT 0,
                charisma INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                rarity TEXT NOT NULL CHECK (rarity IN ('common', 'rare', 'legendary')),
                value INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL CHECK (type IN ('melee', 'ranged')),
                hands_required TEXT NOT NULL CHECK (hands_required IN ('one_handed', 'two_handed')),
                attack INTEGER NOT NULL,
                rarity TEXT NOT NULL CHECK (rarity IN ('common', 'rare', 'legendary')),
                value INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS armor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL CHECK (type IN ('helmet', 'shield', 'chestplate', 'boots', 'leggings')),
                defense INTEGER NOT NULL,
                rarity TEXT NOT NULL CHECK (rarity IN ('common', 'rare', 'legendary')),
                value INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_items (
                player_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                acquired_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (player_id, item_id),
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_weapons (
                player_id INTEGER NOT NULL,
                weapon_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                equipped BOOLEAN NOT NULL DEFAULT 0,
                acquired_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (player_id, weapon_id),
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_armor (
                player_id INTEGER NOT NULL,
                armor_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                equipped BOOLEAN NOT NULL DEFAULT 0,
                acquired_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (player_id, armor_id),
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                FOREIGN KEY (armor_id) REFERENCES armor(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS battles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS npcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                world_id INTEGER NOT NULL,
                campaign_id INTEGER,
                battle_id INTEGER,
                name TEXT NOT NULL,
                character_class TEXT NOT NULL,
                character_race TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                hp INTEGER NOT NULL,
                max_hp INTEGER NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                gold INTEGER NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (battle_id) REFERENCES battles(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                world_id INTEGER NOT NULL,
                location_id INTEGER NOT NULL,
                battle_id INTEGER,
                type TEXT NOT NULL CHECK (type IN ('user_message', 'assistant_message', 'tool_call', 'tool_result')),
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')) NOT NULL,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (world_id) REFERENCES worlds(id) ON DELETE RESTRICT,
                FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE RESTRICT,
                FOREIGN KEY (battle_id) REFERENCES battles(id) ON DELETE SET NULL
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_world ON campaigns(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_players_campaign ON players(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_world ON items(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_campaign ON items(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_weapons_world ON weapons(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_weapons_campaign ON weapons(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_armor_world ON armor(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_armor_campaign ON armor(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_world ON npcs(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_campaign ON npcs(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_npcs_battle ON npcs(battle_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_world ON locations(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_campaign ON locations(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_battles_world ON battles(world_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_battles_campaign ON battles(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_logs_campaign ON campaign_logs(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_logs_location ON campaign_logs(location_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_logs_battle ON campaign_logs(battle_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaign_logs_type ON campaign_logs(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_items_player ON player_items(player_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_weapons_player ON player_weapons(player_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_armor_player ON player_armor(player_id)")

        self.conn.commit()
