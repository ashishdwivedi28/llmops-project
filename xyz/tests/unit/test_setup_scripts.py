"""Tests for the setup scripts."""

from unittest.mock import MagicMock, patch

from scripts.seed_firestore_config import seed
from scripts.setup_bigquery import SCHEMA_REQUESTS, create_tables


class TestSetupScripts:
    """Test BigQuery and Firestore setup scripts."""

    def test_create_tables(self):
        """Should create dataset and tables with correct schema."""
        with patch("scripts.setup_bigquery.bigquery.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value

            create_tables("test-project")

            # Verify dataset creation
            mock_client.create_dataset.assert_called_once()
            dataset_arg = mock_client.create_dataset.call_args[0][0]
            # Dataset ID might vary based on how the lib parses it, check strict string match of full ID if possible
            # or check components
            assert dataset_arg.dataset_id == "llmops"
            assert dataset_arg.project == "test-project"

            # Verify table creation
            assert mock_client.create_table.call_count == 3

            # Check requests table schema
            table_calls = mock_client.create_table.call_args_list
            requests_call = table_calls[0]

            table_arg = requests_call[0][0]
            assert "requests" in table_arg.table_id
            assert table_arg.schema == SCHEMA_REQUESTS
            assert table_arg.time_partitioning.field == "timestamp"

    def test_seed_firestore(self):
        """Should seed Firestore with initial config."""
        with patch(
            "scripts.seed_firestore_config.firestore.Client"
        ) as mock_firestore_cls:
            mock_db = mock_firestore_cls.return_value

            # Setup mocks so that recursive collection/document calls return distinct mocks
            mock_col_configs = MagicMock()
            mock_doc_app = MagicMock()
            mock_col_prompts = MagicMock()
            mock_doc_prompt = MagicMock()

            mock_db.collection.return_value = mock_col_configs
            mock_col_configs.document.return_value = mock_doc_app
            mock_doc_app.collection.return_value = mock_col_prompts
            mock_col_prompts.document.return_value = mock_doc_prompt

            seed("test-project")

            # There are 4 apps. Each app has 1 prompt.
            # db.collection("configs").document(...) -> set() (4 times)
            # ... .collection("prompts").document(...) -> set() (4 times)

            assert mock_doc_app.set.call_count == 4
            assert mock_doc_prompt.set.call_count == 4
