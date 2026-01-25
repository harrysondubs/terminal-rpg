# Terminal RPG

An AI-powered text-based RPG that uses Claude as your Dungeon Master. Experience an immersive fantasy adventure where an AI guides your journey through a rich world with dynamic storytelling and interactive gameplay.

## Features

- 🎭 **AI Dungeon Master** - Claude acts as your DM, creating engaging narratives and responding to your actions
- 🗺️ **Exploration** - Travel through multiple locations in a fantasy world
- ⚔️ **Character Classes** - Choose from Fighter, Thief, or Bard with unique stats and equipment
- 🎒 **Inventory System** - Manage weapons, armor, and items
- 💾 **Persistent Campaigns** - All conversations and game state saved to database
- 🛠️ **Tool Integration** - AI can check your inventory and move you between locations

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install anthropic rich questionary python-dotenv
```

### 2. Configure Environment Variables

Copy the example environment file and add your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key from [Anthropic Console](https://console.anthropic.com/settings/keys)

### 3. Run the Game

```bash
python -m src.terminal_rpg.main
```

## How to Play

1. **Create a New Game**: Choose a world and character class
2. **Name Your Character**: Give your character a name and backstory
3. **Start Adventuring**: Interact with the AI DM through natural conversation
   - Describe what you want to do: "I approach the innkeeper"
   - Ask questions: "What's in my inventory?"
   - Travel: "I want to go to the Whispering Woods"
   - Type `quit` to exit

## Project Structure

```
src/terminal_rpg/
├── engines/          # Game logic and campaign creation
├── llm/             # AI integration
│   ├── claude_api.py       # API wrapper
│   └── game/
│       ├── dm_game.py      # Main DM loop
│       ├── message_history.py
│       ├── prompts/        # System prompts
│       └── tools/          # DM tools (inventory, location)
├── storage/         # Database and models
├── ui/              # Terminal UI components
└── main.py          # Entry point
```

## Available Locations

- The Prancing Pony Inn (starting location)
- Whispering Woods
- Ruins of Shadowkeep
- Crystal Caverns
- Millhaven Village

## Character Classes

- **Fighter**: High strength and HP, specialized in melee combat
- **Thief**: High dexterity and charisma, nimble and stealthy
- **Bard**: High charisma and intelligence, masters of magic and persuasion
