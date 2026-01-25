# Terminal RPG - Game Setup Implementation

## Overview
A complete game setup flow has been implemented for your terminal-based RPG. Players can now create campaigns, choose character classes, customize their characters, and start their adventures!

## What Was Implemented

### 1. Database Initialization
- Automatic database creation and seeding on first run
- Seeds "The Forgotten Realms" world with:
  - 5 unique locations (tavern, forest, dungeon, caverns, village)
  - 9 consumable items (health potions, scrolls, etc.)
  - 10 weapons (daggers, swords, axes, bows)
  - 15 armor pieces (helmets, chestplates, boots, shields, leggings)
  - 10 NPCs/enemies (from level 1 goblins to level 20 dragons)

### 2. Character Class System
Three pre-configured character classes with unique stats and starting equipment:

#### Fighter (Human)
- **Primary Stats**: STR 16, CON 15
- **HP**: 80
- **Starting Equipment**:
  - Weapons: Iron Sword (equipped), Battle Axe
  - Armor: Leather Armor (equipped), Steel Helmet (equipped)
  - Items: Minor Health Potion
- **Gold**: 100

#### Thief (Halfling)
- **Primary Stats**: DEX 17, CHA 14
- **HP**: 64
- **Starting Equipment**:
  - Weapons: Rusty Dagger (equipped), Wooden Bow
  - Armor: Leather Armor (equipped), Leather Boots (equipped)
  - Items: Minor Health Potion
- **Gold**: 75

#### Bard (Elf)
- **Primary Stats**: CHA 16, INT 14
- **HP**: 57
- **Starting Equipment**:
  - Weapons: Rusty Dagger (equipped), Wooden Bow
  - Armor: Leather Armor (equipped), Leather Cap (equipped)
  - Items: Minor Health Potion
- **Gold**: 80

### 3. Game Flow
Complete new game creation flow with:
1. Welcome screen with ASCII art
2. Main menu (New Game, Load Game, Exit)
3. World selection from database
4. Class selection with stat preview
5. Campaign naming
6. Character naming
7. Character description
8. Confirmation dialog
9. Character creation with loading animation
10. Final character sheet display

### 4. UI Features
- Rich terminal formatting with colors and panels
- Interactive questionary prompts with validation
- Progress spinners during database operations
- Formatted stat tables and equipment lists
- Error handling with user-friendly messages

## How to Run the Game

### Prerequisites
Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or if you're using a virtual environment:

```bash
python3 -m venv terminal_rpg-venv
source terminal_rpg-venv/bin/activate
pip install -r requirements.txt
```

### Running the Game

From the project root directory:

```bash
cd src
python3 -m terminal_rpg.main
```

The game will:
1. Automatically create and seed the database if it doesn't exist
2. Display the welcome screen
3. Present you with the main menu

### Game Flow

1. **Start Menu**: Choose "New Game" to begin
2. **World Selection**: Select "The Forgotten Realms" (or create your own - not yet implemented)
3. **Class Selection**: Choose Fighter, Thief, or Bard
   - Each class displays stats and starting equipment
4. **Campaign Setup**:
   - Enter a name for your campaign
   - Enter your character's name
   - Provide a character description
5. **Confirmation**: Confirm your choices
6. **Character Creation**: Watch as your campaign is created
7. **Character Sheet**: Review your final character

## Files Modified/Created

### Backend Logic
- **[src/terminal_rpg/engines/new_campaign.py](src/terminal_rpg/engines/new_campaign.py)** (NEW)
  - `get_available_worlds()` - Query worlds from database
  - `create_character_class_presets()` - Return class configurations
  - `create_new_campaign()` - Main campaign creation function
  - `_resolve_equipment_ids()` - Convert equipment names to IDs
  - `_add_starting_equipment()` - Add items to player inventory

### UI Display
- **[src/terminal_rpg/ui/display.py](src/terminal_rpg/ui/display.py)** (UPDATED)
  - `display_welcome()` - ASCII art welcome screen
  - `display_world_info()` - World details panel
  - `display_class_info()` - Class stats and equipment
  - `display_game_start_summary()` - Final character sheet

### UI Prompts
- **[src/terminal_rpg/ui/prompts.py](src/terminal_rpg/ui/prompts.py)** (UPDATED)
  - `show_start_menu()` - Main menu selection
  - `select_world()` - World selection menu
  - `select_class()` - Class selection menu
  - `get_campaign_name()` - Campaign name input
  - `get_character_name()` - Character name input
  - `get_character_description()` - Character description input
  - `confirm_character_creation()` - Confirmation dialog

### Entry Point
- **[src/terminal_rpg/main.py](src/terminal_rpg/main.py)** (UPDATED)
  - `main()` - Entry point, database initialization, main menu loop
  - `run_new_game_flow()` - Complete new game creation orchestration

## Database Structure

The game uses SQLite with the following key tables:
- `worlds` - Game worlds
- `campaigns` - Save files
- `players` - Player characters (one per campaign)
- `locations` - Places in the world
- `items`, `weapons`, `armor` - Equipment and items
- `npcs` - Non-player characters
- `player_items`, `player_weapons`, `player_armor` - Inventory join tables
- `battles`, `campaign_log` - Combat and history tracking

## Verification

To verify the database was created correctly, run:

```bash
./verify_database.sh
```

This will check:
- Database file exists
- World data is present
- All seed data (locations, items, weapons, armor) is loaded
- Equipment matches class requirements

## Next Steps

The following features are marked as placeholders for future implementation:
1. **Load Game** - Load existing campaigns from database
2. **Create Your Own World** - Custom world creation
3. **Game Engine** - The actual gameplay loop after character creation

## Technical Notes

### HP Calculation
HP is calculated as: `base_hp + (constitution * 2)`
- Fighter: 50 + (15 * 2) = 80 HP
- Thief: 40 + (12 * 2) = 64 HP
- Bard: 35 + (11 * 2) = 57 HP

### Equipment Auto-Equip
- Primary weapon (first in list) is automatically equipped
- All starting armor pieces are automatically equipped
- Items remain in inventory (not equipped)

### Error Handling
- Database connection errors: Caught and displayed to user
- Missing equipment: Raises ValueError with specific item name
- User cancellation: Gracefully returns to main menu
- Input validation: Enforced via Questionary validators

### Race Assignment
Currently, each class has a fixed race:
- Fighter → Human
- Thief → Halfling
- Bard → Elf

This can be extended to allow race selection in future updates.

## Testing

The implementation has been verified:
- ✅ Database initialization and seeding works
- ✅ All seed data is present (worlds, locations, items, weapons, armor, NPCs)
- ✅ Backend logic successfully creates campaigns
- ✅ Equipment resolution matches class requirements
- ✅ Inventory system properly tracks items
- ✅ Auto-equip functionality works for weapons and armor
- ✅ Rich UI formatting displays correctly
- ✅ Error handling prevents crashes

## Troubleshooting

### "Module not found" errors
Make sure you're running from the `src` directory and using the module syntax:
```bash
cd src
python3 -m terminal_rpg.main
```

### Database not found
The database is created automatically in the current working directory. If you see this error, make sure you have write permissions in the directory.

### Interactive prompts not working
Questionary requires an interactive terminal. If running in a non-interactive environment, the prompts will fail. Make sure you're running the game directly in your terminal, not through a script or automation tool.

## Success! 🎉

Your terminal RPG now has a complete game setup system! Players can:
- ✅ Launch the game and see a welcome screen
- ✅ Create new campaigns
- ✅ Choose from three distinct character classes
- ✅ Customize their character name and description
- ✅ Start with appropriate equipment for their class
- ✅ See a beautiful character sheet before beginning their adventure

The foundation is set for adding the actual game engine and gameplay mechanics!
