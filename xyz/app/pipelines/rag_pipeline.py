"""
RAG Pipeline — retrieves relevant chunks from Vertex AI RAG Engine corpus,
then generates an answer using the configured LLM model.
"""

import logging
import os
from typing import Any

from app.pipelines.base import BasePipeline
from app.services import llm_provider

logger = logging.getLogger(__name__)

NO_CONTEXT_NOTE = (
    "I could not find relevant information in the knowledge base "
    "for your question. Please ensure documents have been uploaded, "
    "or try rephrasing your question."
)


class RAGPipeline(BasePipeline):
    """Retrieval-Augmented Generation pipeline using Vertex AI RAG Engine."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize with app config from Firestore.

        Config must contain:
            - active_model or model: str
            - prompt_template: str (with {context} and {user_input} placeholders)
            - rag_corpus_id: str (Vertex AI RAG corpus resource name)
            - top_k: int (number of chunks to retrieve, default 3)
        """
        super().__init__(config)
        self.top_k = int(config.get("top_k", 3))
        self.corpus_id: str | None = config.get("rag_corpus_id", "")
        self.prompt_template: str = config.get(
            "prompt_template", "Context:\n{context}\n\nUser: {user_input}\nAssistant:"
        )
        self._rag_initialized = False

    def _init_rag(self) -> bool:
        """Lazy-initialize Vertex AI RAG Engine client."""
        if self._rag_initialized:
            return True

        project = os.getenv("FIRESTORE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("RAG_LOCATION", "us-central1")

        if not project or not self.corpus_id:
            logger.warning("RAG not configured: missing project or corpus_id.")
            return False

        try:
            import vertexai

            vertexai.init(project=project, location=location)
            self._rag_initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            return False

    def _retrieve_context(self, user_input: str) -> tuple[str, int]:
        """Retrieve relevant chunks from the RAG corpus.

        Returns:
            Tuple of (context_string, num_chunks_retrieved)
        """
        if not self._init_rag():
            return "", 0

        try:
            from vertexai.preview import rag

            response = rag.retrieval_query(
                rag_resources=[rag.RagResource(rag_corpus=self.corpus_id)],
                text=user_input,
                similarity_top_k=self.top_k,
                vector_distance_threshold=0.5,
            )

            chunks = []
            for context in response.contexts.contexts:
                source = context.source_uri or "document"
                text = context.text.strip()
                if text:
                    chunks.append(f"[Source: {source}]\n{text}")

            if not chunks:
                return "", 0

            context_str = "\n\n---\n\n".join(chunks)
            return context_str, len(chunks)

        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            return "", 0

    def execute(self, user_input: str) -> tuple[str, int]:
        """Execute the RAG pipeline.

        Args:
            user_input: The user's question.

        Returns:
            Tuple of (response_text, num_chunks_retrieved)
        """
        logger.info(f"RAGPipeline: starting retrieval for input: {user_input[:50]}...")
        context, num_chunks = self._retrieve_context(user_input)
        logger.info(f"RAGPipeline: retrieved {num_chunks} chunks.")

        if not context:
            # No documents found — still answer but warn
            logger.info("RAGPipeline: No context found, using fallback prompt.")
            prompt = self.prompt_template.format(
                context=NO_CONTEXT_NOTE, user_input=user_input
            )
        else:
            prompt = self.prompt_template.format(context=context, user_input=user_input)

        try:
            logger.info(f"RAGPipeline: generating answer with model {self.model}")
            response = llm_provider.generate(prompt, self.model)
            return response, num_chunks
        except Exception as e:
            logger.error(f"LLM generation failed in RAG pipeline: {e}")
            raise RuntimeError(f"RAG pipeline generation failed: {str(e)}") from e
