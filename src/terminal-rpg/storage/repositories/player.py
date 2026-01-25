"""
Player repository for player entity CRUD and inventory operations.
"""

import sqlite3
from typing import Optional

from .base import BaseRepository
from ..models import (
    Player, Item, Weapon, Armor,
    Rarity, WeaponType, HandsRequired, ArmorType,
    datetime_from_db
)


class PlayerRepository(BaseRepository):
    """Repository for Player entity CRUD operations"""

    def create(self, player: Player) -> Player:
        """Insert player, return with ID populated"""
        player.id = self._execute_insert(
            """INSERT INTO players
               (campaign_id, name, description, character_class, character_race,
                level, hp, max_hp, xp, gold, strength, dexterity, constitution,
                intelligence, wisdom, charisma)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (player.campaign_id, player.name, player.description,
             player.character_class, player.character_race,
             player.level, player.hp, player.max_hp, player.xp, player.gold,
             player.strength, player.dexterity, player.constitution,
             player.intelligence, player.wisdom, player.charisma)
        )
        player.created_at = self._fetch_timestamp('players', player.id)
        return player

    def get_by_id(self, player_id: int) -> Optional[Player]:
        """Fetch single player by ID"""
        row = self._fetch_by_id('players', player_id)
        return self._row_to_player(row) if row else None

    def get_by_campaign_id(self, campaign_id: int) -> Optional[Player]:
        """Fetch player for a campaign (one per campaign)"""
        row = self.db.conn.execute(
            "SELECT * FROM players WHERE campaign_id = ?", (campaign_id,)
        ).fetchone()
        return self._row_to_player(row) if row else None

    def update(self, player: Player) -> None:
        """Update existing player"""
        self.db.conn.execute(
            """UPDATE players SET
               campaign_id = ?, name = ?, description = ?, character_class = ?,
               character_race = ?, level = ?, hp = ?, max_hp = ?, xp = ?, gold = ?,
               strength = ?, dexterity = ?, constitution = ?, intelligence = ?,
               wisdom = ?, charisma = ?
               WHERE id = ?""",
            (player.campaign_id, player.name, player.description,
             player.character_class, player.character_race,
             player.level, player.hp, player.max_hp, player.xp, player.gold,
             player.strength, player.dexterity, player.constitution,
             player.intelligence, player.wisdom, player.charisma, player.id)
        )
        self.db.conn.commit()

    def delete(self, player_id: int) -> None:
        """Delete player"""
        self._delete_by_id('players', player_id)

    # Inventory management methods

    def add_item(self, player_id: int, item_id: int, quantity: int = 1) -> None:
        """Add item to player inventory or increase quantity"""
        self._add_to_join_table('player_items', 'player_id', 'item_id', player_id, item_id, quantity)

    def add_weapon(self, player_id: int, weapon_id: int, quantity: int = 1) -> None:
        """Add weapon to player inventory or increase quantity"""
        self._add_to_join_table('player_weapons', 'player_id', 'weapon_id', player_id, weapon_id, quantity)

    def add_armor(self, player_id: int, armor_id: int, quantity: int = 1) -> None:
        """Add armor to player inventory or increase quantity"""
        self._add_to_join_table('player_armor', 'player_id', 'armor_id', player_id, armor_id, quantity)

    def equip_weapon(self, player_id: int, weapon_id: int) -> None:
        """Equip a weapon (sets equipped = True)"""
        self.db.conn.execute(
            "UPDATE player_weapons SET equipped = 1 WHERE player_id = ? AND weapon_id = ?",
            (player_id, weapon_id)
        )
        self.db.conn.commit()

    def unequip_weapon(self, player_id: int, weapon_id: int) -> None:
        """Unequip a weapon (sets equipped = False)"""
        self.db.conn.execute(
            "UPDATE player_weapons SET equipped = 0 WHERE player_id = ? AND weapon_id = ?",
            (player_id, weapon_id)
        )
        self.db.conn.commit()

    def equip_armor(self, player_id: int, armor_id: int) -> None:
        """Equip an armor piece (sets equipped = True)"""
        self.db.conn.execute(
            "UPDATE player_armor SET equipped = 1 WHERE player_id = ? AND armor_id = ?",
            (player_id, armor_id)
        )
        self.db.conn.commit()

    def unequip_armor(self, player_id: int, armor_id: int) -> None:
        """Unequip an armor piece (sets equipped = False)"""
        self.db.conn.execute(
            "UPDATE player_armor SET equipped = 0 WHERE player_id = ? AND armor_id = ?",
            (player_id, armor_id)
        )
        self.db.conn.commit()

    def get_equipped_weapons(self, player_id: int) -> list[Weapon]:
        """Get all equipped weapons for player"""
        rows = self.db.conn.execute(
            """SELECT w.* FROM weapons w
               JOIN player_weapons pw ON w.id = pw.weapon_id
               WHERE pw.player_id = ? AND pw.equipped = 1""",
            (player_id,)
        ).fetchall()
        return [self._row_to_weapon(row) for row in rows]

    def get_equipped_armor(self, player_id: int) -> list[Armor]:
        """Get all equipped armor for player"""
        rows = self.db.conn.execute(
            """SELECT a.* FROM armor a
               JOIN player_armor pa ON a.id = pa.armor_id
               WHERE pa.player_id = ? AND pa.equipped = 1""",
            (player_id,)
        ).fetchall()
        return [self._row_to_armor(row) for row in rows]

    def get_inventory_items(self, player_id: int) -> list[tuple[Item, int]]:
        """Get all items in player inventory with quantities"""
        rows = self.db.conn.execute(
            """SELECT i.*, pi.quantity FROM items i
               JOIN player_items pi ON i.id = pi.item_id
               WHERE pi.player_id = ?""",
            (player_id,)
        ).fetchall()
        return [(self._row_to_item(row), row['quantity']) for row in rows]

    def get_inventory_weapons(self, player_id: int) -> list[tuple[Weapon, int]]:
        """Get all weapons in player inventory with quantities (includes equipped)"""
        rows = self.db.conn.execute(
            """SELECT w.*, pw.quantity FROM weapons w
               JOIN player_weapons pw ON w.id = pw.weapon_id
               WHERE pw.player_id = ?""",
            (player_id,)
        ).fetchall()
        return [(self._row_to_weapon(row), row['quantity']) for row in rows]

    def get_inventory_armor(self, player_id: int) -> list[tuple[Armor, int]]:
        """Get all armor in player inventory with quantities (includes equipped)"""
        rows = self.db.conn.execute(
            """SELECT a.*, pa.quantity FROM armor a
               JOIN player_armor pa ON a.id = pa.armor_id
               WHERE pa.player_id = ?""",
            (player_id,)
        ).fetchall()
        return [(self._row_to_armor(row), row['quantity']) for row in rows]

    def _row_to_player(self, row: sqlite3.Row) -> Player:
        """Convert database row to Player dataclass"""
        return Player(
            id=row['id'],
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            character_class=row['character_class'],
            character_race=row['character_race'],
            level=row['level'],
            hp=row['hp'],
            max_hp=row['max_hp'],
            xp=row['xp'],
            gold=row['gold'],
            strength=row['strength'],
            dexterity=row['dexterity'],
            constitution=row['constitution'],
            intelligence=row['intelligence'],
            wisdom=row['wisdom'],
            charisma=row['charisma'],
            created_at=datetime_from_db(row['created_at'])
        )

    def _row_to_weapon(self, row: sqlite3.Row) -> Weapon:
        """Convert database row to Weapon dataclass"""
        return Weapon(
            id=row['id'],
            world_id=row['world_id'],
            campaign_id=row['campaign_id'],
            name=row['name'],
            description=row['description'],
            type=WeaponType(row['type']),
            hands_required=HandsRequired(row['hands_required']),
            attack=row['attack'],
            rarity=Rarity(row['rarity']),
            value=row['value']
        )

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
