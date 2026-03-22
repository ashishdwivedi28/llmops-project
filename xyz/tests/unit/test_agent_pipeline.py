from unittest.mock import patch

from app.pipelines.agent_pipeline import AgentPipeline


def test_agent_pipeline_calculator_tool_success():
    """Test that the AgentPipeline can successfully use the calculator tool."""
    config = {"model": "mock-agent-model", "max_iterations": 3}
    pipeline = AgentPipeline(config)
    user_input = "What is 2 + 2?"

    # Simulate the ReAct loop with mock LLM responses
    mock_llm_responses = [
        "Action: calculator\nInput: 2 + 2",
        "Observation: 4\nFinal Answer: The result is 4.",
    ]

    with patch("app.services.llm_provider.generate") as mock_generate:
        mock_generate.side_effect = mock_llm_responses

        result = pipeline.execute(user_input)

    assert result == "The result is 4."
    assert mock_generate.call_count == 2


def test_agent_pipeline_max_iterations_reached():
    """Test that the agent stops after reaching max_iterations."""
    config = {"model": "mock-agent-model", "max_iterations": 2}
    pipeline = AgentPipeline(config)
    user_input = "Some complex task."

    # Simulate a loop where the agent never finds a final answer
    mock_llm_responses = ["Thinking...", "Still thinking..."]

    with patch("app.services.llm_provider.generate") as mock_generate:
        mock_generate.side_effect = mock_llm_responses
        result = pipeline.execute(user_input)

    assert result == "Still thinking..."
    assert mock_generate.call_count == 2
