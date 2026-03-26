from unittest.mock import MagicMock, patch

from app.pipelines.agent_pipeline import (
    AgentPipeline,
    bigquery_query,
    calculate,
    list_gcs_files,
)


class TestAgentPipeline:
    def test_fallback_when_adk_missing(self):
        """Test that pipeline falls back to simple LLM when ADK fails or is missing."""
        config = {"model": "mock-model", "system_prompt": "You are a bot."}
        pipeline = AgentPipeline(config)

        # Mock _run_adk_agent to raise ImportError to simulate missing ADK
        with patch.object(
            pipeline, "_run_adk_agent", side_effect=ImportError("No ADK")
        ), patch(
            "app.services.llm_provider.generate", return_value="Fallback response"
        ) as mock_generate:
            result = pipeline.execute("Hello")

            assert result == "Fallback response"
            mock_generate.assert_called_once()
            args, _ = mock_generate.call_args
            assert "You are a bot." in args[0]
            assert "User: Hello" in args[0]

    def test_mock_model_returns_mock_response(self):
        """Test that 'mock' model returns a hardcoded string immediately."""
        config = {"model": "mock"}
        pipeline = AgentPipeline(config)
        result = pipeline.execute("Do something")
        assert "[MOCK AGENT]" in result


class TestAgentTools:
    def test_calculate_valid(self):
        assert calculate("2 + 2") == "4"
        assert calculate("10 * 5") == "50"
        assert calculate("(10 + 2) / 2") == "6.0"

    def test_calculate_invalid_chars(self):
        assert "Error" in calculate("import os")
        assert "Error" in calculate("2 + 2; rm -rf")

    def test_calculate_error(self):
        assert "error" in calculate("1 / 0").lower()

    @patch("google.cloud.bigquery.Client")
    @patch.dict("os.environ", {"BIGQUERY_PROJECT": "test-project"})
    def test_bigquery_query_success(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_job = mock_client.query.return_value
        mock_job.result.return_value = [{"col1": "val1", "col2": "val2"}]

        result = bigquery_query("SELECT * FROM table")
        assert "col1 | col2" in result
        assert "val1 | val2" in result

    def test_bigquery_query_safety(self):
        assert "Error" in bigquery_query("DELETE FROM table")
        assert "Error" in bigquery_query("DROP TABLE table")

    @patch.dict("os.environ", {}, clear=True)
    def test_bigquery_query_no_env(self):
        assert "BigQuery not configured" in bigquery_query("SELECT 1")

    @patch("google.cloud.storage.Client")
    def test_list_gcs_files_success(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_blob = MagicMock()
        mock_blob.name = "file1.txt"
        mock_client.list_blobs.return_value = [mock_blob]

        result = list_gcs_files("my-bucket")
        assert "Files in gs://my-bucket/:" in result
        assert "- file1.txt" in result

    @patch("google.cloud.storage.Client")
    def test_list_gcs_files_empty(self, mock_client_cls):
        mock_client = mock_client_cls.return_value
        mock_client.list_blobs.return_value = []

        result = list_gcs_files("my-bucket")
        assert "No files found" in result
