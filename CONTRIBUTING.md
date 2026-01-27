# Contributing to Terminal RPG 🎲

Thank you for your interest in contributing to Terminal RPG! This document provides guidelines and instructions for contributing to the project.

## 🌟 Ways to Contribute

There are many ways to contribute to Terminal RPG:

- **🐛 Report Bugs**: Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **💡 Suggest Features**: Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **📝 Improve Documentation**: Fix typos, clarify instructions, add examples
- **🔧 Submit Code**: Fix bugs, add features, improve performance
- **🎨 Design**: Create campaign presets, write storylines, design game mechanics
- **🧪 Testing**: Test new features, report issues, provide feedback

## 🚀 Getting Started

### 1. Set Up Your Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/harrysondubs/terminal-rpg.git
cd terminal-rpg

# Run the quickstart script in developer mode
python quickstart.py --dev

# Activate the virtual environment
source rpg-venv/bin/activate  # On Windows: rpg-venv\Scripts\activate

# Install pre-commit hooks
pre-commit install
```

### 2. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or updates

### 3. Make Your Changes

Follow these guidelines:

- **Code Style**: We use Ruff for formatting and linting
- **Line Length**: Maximum 100 characters
- **Type Hints**: Add type hints to function signatures
- **Docstrings**: Add docstrings to classes and functions
- **Comments**: Explain complex logic with inline comments

### 4. Test Your Changes

```bash
# Run the linter
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Format code
ruff format src/

# Run pre-commit hooks
pre-commit run --all-files

# Test the game manually
cd src
python -m terminal_rpg.main
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new campaign preset for Eberron"
# or
git commit -m "fix: resolve inventory duplication bug"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style/formatting
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub using our [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## 📋 Code Style Guidelines

### Python Style

We follow these conventions:

- **Formatter**: Ruff (configured in `pyproject.toml`)
- **Imports**: Sorted using isort (integrated in Ruff)
- **Quotes**: Double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Line Length**: 100 characters max

### Example

```python
"""Module docstring explaining the purpose."""

from typing import Optional

from terminal_rpg.storage.models import Player


def create_player(name: str, class_name: str, description: Optional[str] = None) -> Player:
    """
    Create a new player character.

    Args:
        name: The character's name
        class_name: The character's class (e.g., "Fighter", "Wizard")
        description: Optional character description

    Returns:
        A new Player instance

    Raises:
        ValueError: If name or class_name is empty
    """
    if not name or not class_name:
        raise ValueError("Name and class name are required")

    return Player(name=name, class_name=class_name, description=description)
```

## 🏗️ Project Architecture

Understanding the codebase structure:

```
src/terminal_rpg/
├── campaign_presets/     # Campaign world definitions
│   ├── models.py        # Preset data models
│   ├── registry.py      # Preset registration system
│   └── presets/         # Individual campaign presets
├── engines/             # Core game logic
│   ├── game.py         # Main game loop
│   ├── combat.py       # Combat system
│   └── new_campaign.py # Campaign creation
├── llm/                 # AI integration
│   ├── claude_api.py   # Anthropic API wrapper
│   ├── game/           # Game-related AI prompts
│   └── combat/         # Combat-related AI prompts
├── storage/             # Database layer
│   ├── models.py       # SQLAlchemy models
│   ├── database.py     # Database connection
│   └── repositories/   # Data access layer
├── ui/                  # User interface
│   ├── menu_display.py # Menu screens
│   ├── prompts.py      # User input prompts
│   └── game_display.py # Game output formatting
└── main.py             # Entry point
```

## 🎨 Adding New Features

### Adding a New Campaign Preset

1. Create a new file in `src/terminal_rpg/campaign_presets/presets/`
2. Define your preset using the `CampaignPreset` model
3. Register it in the preset system
4. Add at least one starting location and class

Example:
```python
from terminal_rpg.campaign_presets.models import CampaignPreset, ClassPreset, LocationPreset

EBERRON_PRESET = CampaignPreset(
    name="Eberron",
    description="A world of noir intrigue and pulp adventure",
    # ... rest of preset definition
)
```

### Adding New Game Commands

1. Add the command handler in the appropriate engine file
2. Update the AI prompt system to recognize the command
3. Add tool definitions if needed for structured AI output
4. Update documentation

### Modifying the Database Schema

1. Update models in `src/terminal_rpg/storage/models.py`
2. Update repository methods in `src/terminal_rpg/storage/repositories/`
3. Test with a fresh database to ensure schema creation works
4. Document any migration steps needed

## 🧪 Testing Guidelines

While we're still building our test suite, please manually test:

1. **New Campaigns**: Create a campaign with your changes
2. **Saved Games**: Load an existing game and verify compatibility
3. **Combat**: Enter and complete a combat encounter
4. **Edge Cases**: Test with invalid inputs, empty values, etc.
5. **Cross-Platform**: If possible, test on Windows, macOS, and Linux

## 📝 Documentation

When adding features, update:

- **README.md**: For major features or changes
- **QUICKSTART.md**: For setup or getting started changes
- **Docstrings**: For all new functions and classes
- **Comments**: For complex logic or algorithms

## ❓ Questions or Need Help?

- **Discussion**: Open a [GitHub Discussion](https://github.com/harrysondubs/terminal-rpg/discussions)
- **Issues**: Check [existing issues](https://github.com/harrysondubs/terminal-rpg/issues) or create a new one
- **Code Review**: Don't hesitate to ask for feedback in your PR

## 🎖️ Recognition

All contributors are valued and will be recognized:

- Contributors are listed in GitHub's contributor graph
- Significant contributions may be highlighted in release notes
- We appreciate all contributions, no matter how small!

## 📜 License

By contributing to Terminal RPG, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping make Terminal RPG better!** 🎲⚔️

Your contributions help create amazing adventures for players around the world.
