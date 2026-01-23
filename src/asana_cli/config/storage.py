"""Configuration file storage."""

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "asana-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}

    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def set_token(token: str) -> None:
    """Set the API token in config file."""
    config = load_config()
    config["token"] = token
    save_config(config)


def set_workspace(workspace_gid: str) -> None:
    """Set the default workspace in config file."""
    config = load_config()
    config["workspace"] = workspace_gid
    save_config(config)


def clear_config() -> None:
    """Clear all configuration."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
