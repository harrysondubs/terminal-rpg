<div align="center">

# Terminal RPG 🎲
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
### By Harry Dubke
### [Website](https://harrydubke.com) | [Github](https://github.com/harrysondubs) | [X](https://x.com/HarryDubke)
</div>

## ℹ️ Overview
### 👾 The Game
**Terminal RPG** is an experimental, AI-driven text RPG built to explore how large language models (LLMs) can function as real-time game engines and narrative systems within a structured game environment.

I designed terminal-rpg to use **Anthropic's Claude as a Dungeon Master**, combining structured game state, turn-based combat, and free-form storytelling to create an infinitely flexible 5E-ish game. Players have real stats, inventory, health and XP that are stored in a relational database (SQLite) and update as they move through the game. As DM, Claude can initiate ability checks, deal damage, set loot and more all via [agent tool-calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).

The result is—I hope—a game that feels scarily close to sitting down at a table and playing [Dungeons & Dragons 5E](https://en.wikipedia.org/wiki/Dungeons_%26_Dragons#5th_Edition) with a really, really creative DM.

### 💡 Why I Built This
The most powerful and troublesome feature of working with AI is that **LLMs are not deterministic** in their outputs. **Powerful** because non-determinism allows LLMs to react to novel situations. **Troublesome** because engineers (and customers) like predictability and interpretability.

Take the following quote:

> *"Insanity is doing the same thing over and over again and expecting different results"*

Whoever wrote this clearly had zero experience working with AI (or doing sales calls, for that matter).

Whether building [AI agents that respond to Airbnb guests](https://cortado-ai.com) or working on custom builds for clients, I specialize in creating software that balances AI's inherent adaptability with the predictability of a well-engineered system. I hope that terminal-rpg showcases both of these attributes.


## 🧠 What This Project Demonstrates
I designed terminal-rpg as a portfolio project to demonstrate my abilities as an applied AI engineer to:
- **Design rules-based LLM systems**
- **Implement effective agent tool-calling** with [Claude's Messages API](https://platform.claude.com/docs/en/api/python/messages)
- **Efficiently manage long, multi-turn conversations** with popular AI APIs
- **Engineer extensible prompts** that allow for quick, modular tone and context swaps
- **Integrate structured AI responses and relational database schemas**
- **Build a polished terminal UX** using modern Python tooling


## 🚀 Quick Start

Check out the [**Quick Start Guide**](QUICKSTART.md) for the quickest setup from clone to play.

### TL;DR

```bash
# 1. Clone the repo
git clone https://github.com/harrysondubs/terminal-rpg.git

# 2. Navigate to root
cd terminal-rpg

# 3. Run the quickstart script (it will prompt for your Anthropic API key)
python quickstart.py
```

Get your Anthropic API key at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

## 📖 Manual Installation

For devs who prefer manual setup or want more control:

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

# 3.1 Optional: Install dev testing requirements
pip install -r requirements-dev.txt
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

### Code Quality Tools

This project uses:
- **Ruff** for fast Python linting, formatting, and import sorting (100 character line length)
- **Pre-commit** hooks for automated checks

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
│       ├── campaign_presets/    # Campaign presets
│       ├── engines/             # Game and combat engines
│       ├── llm/                 # Claude AI integration and prompting
│       ├── storage/             # Database models and repositories
│       ├── ui/                  # Terminal-based UI components (rich)
│       └── main.py             # Entry point
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project configuration
├── quickstart.py              # Automated setup script
├── QUICKSTART.md              # Quick start guide
└── README.md                  # This file
```

## 🕹️ How to Play

1. **Create or Load a Campaign**: Choose from pre-built worlds or continue existing adventures
2. **Build Your Character**: Select a pre-set class, name your character, and write their backstory
3. **Explore and Interact**: The AI DM responds to your actions with dynamic storytelling
4. **Engage in Combat *(turn-based combat coming soon)***: Face monsters in tactical turn-based battles
5. **Progress and Grow**: Level up, collect loot, and shape your legend

### Game Files

The game creates these files automatically. They are .gitignored by default:
- `games.db` - SQLite database storing all your campaigns and progress
- `terminal_rpg_debug.log` - Debug logs for troubleshooting

## 🎬 Screenshots

> Coming soon

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

**Ready to embark on your adventure?** Head to the [Quick Start Guide](QUICKSTART.md) and begin your journey... 🎲⚔️
