# Terminal RPG 🎲

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

An immersive, AI-powered text-based RPG that uses Claude as your personal Dungeon Master. Experience dynamic storytelling, tactical turn-based combat, and a rich campaign system where every decision shapes your adventure.

## ✨ Features

- **🤖 AI Dungeon Master**: Claude crafts personalized narratives and responds dynamically to your choices
- **⚔️ Turn-Based Combat**: Tactical D&D-style combat with abilities, equipment, and strategic depth
- **🗺️ Campaign System**: Pre-built worlds (Forgotten Realms, Sword Coast) with rich lore and locations
- **📊 Character Progression**: Level up, gain XP, manage inventory, and develop your hero
- **💾 Save System**: Persistent SQLite database tracks multiple campaigns and characters
- **🎨 Beautiful UI**: Rich terminal interface with colors, tables, and formatted output
- **🔧 Extensible**: Modular architecture makes it easy to add new campaigns, classes, and features

## 🚀 Quick Start

**New to the game?** Check out our [**Quick Start Guide**](QUICKSTART.md) for a simple 3-step setup!

### TL;DR

```bash
# 1. Clone the repo
git clone https://github.com/harrysondubs/terminal-rpg.git
cd terminal-rpg

# 2. Run the quickstart script (it will prompt for your API key)
python quickstart.py
```

Get your free Anthropic API key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

## 📖 Manual Installation

For developers who prefer manual setup or want more control:

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- An Anthropic API key

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/harrysondubs/terminal-rpg.git
cd terminal-rpg
```

2. Create and activate a virtual environment:
```bash
python -m venv rpg-venv
source rpg-venv/bin/activate  # On Windows: rpg-venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
# Copy the example file and add your API key
cp .env.example .env
# Then edit .env and replace 'your_api_key_here' with your actual key
```

Or create `.env` manually:
```bash
echo "ANTHROPIC_API_KEY=your_actual_key_here" > .env
```

5. Run the game:
```bash
cd src
python -m terminal_rpg.main
```

## 🎮 How to Play

1. **Create or Load a Campaign**: Choose from pre-built worlds or continue existing adventures
2. **Build Your Character**: Select a class, name your hero, and write their backstory
3. **Explore and Interact**: The AI DM responds to your actions with dynamic storytelling
4. **Engage in Combat**: Face monsters in tactical turn-based battles
5. **Progress and Grow**: Level up, collect loot, and shape your legend

### Game Files

The game creates these files automatically:
- `games.db` - SQLite database storing all your campaigns and progress
- `terminal_rpg_debug.log` - Debug logs for troubleshooting

## 🎬 Screenshots

> Coming soon! We're working on adding screenshots of the game in action.

## 🛠️ Development

### Development Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

This will automatically run code formatting and linting checks before each commit.

### Code Quality Tools

This project uses:
- **Ruff** for fast Python linting, formatting, and import sorting (100 character line length)
- **Pre-commit** hooks for automated checks

#### Manual Commands

Run ruff to lint:
```bash
ruff check src/
```

Run ruff to auto-fix issues:
```bash
ruff check --fix src/
```

Format code with ruff:
```bash
ruff format src/
```

Run all pre-commit hooks manually:
```bash
pre-commit run --all-files
```

### Running Tests

```bash
pytest
```

> Note: Test suite is currently in development.

## 📁 Project Structure

```
terminal-rpg/
├── src/
│   └── terminal_rpg/
│       ├── campaign_presets/    # Campaign preset system
│       ├── engines/             # Game and combat engines
│       ├── llm/                 # Claude AI integration
│       ├── storage/             # Database models and repositories
│       ├── ui/                  # User interface components
│       └── main.py             # Entry point
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project configuration
├── quickstart.py              # Automated setup script
├── QUICKSTART.md              # Quick start guide
└── README.md                  # This file
```

## 🤝 Contributing

We welcome contributions from the community! Whether you want to:
- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit code changes

Please check out our [issue templates](.github/ISSUE_TEMPLATE/) and [pull request template](.github/PULL_REQUEST_TEMPLATE.md) to get started.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and commit (`git commit -m 'Add amazing feature'`)
4. Push to your branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Make sure to:
- Follow the existing code style (enforced by Ruff)
- Run pre-commit hooks before committing
- Write clear commit messages
- Update documentation as needed

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for creating Claude, the AI that powers our dynamic Dungeon Master
- **D&D 5e** for inspiration on game mechanics and the Open Gaming License
- The Python community for amazing libraries like `rich`, `questionary`, and `anthropic`
- All contributors who help make this project better!

## 📞 Support & Community

- **Issues**: Found a bug? [Report it here](https://github.com/harrysondubs/terminal-rpg/issues)
- **Discussions**: Have questions? [Start a discussion](https://github.com/harrysondubs/terminal-rpg/discussions)
- **API Costs**: This game uses the Anthropic API. Monitor your usage at [console.anthropic.com](https://console.anthropic.com/)

## 🗺️ Roadmap

Future plans include:
- [ ] Additional campaign worlds and presets
- [ ] Custom campaign and character creators
- [ ] Enhanced combat flow and spells
- [ ] In-game image generation
- [ ] Export adventures to PDF

---

**Ready to embark on your adventure?** Head to the [Quick Start Guide](QUICKSTART.md) and begin your journey! 🎲⚔️
