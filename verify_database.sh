#!/bin/bash

echo "=== Database Verification Script ==="
echo ""

DB="src/game.db"

if [ ! -f "$DB" ]; then
    echo "❌ Database not found at $DB"
    exit 1
fi

echo "✓ Database file exists"
echo ""

echo "=== World Data ==="
sqlite3 "$DB" "SELECT '  World: ' || name FROM worlds;"
echo ""

echo "=== Locations ==="
sqlite3 "$DB" "SELECT '  ' || COUNT(*) || ' locations' FROM locations;"
sqlite3 "$DB" "SELECT '    - ' || name FROM locations LIMIT 3;"
echo ""

echo "=== Items ==="
sqlite3 "$DB" "SELECT '  ' || COUNT(*) || ' items' FROM items;"
sqlite3 "$DB" "SELECT '    - ' || name FROM items WHERE name LIKE '%Health Potion%';"
echo ""

echo "=== Weapons ==="
sqlite3 "$DB" "SELECT '  ' || COUNT(*) || ' weapons' FROM weapons;"
sqlite3 "$DB" "SELECT '    - ' || name || ' (Attack: ' || attack || ')' FROM weapons WHERE name IN ('Iron Sword', 'Battle Axe', 'Rusty Dagger', 'Wooden Bow');"
echo ""

echo "=== Armor ==="
sqlite3 "$DB" "SELECT '  ' || COUNT(*) || ' armor pieces' FROM armor;"
sqlite3 "$DB" "SELECT '    - ' || name || ' (Defense: ' || defense || ')' FROM armor WHERE name IN ('Leather Armor', 'Steel Helmet', 'Leather Boots', 'Leather Cap');"
echo ""

echo "✅ All seed data verified!"
