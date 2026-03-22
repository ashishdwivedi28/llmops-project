"""Abstract base class for all execution pipelines."""

from abc import ABC, abstractmethod


class BasePipeline(ABC):
    """All pipeline classes must inherit from this and implement execute()."""

    def __init__(self, config: dict) -> None:
        """Initialize with app config dict loaded from Firestore or config.json."""
        self.config = config
        self.model: str = config.get("active_model", config.get("model", "mock"))

    @abstractmethod
    def execute(self, user_input: str) -> str | tuple[str, int]:
        """Execute the pipeline and return a response.

        Args:
            user_input: The raw user message.

        Returns:
            Either a string response, or a tuple of (response, metadata_int).
            RAGPipeline returns (response_text, num_chunks_retrieved).
            LLMPipeline and AgentPipeline return response_text only.
        """

    def get_model(self) -> str:
        """Return the configured model name."""
        return self.model
