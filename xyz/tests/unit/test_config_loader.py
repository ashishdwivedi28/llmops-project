"""Tests for the config_loader module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestConfigLoader:
    """Test config loading logic."""

    def test_load_from_firestore_success(self):
        """Should load config from Firestore when FIRESTORE_PROJECT is set."""
        mock_config = {"pipeline": "llm", "active_prompt_version": "v2"}
        mock_prompt = {"system_prompt": "sys", "prompt_template": "tpl"}

        with patch("google.cloud.firestore.Client") as mock_firestore:
            # Mock the document structure
            mock_db = mock_firestore.return_value

            # First get() for config doc
            mock_doc_snapshot = MagicMock()
            mock_doc_snapshot.exists = True
            mock_doc_snapshot.to_dict.return_value = mock_config

            # Second get() for prompt doc
            mock_prompt_snapshot = MagicMock()
            mock_prompt_snapshot.exists = True
            mock_prompt_snapshot.to_dict.return_value = mock_prompt

            # Determine which get() returns what based on call order or arguments isn't strictly necessary
            # if we just mock the chain carefully, but for simplicity let's make the chain return these in order
            # However, the structure is:
            # db.collection("configs").document(app_id).get()
            # db.collection("configs").document(app_id).collection("prompts").document(v).get()

            # Let's mock the chain more precisely
            mock_config_doc = MagicMock()
            mock_config_doc.get.return_value = mock_doc_snapshot

            mock_prompt_doc = MagicMock()
            mock_prompt_doc.get.return_value = mock_prompt_snapshot

            def document_side_effect(arg):
                if arg == "test_app":
                    return mock_config_doc
                return MagicMock()  # default

            # This is tricky to mock perfectly due to chaining.
            # Let's simplify: existing code calls:
            # db.collection("configs").document(app_id).get()
            # db.collection("configs").document(app_id).collection("prompts").document(v).get()

            # We can mock the return values of the chain

            # To handle the two different get calls, we can use side_effect on the final .get()
            # But the path differs.
            # 1. db.collection("configs").document("test_app").get()
            # 2. db.collection("configs").document("test_app").collection("prompts").document("v2").get()

            # Let's verify the call arguments instead of complex return values if possible,
            # or use a more robust mock.

            # We'll just patch the internal _load_from_firestore to avoid deep mocking if feasible?
            # No, we should test the logic.

            # Let's try mocking the firestore module imported in the function
            with patch.dict("os.environ", {"FIRESTORE_PROJECT": "test-project"}):
                from utils.config_loader import invalidate_cache, load_config

                # Clear cache first
                invalidate_cache()

                # Setup the mock behavior
                # First call to get() (config)
                # Second call to get() (prompt)

                # We need to distinguish the document references.
                # The code does:
                # doc = db.collection("configs").document(app_id).get()
                # prompt_doc = db.collection("configs").document(app_id).collection("prompts").document(v).get()

                # We can mock the document() method to return different mocks based on args
                mock_config_ref = MagicMock()
                mock_config_ref.get.return_value = mock_doc_snapshot
                mock_config_ref.collection.return_value.document.return_value.get.return_value = (
                    mock_prompt_snapshot
                )

                mock_db.collection.return_value.document.return_value = mock_config_ref

                result = load_config("test_app")

                assert result["pipeline"] == "llm"
                assert result["system_prompt"] == "sys"
                assert result["active_prompt_version"] == "v2"

    def test_load_from_json_fallback(self, tmp_path: Path) -> None:
        """Should return config dict for a valid app_id from JSON (dev fallback)."""
        config_data = {"mock_app": {"pipeline": "llm", "model": "mock"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("utils.config_loader._LOCAL_CONFIG_PATH", config_file):
            # Ensure Firestore is not used
            with patch.dict("os.environ", {}, clear=True):
                from utils.config_loader import invalidate_cache, load_config

                invalidate_cache()

                result = load_config("mock_app")

        assert result["pipeline"] == "llm"
        assert result["model"] == "mock"

    def test_invalid_app_id_raises_key_error(self, tmp_path: Path) -> None:
        """Should raise KeyError for unknown app_id."""
        config_data = {"mock_app": {"pipeline": "llm"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("utils.config_loader._LOCAL_CONFIG_PATH", config_file):
            with patch.dict("os.environ", {}, clear=True):
                from utils.config_loader import invalidate_cache, load_config

                invalidate_cache()

                with pytest.raises(KeyError, match="not found"):
                    load_config("nonexistent")

    def test_missing_config_file_raises_file_not_found(self) -> None:
        """Should raise FileNotFoundError if config.json does not exist."""
        fake_path = Path("/tmp/nonexistent_config_file_xyz.json")
        with patch("utils.config_loader._LOCAL_CONFIG_PATH", fake_path):
            with patch.dict("os.environ", {}, clear=True):
                from utils.config_loader import invalidate_cache, load_config

                invalidate_cache()

                with pytest.raises(FileNotFoundError):
                    load_config("any_app")
