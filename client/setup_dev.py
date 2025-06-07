#!/usr/bin/env python3
"""
Development setup script for FixieDashBrooklyn

This script automates the setup process for development.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(
        f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible"
    )
    return True


def setup_virtual_environment():
    """Set up virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True

    return run_command("python -m venv venv", "Creating virtual environment")


def install_dependencies():
    """Install project dependencies."""
    # Determine the activation script based on OS
    if os.name == "nt":  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # macOS/Linux
        pip_cmd = "venv/bin/pip"

    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing dependencies"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False

    return True


def check_assets():
    """Check if required assets exist."""
    assets_path = Path("assets")
    required_assets = [
        "repeatable_background.png",
        "cyclist_flat.png",
        "cyclist_up.png",
        "get_that_empanada.png",
        "start_screens/prospect_farmers.png",
        "start_screens/prospect_park_entrance.png",
        "start_screens/wegmans.png",
        "start_screens/williamsburg.png",
    ]

    missing_assets = []
    for asset in required_assets:
        asset_path = assets_path / asset
        if not asset_path.exists():
            missing_assets.append(asset)

    if missing_assets:
        print("⚠️  Missing assets:")
        for asset in missing_assets:
            print(f"   - {asset}")
        print("   The game may not display properly without these files.")
        return False

    print("✅ All required assets found")
    return True


def show_next_steps():
    """Show the user what to do next."""
    print("\n🎉 Setup complete!")
    print("\n🚀 To run the game:")

    if os.name == "nt":  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")

    print("   python main.py")
    print("\n🎮 Controls:")
    print("   - Left/Right Arrow Keys: Pedal")
    print("   - Escape: Quit")
    print("\n📖 See README.md for detailed instructions")


def main():
    """Main setup function."""
    print("🚴‍♂️ FixieDashBrooklyn - Development Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        return 1

    # Set up virtual environment
    if not setup_virtual_environment():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    # Check assets (non-fatal)
    check_assets()

    # Show next steps
    show_next_steps()

    return 0


if __name__ == "__main__":
    sys.exit(main())
