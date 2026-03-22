"""Tests for the config_loader module."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


class TestConfigLoader:
    """Test config loading from JSON (dev fallback)."""

    def test_load_valid_app_id(self, tmp_path: Path) -> None:
        """Should return config dict for a valid app_id."""
        config_data = {"mock_app": {"pipeline": "llm", "model": "mock"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("utils.config_loader.CONFIG_PATH", config_file):
            # Ensure Firestore is not used
            with patch.dict("os.environ", {}, clear=True):
                from utils.config_loader import load_config

                result = load_config("mock_app")

        assert result["pipeline"] == "llm"
        assert result["model"] == "mock"

    def test_invalid_app_id_raises_key_error(self, tmp_path: Path) -> None:
        """Should raise KeyError for unknown app_id."""
        config_data = {"mock_app": {"pipeline": "llm"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("utils.config_loader.CONFIG_PATH", config_file):
            from utils.config_loader import load_config

            with pytest.raises(KeyError, match="not found"):
                load_config("nonexistent")

    def test_missing_config_file_raises_file_not_found(self) -> None:
        """Should raise FileNotFoundError if config.json does not exist."""
        fake_path = Path("/tmp/nonexistent_config_file_xyz.json")
        with patch("utils.config_loader.CONFIG_PATH", fake_path):
            from utils.config_loader import load_config

            with pytest.raises(FileNotFoundError):
                load_config("any_app")
