from unittest.mock import patch

import pytest

from app.services.task_detector import detect


@pytest.mark.parametrize(
    ("llm_response, expected_rag, expected_agent"),
    [
        ("NEEDS_RAG", True, False),
        ("NEEDS_AGENT", False, True),
        ('{"needs_rag": true, "needs_agent": false}', True, False),
        ('{"needs_agent": true, "needs_rag": false}', False, True),
        ("Something else", False, False),
        ("", False, False),
    ],
)
@patch("app.services.task_detector.llm_provider.generate")
def test_detect_parses_llm_response(mock_llm_generate, llm_response, expected_rag, expected_agent):
    """Verify that the task detector correctly parses various LLM responses."""
    mock_llm_generate.return_value = llm_response
    result = detect("some user input", "mock-model")
    assert result["needs_rag"] == expected_rag
    assert result["needs_agent"] == expected_agent


@patch("app.services.task_detector.llm_provider.generate")
def test_detect_llm_failure_returns_fallback(mock_llm_generate):
    """Verify that if the LLM call fails, the detector returns a default fallback."""
    mock_llm_generate.side_effect = Exception("API error")
    result = detect("some user input", "mock-model")
    assert result["needs_rag"] is False
    assert result["needs_agent"] is False


@patch("app.services.task_detector.llm_provider.generate")
def test_detect_json_parsing_error_returns_fallback(mock_llm_generate):
    """Verify that a JSON parsing error in the LLM response leads to a fallback."""
    mock_llm_generate.return_value = '{"invalid_json": true'
    result = detect("some user input", "mock-model")
    assert result["needs_rag"] is False
    assert result["needs_agent"] is False
