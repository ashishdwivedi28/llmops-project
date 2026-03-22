"""Tests that KFP pipelines compile without errors.

These tests do NOT run the pipelines — they only compile them.
Running requires Vertex AI credentials and is done manually.
"""

import pytest


class TestPipelineCompilation:
    """Verify all KFP pipeline definitions are valid and compile successfully."""

    def test_evaluation_pipeline_compiles(self, tmp_path):
        """Evaluation pipeline should compile to a valid JSON spec."""
        try:
            from kfp import compiler

            from pipelines.evaluation_pipeline import evaluation_pipeline

            output = tmp_path / "eval.json"
            compiler.Compiler().compile(evaluation_pipeline, str(output))
            assert output.exists()
            assert output.stat().st_size > 100
        except ImportError:
            pytest.skip("kfp not installed — skipping pipeline compilation test")

    def test_rag_ingestion_pipeline_compiles(self, tmp_path):
        """RAG ingestion pipeline should compile to a valid JSON spec."""
        try:
            from kfp import compiler

            from pipelines.rag_ingestion_pipeline import rag_ingestion_pipeline

            output = tmp_path / "rag.json"
            compiler.Compiler().compile(rag_ingestion_pipeline, str(output))
            assert output.exists()
        except ImportError:
            pytest.skip("kfp not installed")

    def test_master_pipeline_compiles(self, tmp_path):
        """Master pipeline should compile to a valid JSON spec."""
        try:
            from kfp import compiler

            from pipelines.master_pipeline import master_pipeline

            output = tmp_path / "master.json"
            compiler.Compiler().compile(master_pipeline, str(output))
            assert output.exists()
        except ImportError:
            pytest.skip("kfp not installed")
