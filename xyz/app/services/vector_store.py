from abc import ABC, abstractmethod


class VectorStore(ABC):
    """
    Abstract Base Class for Vector Search.
    Ensures a unified interface for document retrieval.
    """

    @abstractmethod
    def search(self, query: str, limit: int = 3) -> list[str]:
        """
        Retrieves relevant document chunks for a given query.

        Args:
            query (str): The search query.
            limit (int): Number of chunks to retrieve.

        Returns:
            List[str]: A list of relevant document strings.
        """
        pass


class MockVectorStore(VectorStore):
    """
    Mock implementation for testing the RAG pipeline.
    Returns static content based on simple keyword matching.
    """

    def search(self, query: str, limit: int = 3) -> list[str]:
        # Simulated "Retrieved" documents
        mock_docs = [
            "LLMOps is the practice of managing the lifecycle of large language models in production.",
            "Retrieval-Augmented Generation (RAG) combines search with generation for better accuracy.",
            "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python.",
        ]
        # Return a few docs to simulate retrieval
        return mock_docs[:limit]


class VectorStoreFactory:
    """Factory to get the correct Vector Store instance."""

    @staticmethod
    def get_store(store_type: str = "mock") -> VectorStore:
        if store_type == "mock":
            return MockVectorStore()
        # In the future: return VertexAISearchStore(), PineconeStore(), etc.
        return MockVectorStore()
