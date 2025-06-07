"""
Configuration service for managing game settings.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigService:
    """Service for managing game configuration and settings."""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._defaults = {
            "window": {"width": 800, "height": 600, "fullscreen": False},
        }
        self.load_config()

    def load_config(self):
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self._config = self._deep_merge(self._defaults.copy(), loaded_config)
            else:
                self._config = self._defaults.copy()
                self.save_config()  # Create default config file
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            self._config = self._defaults.copy()

    def save_config(self):
        """Save current configuration to file."""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'window.width')."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, save: bool = True):
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        if save:
            self.save_config()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self._config.get(section, {}).copy()

    def update_section(self, section: str, values: Dict[str, Any], save: bool = True):
        """Update an entire configuration section."""
        if section not in self._config:
            self._config[section] = {}

        self._config[section].update(values)

        if save:
            self.save_config()

    def reset_to_defaults(self, save: bool = True):
        """Reset configuration to default values."""
        self._config = self._defaults.copy()
        if save:
            self.save_config()

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    # Convenience properties for common settings
    @property
    def window_size(self) -> tuple[int, int]:
        """Get window size as (width, height)."""
        return (self.get("window.width"), self.get("window.height"))

    @property
    def is_fullscreen(self) -> bool:
        """Check if fullscreen mode is enabled."""
        return self.get("window.fullscreen", False)
