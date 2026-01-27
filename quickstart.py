#!/usr/bin/env python3
"""
Terminal RPG Quickstart Script
Cross-platform script to set up virtual environment and launch the game.
"""

import argparse
import platform
import re
import shutil
import subprocess
import sys
import venv
from pathlib import Path


def check_python_version():
    """Check if Python version meets minimum requirements."""
    if sys.version_info < (3, 10):  # noqa: UP036
        print("❌ Error: Python 3.10 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("\n   Please upgrade Python and try again.")
        print("   Visit: https://www.python.org/downloads/")
        sys.exit(1)
    print(
        f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected"
    )


def get_venv_paths(venv_dir: Path):
    """Get the correct paths for venv binaries based on OS."""
    system = platform.system()

    if system == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
        pip_path = venv_dir / "Scripts" / "pip.exe"
        activate_cmd = str(venv_dir / "Scripts" / "activate.bat")
    else:  # Unix-like (Linux, macOS, etc.)
        python_path = venv_dir / "bin" / "python"
        pip_path = venv_dir / "bin" / "pip"
        activate_cmd = f"source {venv_dir / 'bin' / 'activate'}"

    return python_path, pip_path, activate_cmd


def create_virtualenv(venv_dir: Path):
    """Create a virtual environment."""
    print(f"\n📦 Creating virtual environment at {venv_dir}...")
    try:
        venv.create(venv_dir, with_pip=True)
        print("✓ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False


def install_dependencies(pip_path: Path, dev_mode: bool = False):
    """Install project dependencies."""
    print("\n📥 Installing dependencies...")

    # Install runtime dependencies
    print("   Installing runtime dependencies from requirements.txt...")
    result = subprocess.run(
        [str(pip_path), "install", "-r", "requirements.txt"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print("❌ Error installing runtime dependencies:")
        print(result.stderr)
        return False

    print("✓ Runtime dependencies installed")

    # Install dev dependencies if requested
    if dev_mode:
        print("   Installing development dependencies from requirements-dev.txt...")
        result = subprocess.run(
            [str(pip_path), "install", "-r", "requirements-dev.txt"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("❌ Error installing development dependencies:")
            print(result.stderr)
            return False

        print("✓ Development dependencies installed")

    return True


def check_env_file():
    """Check if .env file exists and prompt for API key if needed."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    # Step 1: Create .env from .env.example if it doesn't exist
    if not env_file.exists():
        print("\n📝 .env file not found.")

        if env_example.exists():
            try:
                # Copy .env.example to .env
                shutil.copy(env_example, env_file)
                print("✓ Created .env from .env.example template")
            except Exception as e:
                print(f"⚠️  Could not copy .env.example: {e}")
                # Create manually as fallback
                try:
                    with open(".env", "w") as f:
                        f.write("# Anthropic API Key\n")
                        f.write("# Get your key at: https://console.anthropic.com/settings/keys\n")
                        f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
                    print("✓ Created .env template manually")
                except Exception as e2:
                    print(f"❌ Error creating .env file: {e2}")
                    return
        else:
            # No .env.example, create from scratch
            try:
                with open(".env", "w") as f:
                    f.write("# Anthropic API Key\n")
                    f.write("# Get your key at: https://console.anthropic.com/settings/keys\n")
                    f.write("ANTHROPIC_API_KEY=your_api_key_here\n")
                print("✓ Created .env template")
            except Exception as e:
                print(f"❌ Error creating .env file: {e}")
                return
    else:
        print("✓ .env file found")

    # Step 2: Check if API key is set to a real value
    try:
        api_key = None
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

        # Check if API key is missing or still has placeholder value
        if not api_key or api_key in ["your_api_key_here", "", '""', "''"]:
            print("\n⚠️  Anthropic API key not configured!")
            print("   The game requires a valid API key to function.")
            print()
            print("   Visit https://console.anthropic.com/settings/keys to create your key")
            print()

            user_key = input(
                "   Paste your Anthropic API key here (or press Enter to skip): "
            ).strip()

            if user_key and user_key != "your_api_key_here":
                try:
                    # Read the file content
                    with open(env_file) as f:
                        content = f.read()

                    # Replace the placeholder or add the key
                    if "ANTHROPIC_API_KEY=" in content:
                        # Replace existing line
                        content = re.sub(
                            r"ANTHROPIC_API_KEY=.*", f"ANTHROPIC_API_KEY={user_key}", content
                        )
                    else:
                        # Append if not found
                        content += f"\nANTHROPIC_API_KEY={user_key}\n"

                    # Write back
                    with open(env_file, "w") as f:
                        f.write(content)

                    print("✓ API key saved to .env file!")
                except Exception as e:
                    print(f"❌ Error saving API key: {e}")
                    print("   Please manually edit .env and add your key.")
            else:
                print("⚠️  Skipped API key setup.")
                print("   Remember to add your API key to .env before playing!")
                print("   Edit the file and set: ANTHROPIC_API_KEY=your_actual_key")
        else:
            print("✓ Anthropic API key configured")

    except Exception as e:
        print(f"⚠️  Could not verify API key: {e}")
        print("   Please ensure your .env file contains: ANTHROPIC_API_KEY=your_key")


def launch_game(python_path: Path):
    """Launch the Terminal RPG game."""
    print("\n🎮 Launching Terminal RPG...")
    print("=" * 60)
    print()

    try:
        # Convert to absolute path before changing directories
        absolute_python_path = python_path.resolve()

        # Change to src directory and run the game
        result = subprocess.run([str(absolute_python_path), "-m", "terminal_rpg.main"], cwd="src")
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Goodbye!")
        return True
    except Exception as e:
        print(f"\n❌ Error launching game: {e}")
        return False


def main():
    """Main quickstart flow."""
    parser = argparse.ArgumentParser(
        description="Terminal RPG Quickstart - Automated setup and launch script"
    )
    parser.add_argument(
        "--dev", action="store_true", help="Install development dependencies (for contributors)"
    )
    parser.add_argument(
        "--skip-launch", action="store_true", help="Set up environment but don't launch the game"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🎲 Terminal RPG - Quickstart Setup")
    print("=" * 60)

    # Check Python version
    check_python_version()

    # Setup paths
    venv_dir = Path("rpg-venv")
    python_path, pip_path, activate_cmd = get_venv_paths(venv_dir)

    # Check if venv already exists
    if venv_dir.exists() and python_path.exists():
        print(f"✓ Virtual environment already exists at {venv_dir}")
        print("   Tip: Delete 'rpg-venv' folder to recreate from scratch")
    else:
        # Create virtual environment
        if not create_virtualenv(venv_dir):
            sys.exit(1)

    # Upgrade pip in the virtual environment
    print("\n⬆️  Upgrading pip...")
    subprocess.run(
        [str(python_path), "-m", "pip", "install", "--upgrade", "pip"], capture_output=True
    )
    print("✓ pip upgraded")

    # Install dependencies
    if not install_dependencies(pip_path, dev_mode=args.dev):
        sys.exit(1)

    # Check for .env file
    check_env_file()

    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)

    if args.dev:
        print("\n📝 Development mode enabled. Additional info:")
        print("   • Pre-commit hooks: Run 'pre-commit install' in activated venv")
        print("   • Linting: ruff check src/")
        print("   • Formatting: ruff format src/")

    print("\n💡 To activate the virtual environment manually:")
    print(f"   {activate_cmd}")
    print("\n💡 To run the game later:")
    if platform.system() == "Windows":
        print("   rpg-venv\\Scripts\\python.exe -m terminal_rpg.main")
    else:
        print("   rpg-venv/bin/python -m terminal_rpg.main")

    # Launch game unless skip flag is set
    if not args.skip_launch:
        print()
        input("Press Enter to launch the game...")
        if not launch_game(python_path):
            sys.exit(1)

    print("\n👋 Thank you for playing Harry Dubke's Terminal RPG!")


if __name__ == "__main__":
    main()
