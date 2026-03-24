"""Pipeline routing logic.

Priority rules:
1. If config.pipeline is set explicitly (not 'auto') → use that pipeline.
2. If config.pipeline is 'auto' → use task_detection result.
   - needs_agent=True → AgentPipeline
   - needs_rag=True   → RAGPipeline
   - default          → LLMPipeline

The orchestrator does ZERO AI logic. It only routes.
"""

import logging
from typing import Any, cast

from app.pipelines.agent_pipeline import AgentPipeline
from app.pipelines.base import BasePipeline
from app.pipelines.llm_pipeline import LLMPipeline
from app.pipelines.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

_PIPELINE_MAP: dict[str, Any] = {
    "llm": LLMPipeline,
    "rag": RAGPipeline,
    "agent": AgentPipeline,
}


def get_pipeline(config: dict[str, Any], detection: dict[str, Any]) -> BasePipeline:
    """Route to the correct pipeline.

    Args:
        config: App config from Firestore. Must contain 'pipeline' key.
        detection: Task detection result with needs_rag and needs_agent booleans.

    Returns:
        An instantiated pipeline with an execute() method.

    Raises:
        ValueError: If pipeline type is not recognized.
    """
    config_pipeline = config.get("pipeline", "auto")

    # Explicit pipeline routing
    if config_pipeline != "auto" and config_pipeline in _PIPELINE_MAP:
        logger.info(f"Using config-specified pipeline: {config_pipeline}")
        return cast(BasePipeline, _PIPELINE_MAP[config_pipeline](config))

    # Auto mode: use task detection
    if detection.get("needs_agent"):
        logger.info("Task detection: routing to AgentPipeline")
        return AgentPipeline(config)
    elif detection.get("needs_rag"):
        logger.info("Task detection: routing to RAGPipeline")
        return RAGPipeline(config)
    else:
        logger.info("Task detection: routing to LLMPipeline (default)")
        return LLMPipeline(config)
