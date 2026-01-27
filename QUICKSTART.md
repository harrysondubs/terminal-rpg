# 🎲 Terminal RPG - Quick Start Guide

Get up and running with Terminal RPG in under 5 minutes!

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.10 or higher** installed
   - Check your version: `python --version` or `python3 --version`
   - Download from: [python.org/downloads](https://www.python.org/downloads/)

2. **An Anthropic API key** (required for the AI Dungeon Master)
   - Sign up for free at: [console.anthropic.com](https://console.anthropic.com/)

## Quick Start (3 Steps)

### 1. Clone the Repository

```bash
git clone https://github.com/harrysondubs/terminal-rpg.git
cd terminal-rpg
```

### 2. Get Your API Key

Sign up for an Anthropic account and get your API key:
- Visit: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- Create a new API key
- Copy it (you'll need it in the next step)

> **Note:** The quickstart script will automatically create a `.env` file from the included `.env.example` template and prompt you to paste your API key. You can also set it up manually if you prefer.

### 3. Run the Quickstart Script

```bash
python quickstart.py
```

That's it! The script will:
- ✓ Create a virtual environment
- ✓ Install all dependencies
- ✓ Set up your `.env` file from the template
- ✓ Prompt you to enter your API key (if not already configured)
- ✓ Launch the game

The first time may take a minute to install everything. When prompted, simply paste your API key and press Enter!

## What to Expect on First Launch

When you run the game for the first time, you'll:

1. **See the Welcome Screen** - Beautiful ASCII art greeting
2. **Create Your First Campaign** - Choose from pre-made settings like Forgotten Realms
3. **Design Your Character** - Pick a class, name your hero, and write a backstory
4. **Meet Your AI Dungeon Master** - Claude will guide your adventure

The game creates a `games.db` file to save your progress automatically.

## Developer Mode

If you want to contribute or modify the game:

```bash
python quickstart.py --dev
```

This installs additional development tools like `ruff` for linting and formatting.

After setup, activate the virtual environment and install pre-commit hooks:

```bash
# Activate venv
source rpg-venv/bin/activate  # On macOS/Linux
# OR
rpg-venv\Scripts\activate  # On Windows

# Install pre-commit hooks
pre-commit install
```

## Running the Game Later

After the first setup, you can run the game anytime:

**Option 1: Use the quickstart script**
```bash
python quickstart.py
```

**Option 2: Activate venv manually**
```bash
# Activate the virtual environment
source rpg-venv/bin/activate  # macOS/Linux
# OR
rpg-venv\Scripts\activate  # Windows

# Run the game
cd src
python -m terminal_rpg.main
```

## Troubleshooting

### "Python version too old" error
- You need Python 3.10+. Update Python from [python.org](https://www.python.org/downloads/)
- On some systems, try `python3` instead of `python`

### "ANTHROPIC_API_KEY not set" error
- Make sure your `.env` file exists in the project root
- Check that your API key is correctly formatted (no quotes, no spaces)
- Verify the `.env` file isn't named `.env.txt` (check file extensions)

### "Module not found" errors
- Delete the `rpg-venv` folder and run `python quickstart.py` again
- This recreates the virtual environment from scratch

### Game won't start or crashes
- Check `terminal_rpg_debug.log` for detailed error messages
- Make sure your API key has available credits in your Anthropic account
- Try updating dependencies: `rpg-venv/bin/pip install -r requirements.txt --upgrade`

### Windows-specific issues
- If you get execution policy errors with PowerShell, try:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- Or use Command Prompt (cmd.exe) instead of PowerShell

## Need More Help?

- **Full Documentation**: See [README.md](README.md) for detailed setup and development info
- **Report Issues**: Found a bug? [Open an issue](https://github.com/harrysondubs/terminal-rpg/issues)
- **Get Involved**: Check out [CONTRIBUTING.md](CONTRIBUTING.md) to help improve the game

## Tips for Your First Adventure

- **Save Often**: Your progress auto-saves, but you can return to the main menu anytime
- **Explore**: Try different actions - the AI DM responds to creative choices!
- **Read Carefully**: Claude writes immersive descriptions - take your time
- **Multiple Campaigns**: You can run multiple characters/campaigns simultaneously
- **Combat**: The game includes a turn-based combat system with D&D-style mechanics

---

**Ready to begin your adventure?** Run `python quickstart.py` and let the AI Dungeon Master guide you!

🎮 Happy adventuring! 🎲
