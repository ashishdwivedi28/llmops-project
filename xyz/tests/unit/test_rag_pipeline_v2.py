import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from app.pipelines.rag_pipeline import RAGPipeline


class TestRAGPipeline:
    @pytest.fixture
    def mock_config(self):
        return {
            "model": "gemini-1.5-flash",
            "rag_corpus_id": "projects/123/locations/us-central1/ragCorpora/456",
            "top_k": 2,
            "prompt_template": "Context:\n{context}\n\nUser: {user_input}",
        }

    @patch("app.pipelines.rag_pipeline.llm_provider")
    def test_rag_pipeline_success(self, mock_llm_provider, mock_config):
        # Create mocks
        mock_vertexai = MagicMock()
        mock_preview = mock_vertexai.preview
        mock_rag_module = MagicMock()
        mock_preview.rag = mock_rag_module

        # Mock retrieval response
        mock_context1 = MagicMock()
        mock_context1.text = "This is chunk 1"
        mock_context1.source_uri = "doc1"

        mock_context2 = MagicMock()
        mock_context2.text = "This is chunk 2"
        mock_context2.source_uri = "doc2"

        mock_response = MagicMock()
        # Explicitly mock the intermediate object
        mock_response_contexts = MagicMock()
        mock_response_contexts.contexts = [mock_context1, mock_context2]
        mock_response.contexts = mock_response_contexts

        mock_rag_module.retrieval_query.return_value = mock_response

        # Mock LLM generation
        mock_llm_provider.generate.return_value = "Answer based on context"

        # Patch sys.modules AND os.environ
        # Important: Ensure vertexai.preview is the SAME mock object as mock_vertexai.preview
        with patch.dict(
            sys.modules,
            {
                "vertexai": mock_vertexai,
                "vertexai.preview": mock_preview,
                "vertexai.preview.rag": mock_rag_module,
            },
        ):
            with patch.dict(
                os.environ,
                {"GOOGLE_CLOUD_PROJECT": "test-project", "RAG_LOCATION": "us-central1"},
            ):
                # Initialize pipeline
                pipeline = RAGPipeline(mock_config)

                # Execute
                response, chunks_count = pipeline.execute("test question")

                # Verify
                assert response == "Answer based on context"
                assert chunks_count == 2

                # Check retrieval call
                mock_rag_module.retrieval_query.assert_called_once()
                call_args = mock_rag_module.retrieval_query.call_args
                assert call_args.kwargs["text"] == "test question"
                assert call_args.kwargs["similarity_top_k"] == 2

                # Check prompt construction
                expected_context = "[Source: doc1]\nThis is chunk 1\n\n---\n\n[Source: doc2]\nThis is chunk 2"
                mock_llm_provider.generate.assert_called_once()
                args, _ = mock_llm_provider.generate.call_args
                prompt = args[0]
                assert expected_context in prompt
                assert "User: test question" in prompt

    @patch("app.pipelines.rag_pipeline.llm_provider")
    def test_rag_pipeline_no_context(self, mock_llm_provider, mock_config):
        mock_vertexai = MagicMock()
        mock_preview = mock_vertexai.preview
        mock_rag_module = MagicMock()
        mock_preview.rag = mock_rag_module

        # Mock empty retrieval
        mock_response = MagicMock()
        mock_response_contexts = MagicMock()
        mock_response_contexts.contexts = []
        mock_response.contexts = mock_response_contexts

        mock_rag_module.retrieval_query.return_value = mock_response

        mock_llm_provider.generate.return_value = "I don't know"

        with patch.dict(
            sys.modules,
            {
                "vertexai": mock_vertexai,
                "vertexai.preview": mock_preview,
                "vertexai.preview.rag": mock_rag_module,
            },
        ), patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            pipeline = RAGPipeline(mock_config)
            response, chunks_count = pipeline.execute("test question")

            assert chunks_count == 0
            assert response == "I don't know"

            # Verify warning note in prompt
            mock_llm_provider.generate.assert_called_once()
            args, _ = mock_llm_provider.generate.call_args
            prompt = args[0]
            assert "I could not find relevant information" in prompt

    @patch("app.pipelines.rag_pipeline.llm_provider")
    def test_initialization_missing_config(self, mock_llm_provider):
        config = {"model": "mock"}  # Missing rag_corpus_id
        mock_llm_provider.generate.return_value = "Mock response"

        pipeline = RAGPipeline(config)

        mock_vertexai = MagicMock()
        with patch.dict(sys.modules, {"vertexai": mock_vertexai}):
            with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
                # It won't even call vertexai.init because of check
                response, chunks = pipeline.execute("test")
                assert chunks == 0
                mock_vertexai.init.assert_not_called()
