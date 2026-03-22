"""Tests for the orchestrator routing logic."""

from app.orchestrator.router import get_pipeline
from app.pipelines.agent_pipeline import AgentPipeline
from app.pipelines.llm_pipeline import LLMPipeline
from app.pipelines.rag_pipeline import RAGPipeline


class TestOrchestrator:
    """Orchestrator routes correctly based on config and detection."""

    def test_explicit_llm_pipeline_from_config(self, mock_config, mock_detection_rag):
        """Config pipeline=llm overrides task detection needs_rag=True."""
        mock_config["pipeline"] = "llm"
        pipeline = get_pipeline(mock_config, mock_detection_rag)
        assert isinstance(pipeline, LLMPipeline)

    def test_explicit_rag_pipeline_from_config(self, rag_config, mock_detection_llm):
        """Config pipeline=rag overrides task detection needs_rag=False."""
        pipeline = get_pipeline(rag_config, mock_detection_llm)
        assert isinstance(pipeline, RAGPipeline)

    def test_explicit_agent_pipeline_from_config(self, agent_config, mock_detection_llm):
        """Config pipeline=agent overrides task detection."""
        pipeline = get_pipeline(agent_config, mock_detection_llm)
        assert isinstance(pipeline, AgentPipeline)

    def test_auto_routes_to_rag_when_needs_rag(self, mock_config, mock_detection_rag):
        """Auto mode: needs_rag=True → RAGPipeline."""
        mock_config["pipeline"] = "auto"
        pipeline = get_pipeline(mock_config, mock_detection_rag)
        assert isinstance(pipeline, RAGPipeline)

    def test_auto_routes_to_agent_when_needs_agent(self, mock_config, mock_detection_agent):
        """Auto mode: needs_agent=True → AgentPipeline (agent > rag priority)."""
        mock_config["pipeline"] = "auto"
        pipeline = get_pipeline(mock_config, mock_detection_agent)
        assert isinstance(pipeline, AgentPipeline)

    def test_auto_defaults_to_llm(self, mock_config, mock_detection_llm):
        """Auto mode: no special needs → LLMPipeline."""
        mock_config["pipeline"] = "auto"
        pipeline = get_pipeline(mock_config, mock_detection_llm)
        assert isinstance(pipeline, LLMPipeline)

    def test_unknown_pipeline_in_config_falls_back_to_auto(self, mock_config, mock_detection_rag):
        """Unknown pipeline type falls through to auto mode."""
        mock_config["pipeline"] = "unknown_pipeline_type"
        pipeline = get_pipeline(mock_config, mock_detection_rag)
        # Should fall through to auto-mode → rag because needs_rag=True
        assert isinstance(pipeline, RAGPipeline)
