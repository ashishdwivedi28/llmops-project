import json
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"


def load_config(app_id: str) -> dict[str, Any]:
    """Load configuration for a given app_id from config.json.

    Raises:
        KeyError: If app_id is not found in config.
        FileNotFoundError: If config.json does not exist.
    """
    with open(CONFIG_PATH) as f:
        config: dict[str, dict[str, Any]] = json.load(f)
    if app_id not in config:
        raise KeyError(f"app_id '{app_id}' not found. Valid ids: {list(config.keys())}")
    return config[app_id]
