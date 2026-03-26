"""Tests for the LLM pipeline."""

from unittest.mock import patch

import pytest

from app.pipelines.llm_pipeline import LLMPipeline


class TestLLMPipeline:
    """LLMPipeline calls llm_provider and formats the prompt correctly."""

    def test_execute_calls_llm_provider(self, mock_config):
        """execute() should call llm_provider.generate with formatted prompt."""
        mock_config["prompt_template"] = "User: {user_input}"

        with patch(
            "app.pipelines.llm_pipeline.llm_provider.generate",
            return_value="Test response",
        ) as mock_gen:
            pipeline = LLMPipeline(mock_config)
            result = pipeline.execute("Hello")

        assert result == "Test response"
        call_args = mock_gen.call_args
        assert "Hello" in call_args[0][0]
        # Expect 'mock' because the fixture mock_config has model='mock'
        assert call_args[0][1] == "mock"

    def test_execute_uses_model_from_config(self, mock_config):
        """Model name comes from active_model field in config."""
        mock_config["active_model"] = "gemini"
        with patch(
            "app.pipelines.llm_pipeline.llm_provider.generate", return_value="ok"
        ) as mock_gen:
            LLMPipeline(mock_config).execute("test")

        assert mock_gen.call_args[0][1] == "gemini"

    def test_execute_raises_on_provider_failure(self, mock_config):
        """RuntimeError from llm_provider should propagate."""
        with patch(
            "app.pipelines.llm_pipeline.llm_provider.generate",
            side_effect=RuntimeError("API down"),
        ), pytest.raises(RuntimeError, match="API down"):
            LLMPipeline(mock_config).execute("Hello")
