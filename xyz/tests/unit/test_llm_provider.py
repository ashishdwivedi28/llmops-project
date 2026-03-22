import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from app.services.llm_provider import generate


@pytest.fixture
def mock_vertexai():
    """Mock the entire vertexai library."""
    mock_generative_models = MagicMock()
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Gemini response"
    mock_model.generate_content.return_value = mock_response
    mock_generative_models.GenerativeModel.return_value = mock_model

    mock_vertexai_module = MagicMock()
    mock_vertexai_module.generative_models = mock_generative_models

    with patch.dict(
        sys.modules,
        {"vertexai": mock_vertexai_module, "vertexai.generative_models": mock_generative_models},
    ):
        yield mock_vertexai_module


@pytest.fixture
def mock_anthropic():
    """Mock the entire anthropic library."""
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Claude response")]
    mock_client.messages.create.return_value = mock_message

    mock_anthropic_module = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client

    with patch.dict(sys.modules, {"anthropic": mock_anthropic_module}):
        yield mock_anthropic_module


def test_generate_mock_returns_mock_response():
    """Verify that the mock model returns the expected mock response."""
    prompt = "Hello, world!"
    model = "mock"
    response = generate(prompt, model)
    assert "[MOCK RESPONSE]" in response
    assert prompt[:80] in response


def test_generate_unknown_model_raises_value_error():
    """Verify that an unknown model name raises a ValueError."""
    with pytest.raises(ValueError, match="Unknown model: 'invalid-model'"):
        generate("test prompt", "invalid-model")


@patch.dict(
    os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project", "GOOGLE_CLOUD_LOCATION": "us-central1"}
)
def test_generate_gemini_model_succeeds(mock_vertexai):
    """Test that the Gemini provider can be called successfully."""
    response = generate("test prompt", "gemini-1.5-pro")
    assert response == "Gemini response"
    mock_vertexai.init.assert_called_with(project="test-project", location="us-central1")
    mock_vertexai.generative_models.GenerativeModel.assert_called_with("gemini-1.5-pro")


@patch.dict(os.environ, {}, clear=True)
def test_generate_gemini_missing_project_id_raises_runtime_error(mock_vertexai):
    """Verify that a missing Google Cloud project ID raises a RuntimeError for Gemini."""
    with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_PROJECT environment variable is not set."):
        generate("test prompt", "gemini-pro")


@patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
def test_generate_claude_model_succeeds(mock_anthropic):
    """Test that the Claude provider can be called successfully."""
    response = generate("test prompt", "claude-3-opus-20240229")
    assert response == "Claude response"
    mock_anthropic.Anthropic.assert_called_with(api_key="test-key")


@patch.dict(os.environ, {}, clear=True)
def test_generate_claude_missing_api_key_raises_runtime_error(mock_anthropic):
    """Verify that a missing Anthropic API key raises a RuntimeError for Claude."""
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY environment variable is not set."):
        generate("test prompt", "claude-3-opus-20240229")


def test_generate_gemini_import_error():
    """Test that an ImportError is handled correctly for Gemini."""
    with patch.dict(sys.modules, {"vertexai": None}):
        with pytest.raises(RuntimeError, match="google-cloud-aiplatform package is not installed."):
            generate("test prompt", "gemini-1.5-pro")


def test_generate_claude_import_error():
    """Test that an ImportError is handled correctly for Claude."""
    with patch.dict(sys.modules, {"anthropic": None}):
        with pytest.raises(RuntimeError, match="anthropic package is not installed."):
            generate("test prompt", "claude-3-opus-20240229")
