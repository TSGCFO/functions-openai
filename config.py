"""
Configuration management for the response formatter system.
Handles configuration loading from files, environment variables, and command line arguments.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DisplayConfig:
    """Configuration for response display settings."""
    default_mode: str = "clean"  # clean, verbose, debug
    enable_colors: bool = True
    enable_interactive: bool = True
    enable_cost_tracking: bool = True
    show_timestamps: bool = False
    show_model_info: bool = False
    max_content_length: int = 1000
    truncate_long_content: bool = True
    

@dataclass
class ColorConfig:
    """Color configuration for different content types."""
    header: str = "cyan"
    success: str = "green"
    error: str = "red"
    warning: str = "yellow"
    technical: str = "bright_black"
    content: str = "white"
    reasoning: str = "blue"
    usage: str = "magenta"


@dataclass
class KeyboardConfig:
    """Keyboard shortcut configuration."""
    clean_mode: str = "c"
    verbose_mode: str = "v"
    debug_mode: str = "d"
    reasoning: str = "r"
    expand_collapse: str = "space"
    exit_interactive: str = "escape"


@dataclass
class Config:
    """Main configuration class."""
    display: DisplayConfig
    colors: ColorConfig
    keyboard: KeyboardConfig
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        valid_modes = {"clean", "verbose", "debug"}
        if self.display.default_mode not in valid_modes:
            self.display.default_mode = "clean"


class ConfigManager:
    """Manages configuration loading and saving."""
    
    CONFIG_FILE = "response_formatter_config.json"
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Config:
        """Load configuration from various sources."""
        # Start with default configuration
        config_data = {
            "display": asdict(DisplayConfig()),
            "colors": asdict(ColorConfig()),
            "keyboard": asdict(KeyboardConfig())
        }
        
        # Load from config file if it exists
        config_file_data = self._load_from_file()
        if config_file_data:
            self._merge_config(config_data, config_file_data)
        
        # Override with environment variables
        self._load_from_env(config_data)
        
        # Create config objects
        return Config(
            display=DisplayConfig(**config_data["display"]),
            colors=ColorConfig(**config_data["colors"]),
            keyboard=KeyboardConfig(**config_data["keyboard"])
        )
    
    def _load_from_file(self) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file."""
        config_path = Path(self.CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.CONFIG_FILE}: {e}")
        return None
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Merge configuration dictionaries."""
        for key, value in override.items():
            if key in base:
                if isinstance(value, dict) and isinstance(base[key], dict):
                    self._merge_config(base[key], value)
                else:
                    base[key] = value
    
    def _load_from_env(self, config_data: Dict[str, Any]) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "RF_DEFAULT_MODE": ("display", "default_mode"),
            "RF_ENABLE_COLORS": ("display", "enable_colors", self._str_to_bool),
            "RF_ENABLE_INTERACTIVE": ("display", "enable_interactive", self._str_to_bool),
            "RF_ENABLE_COST_TRACKING": ("display", "enable_cost_tracking", self._str_to_bool),
            "RF_SHOW_TIMESTAMPS": ("display", "show_timestamps", self._str_to_bool),
            "RF_SHOW_MODEL_INFO": ("display", "show_model_info", self._str_to_bool),
            "RF_MAX_CONTENT_LENGTH": ("display", "max_content_length", int),
            "RF_TRUNCATE_LONG_CONTENT": ("display", "truncate_long_content", self._str_to_bool),
        }
        
        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section, key = mapping[0], mapping[1]
                converter = mapping[2] if len(mapping) > 2 else str
                try:
                    config_data[section][key] = converter(value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid value for {env_var}: {value}, error: {e}")
    
    @staticmethod
    def _str_to_bool(value: str) -> bool:
        """Convert string to boolean."""
        return value.lower() in ("true", "1", "yes", "on")
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_data = {
            "display": asdict(self.config.display),
            "colors": asdict(self.config.colors),
            "keyboard": asdict(self.config.keyboard)
        }
        
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def update_display_mode(self, mode: str) -> None:
        """Update the default display mode."""
        valid_modes = {"clean", "verbose", "debug"}
        if mode in valid_modes:
            self.config.display.default_mode = mode
            self.save_config()
    
    def get_config(self) -> Config:
        """Get the current configuration."""
        return self.config


# Global config manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get the global configuration."""
    return config_manager.get_config()


def update_display_mode(mode: str) -> None:
    """Update the global display mode."""
    config_manager.update_display_mode(mode)