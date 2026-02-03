"""
Player repository for player entity CRUD and inventory operations.
"""

import sqlite3

from ..models import (
    Armor,
    ArmorType,
    DamageDiceSides,
    EquipmentSlotError,
    HandsRequired,
    Item,
    Player,
    Rarity,
    Weapon,
    WeaponType,
    datetime_from_db,
)
from .base import BaseRepository


class PlayerRepository(BaseRepository):
    """Repository for Player entity CRUD operations"""

    def create(self, player: Player) -> Player:
        """Insert player, return with ID populated"""
        player.id = self._execute_insert(
            """INSERT INTO players
               (campaign_id, name, description, character_class, character_species,
                level, hp, max_hp, xp, gold, strength, dexterity, constitution,
                intelligence, wisdom, charisma)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                player.campaign_id,
                player.name,
                player.description,
                player.character_class,
                player.character_species,
                player.level,
                player.hp,
                player.max_hp,
                player.xp,
                player.gold,
                player.strength,
                player.dexterity,
                player.constitution,
                player.intelligence,
                player.wisdom,
                player.charisma,
            ),
        )
        player.created_at = self._fetch_timestamp("players", player.id)
        return player

    def get_by_id(self, player_id: int) -> Player | None:
        """Fetch single player by ID"""
        row = self._fetch_by_id("players", player_id)
        return self._row_to_player(row) if row else None

    def get_by_campaign_id(self, campaign_id: int) -> Player | None:
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
               character_species = ?, level = ?, hp = ?, max_hp = ?, xp = ?, gold = ?,
               strength = ?, dexterity = ?, constitution = ?, intelligence = ?,
               wisdom = ?, charisma = ?
               WHERE id = ?""",
            (
                player.campaign_id,
                player.name,
                player.description,
                player.character_class,
                player.character_species,
                player.level,
                player.hp,
                player.max_hp,
                player.xp,
                player.gold,
                player.strength,
                player.dexterity,
                player.constitution,
                player.intelligence,
                player.wisdom,
                player.charisma,
                player.id,
            ),
        )
        self.db.conn.commit()

    def delete(self, player_id: int) -> None:
        """Delete player"""
        self._delete_by_id("players", player_id)

    def update_gold(self, player_id: int, gold: int) -> None:
        """Update player's gold amount"""
        self.db.conn.execute("UPDATE players SET gold = ? WHERE id = ?", (gold, player_id))
        self.db.conn.commit()

    def update_hp(self, player_id: int, hp: int) -> None:
        """Update player's current HP"""
        self.db.conn.execute("UPDATE players SET hp = ? WHERE id = ?", (hp, player_id))
        self.db.conn.commit()

    def update_xp_and_level(self, player_id: int, xp: int, level: int) -> None:
        """Update player's XP and level atomically"""
        self.db.conn.execute(
            "UPDATE players SET xp = ?, level = ? WHERE id = ?", (xp, level, player_id)
        )
        self.db.conn.commit()

    def update_ability_score(self, player_id: int, ability: str, new_value: int) -> None:
        """Update a specific ability score"""
        valid_abilities = [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]
        if ability not in valid_abilities:
            raise ValueError(f"Invalid ability: {ability}. Must be one of {valid_abilities}")

        self.db.conn.execute(
            f"UPDATE players SET {ability} = ? WHERE id = ?", (new_value, player_id)
        )
        self.db.conn.commit()

    def update_max_hp(self, player_id: int, max_hp: int) -> None:
        """Update player's maximum HP"""
        self.db.conn.execute("UPDATE players SET max_hp = ? WHERE id = ?", (max_hp, player_id))
        self.db.conn.commit()

    # Inventory management methods

    def add_item(self, player_id: int, item_id: int, quantity: int = 1) -> None:
        """Add item to player inventory or increase quantity"""
        self._add_to_join_table(
            "player_items", "player_id", "item_id", player_id, item_id, quantity
        )

    def add_weapon(self, player_id: int, weapon_id: int, quantity: int = 1) -> None:
        """Add weapon to player inventory or increase quantity"""
        self._add_to_join_table(
            "player_weapons", "player_id", "weapon_id", player_id, weapon_id, quantity
        )

    def add_armor(self, player_id: int, armor_id: int, quantity: int = 1) -> None:
        """Add armor to player inventory or increase quantity"""
        self._add_to_join_table(
            "player_armor", "player_id", "armor_id", player_id, armor_id, quantity
        )

    def equip_weapon(self, player_id: int, weapon_id: int) -> None:
        """
        Equip a weapon (sets equipped = True).

        Validates hand slot constraints:
        - One two-handed weapon OR
        - Two one-handed weapons OR
        - One one-handed weapon + one shield

        Raises:
            EquipmentSlotError: If equipping would violate hand slot constraints
        """
        # Get the weapon to equip
        weapon_row = self.db.conn.execute(
            "SELECT * FROM weapons WHERE id = ?", (weapon_id,)
        ).fetchone()
        if not weapon_row:
            raise ValueError(f"Weapon with id {weapon_id} not found")
        weapon_to_equip = self._row_to_weapon(weapon_row)

        # Validate equipment slots
        self._validate_weapon_slots(player_id, weapon_to_equip)

        # Equip the weapon
        self.db.conn.execute(
            "UPDATE player_weapons SET equipped = 1 WHERE player_id = ? AND weapon_id = ?",
            (player_id, weapon_id),
        )
        self.db.conn.commit()

    def unequip_weapon(self, player_id: int, weapon_id: int) -> None:
        """Unequip a weapon (sets equipped = False)"""
        self.db.conn.execute(
            "UPDATE player_weapons SET equipped = 0 WHERE player_id = ? AND weapon_id = ?",
            (player_id, weapon_id),
        )
        self.db.conn.commit()

    def equip_armor(self, player_id: int, armor_id: int) -> None:
        """
        Equip an armor piece (sets equipped = True).

        For shields, validates hand slot constraints with equipped weapons.

        Raises:
            EquipmentSlotError: If equipping a shield would violate hand slot constraints
        """
        # Get the armor to equip
        armor_row = self.db.conn.execute("SELECT * FROM armor WHERE id = ?", (armor_id,)).fetchone()
        if not armor_row:
            raise ValueError(f"Armor with id {armor_id} not found")
        armor_to_equip = self._row_to_armor(armor_row)

        # Only validate slots if it's a shield
        if armor_to_equip.type == ArmorType.SHIELD:
            self._validate_shield_slots(player_id)

        # Equip the armor
        self.db.conn.execute(
            "UPDATE player_armor SET equipped = 1 WHERE player_id = ? AND armor_id = ?",
            (player_id, armor_id),
        )
        self.db.conn.commit()

    def unequip_armor(self, player_id: int, armor_id: int) -> None:
        """Unequip an armor piece (sets equipped = False)"""
        self.db.conn.execute(
            "UPDATE player_armor SET equipped = 0 WHERE player_id = ? AND armor_id = ?",
            (player_id, armor_id),
        )
        self.db.conn.commit()

    def unequip_all_weapons(self, player_id: int) -> None:
        """Unequip all weapons for a player"""
        self.db.conn.execute(
            "UPDATE player_weapons SET equipped = 0 WHERE player_id = ?",
            (player_id,),
        )
        self.db.conn.commit()

    def unequip_all_shields(self, player_id: int) -> None:
        """Unequip all shields for a player"""
        self.db.conn.execute(
            """UPDATE player_armor SET equipped = 0
               WHERE player_id = ? AND armor_id IN (
                   SELECT id FROM armor WHERE type = 'shield'
               )""",
            (player_id,),
        )
        self.db.conn.commit()

    def get_equipped_weapons(self, player_id: int) -> list[Weapon]:
        """Get all equipped weapons for player"""
        rows = self.db.conn.execute(
            """SELECT w.* FROM weapons w
               JOIN player_weapons pw ON w.id = pw.weapon_id
               WHERE pw.player_id = ? AND pw.equipped = 1""",
            (player_id,),
        ).fetchall()
        return [self._row_to_weapon(row) for row in rows]

    def get_equipped_armor(self, player_id: int) -> list[Armor]:
        """Get all equipped armor for player"""
        rows = self.db.conn.execute(
            """SELECT a.* FROM armor a
               JOIN player_armor pa ON a.id = pa.armor_id
               WHERE pa.player_id = ? AND pa.equipped = 1""",
            (player_id,),
        ).fetchall()
        return [self._row_to_armor(row) for row in rows]

    def get_inventory_items(self, player_id: int) -> list[tuple[Item, int]]:
        """Get all items in player inventory with quantities"""
        rows = self.db.conn.execute(
            """SELECT i.*, pi.quantity FROM items i
               JOIN player_items pi ON i.id = pi.item_id
               WHERE pi.player_id = ?""",
            (player_id,),
        ).fetchall()
        return [(self._row_to_item(row), row["quantity"]) for row in rows]

    def get_inventory_weapons(self, player_id: int) -> list[tuple[Weapon, int]]:
        """Get all weapons in player inventory with quantities (includes equipped)"""
        rows = self.db.conn.execute(
            """SELECT w.*, pw.quantity FROM weapons w
               JOIN player_weapons pw ON w.id = pw.weapon_id
               WHERE pw.player_id = ?""",
            (player_id,),
        ).fetchall()
        return [(self._row_to_weapon(row), row["quantity"]) for row in rows]

    def get_inventory_armor(self, player_id: int) -> list[tuple[Armor, int]]:
        """Get all armor in player inventory with quantities (includes equipped)"""
        rows = self.db.conn.execute(
            """SELECT a.*, pa.quantity FROM armor a
               JOIN player_armor pa ON a.id = pa.armor_id
               WHERE pa.player_id = ?""",
            (player_id,),
        ).fetchall()
        return [(self._row_to_armor(row), row["quantity"]) for row in rows]

    def _row_to_player(self, row: sqlite3.Row) -> Player:
        """Convert database row to Player dataclass"""
        return Player(
            id=row["id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            character_class=row["character_class"],
            character_species=row["character_species"],
            level=row["level"],
            hp=row["hp"],
            max_hp=row["max_hp"],
            xp=row["xp"],
            gold=row["gold"],
            strength=row["strength"],
            dexterity=row["dexterity"],
            constitution=row["constitution"],
            intelligence=row["intelligence"],
            wisdom=row["wisdom"],
            charisma=row["charisma"],
            created_at=datetime_from_db(row["created_at"]),
        )

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
            damage_dice_count=row["damage_dice_count"],
            damage_dice_sides=DamageDiceSides(row["damage_dice_sides"]),
            rarity=Rarity(row["rarity"]),
            value=row["value"],
        )

    def _row_to_armor(self, row: sqlite3.Row) -> Armor:
        """Convert database row to Armor dataclass"""
        return Armor(
            id=row["id"],
            world_id=row["world_id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            type=ArmorType(row["type"]),
            ac=row["ac"],
            rarity=Rarity(row["rarity"]),
            value=row["value"],
        )

    def _row_to_item(self, row: sqlite3.Row) -> Item:
        """Convert database row to Item dataclass"""
        return Item(
            id=row["id"],
            world_id=row["world_id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            description=row["description"],
            rarity=Rarity(row["rarity"]),
            value=row["value"],
        )

    def _validate_weapon_slots(self, player_id: int, weapon_to_equip: Weapon) -> None:
        """
        Validate that equipping a weapon doesn't violate hand slot constraints.

        Rules:
        - One two-handed weapon OR
        - Two one-handed weapons OR
        - One one-handed weapon + one shield

        Args:
            player_id: Player ID
            weapon_to_equip: The weapon being equipped

        Raises:
            EquipmentSlotError: If equipping would violate constraints
        """
        # Get currently equipped weapons (excluding the one we're trying to equip)
        equipped_weapons = [
            w for w in self.get_equipped_weapons(player_id) if w.id != weapon_to_equip.id
        ]

        # Get currently equipped shields
        equipped_shields = [
            a for a in self.get_equipped_armor(player_id) if a.type == ArmorType.SHIELD
        ]

        # Check if trying to equip a two-handed weapon
        if weapon_to_equip.hands_required == HandsRequired.TWO_HANDED:
            if equipped_weapons:
                raise EquipmentSlotError(
                    f"Cannot equip two-handed weapon '{weapon_to_equip.name}': "
                    f"already have {len(equipped_weapons)} weapon(s) equipped. "
                    f"Unequip all weapons first."
                )
            if equipped_shields:
                raise EquipmentSlotError(
                    f"Cannot equip two-handed weapon '{weapon_to_equip.name}': "
                    f"shield is equipped. Unequip shield first."
                )

        # Check if trying to equip a one-handed weapon
        elif weapon_to_equip.hands_required == HandsRequired.ONE_HANDED:
            # Check for two-handed weapons already equipped
            two_handed_weapons = [
                w for w in equipped_weapons if w.hands_required == HandsRequired.TWO_HANDED
            ]
            if two_handed_weapons:
                raise EquipmentSlotError(
                    f"Cannot equip one-handed weapon '{weapon_to_equip.name}': "
                    f"two-handed weapon '{two_handed_weapons[0].name}' is equipped. "
                    f"Unequip it first."
                )

            # Check if we already have 2 one-handed weapons
            one_handed_weapons = [
                w for w in equipped_weapons if w.hands_required == HandsRequired.ONE_HANDED
            ]
            if len(one_handed_weapons) >= 2:
                raise EquipmentSlotError(
                    f"Cannot equip one-handed weapon '{weapon_to_equip.name}': "
                    f"already have 2 one-handed weapons equipped. "
                    f"Unequip one first."
                )

            # Check if we have 1 one-handed weapon + 1 shield
            if len(one_handed_weapons) == 1 and equipped_shields:
                raise EquipmentSlotError(
                    f"Cannot equip one-handed weapon '{weapon_to_equip.name}': "
                    f"already have one weapon and a shield equipped. "
                    f"Unequip one first."
                )

    def _validate_shield_slots(self, player_id: int) -> None:
        """
        Validate that equipping a shield doesn't violate hand slot constraints.

        Rules:
        - Can only equip shield with one one-handed weapon
        - Cannot equip with two-handed weapon or two one-handed weapons

        Args:
            player_id: Player ID

        Raises:
            EquipmentSlotError: If equipping shield would violate constraints
        """
        equipped_weapons = self.get_equipped_weapons(player_id)

        # No weapons equipped - OK to equip shield
        if not equipped_weapons:
            return

        # Check for two-handed weapons
        two_handed_weapons = [
            w for w in equipped_weapons if w.hands_required == HandsRequired.TWO_HANDED
        ]
        if two_handed_weapons:
            raise EquipmentSlotError(
                f"Cannot equip shield: two-handed weapon '{two_handed_weapons[0].name}' "
                f"is equipped. Unequip it first."
            )

        # Check for two one-handed weapons
        one_handed_weapons = [
            w for w in equipped_weapons if w.hands_required == HandsRequired.ONE_HANDED
        ]
        if len(one_handed_weapons) >= 2:
            raise EquipmentSlotError(
                "Cannot equip shield: already have 2 one-handed weapons equipped. "
                "Unequip one weapon first."
            )

        # If we have exactly 1 one-handed weapon, it's OK to equip shield
        if len(one_handed_weapons) == 1:
            return
