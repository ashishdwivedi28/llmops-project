"""
Structured logging to BigQuery. Falls back to stdout if BigQuery is unavailable.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_BQ_CLIENT = None
_BQ_TABLE = None


def _get_bq_client() -> tuple[Any, str | None]:
    global _BQ_CLIENT, _BQ_TABLE
    if _BQ_CLIENT is None:
        project = os.getenv("BIGQUERY_PROJECT")
        if project:
            try:
                from google.cloud import bigquery  # type: ignore

                _BQ_CLIENT = bigquery.Client(project=project)
                _BQ_TABLE = f"{project}.llmops.requests"
            except Exception as e:
                logger.warning(f"BigQuery init failed: {e}. Using stdout logging.")
    return _BQ_CLIENT, _BQ_TABLE


def log_request(
    app_id: str,
    user_input: str,
    output: str,
    pipeline_executed: str,
    latency_ms: float,
    task_detection: dict,
    config: dict,
    session_id: str | None = None,
    retrieved_chunks: int | None = None,
    guardrail_pass: bool | None = None,
    usage: dict | None = None,
) -> None:
    """Log a completed invoke request to BigQuery (or stdout as fallback)."""

    usage = usage or {}
    
    now = datetime.now(timezone.utc)
    row = {
        "timestamp": now.isoformat(),
        "app_id": app_id,
        "session_id": session_id,
        "user_input": user_input[:2000],  # cap at 2000 chars
        "output": output[:4000],  # cap at 4000 chars
        "pipeline_executed": pipeline_executed,
        "model": str(config.get("active_model", config.get("model", "unknown"))),
        "prompt_version": str(config.get("active_prompt_version", "unknown")),
        "latency_ms": round(latency_ms, 2),
        "input_length": len(user_input),
        "output_length": len(output),
        "needs_rag": bool(task_detection.get("needs_rag", False)),
        "needs_agent": bool(task_detection.get("needs_agent", False)),
        "retrieved_chunks": retrieved_chunks,
        "guardrail_pass": guardrail_pass,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_cost": float(usage.get("total_cost", 0.0)),
    }

    client, table = _get_bq_client()

    if client and table:
        try:
            # client is Any, but mypy might infer it as None from global init
            bq_client: Any = client
            errors = bq_client.insert_rows_json(table, [row])
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
        except Exception as e:
            logger.error(f"BigQuery insert failed: {e}")
            _log_to_stdout(row)
    else:
        _log_to_stdout(row)


def _log_to_stdout(row: dict) -> None:
    logger.info(f"INVOKE_LOG: {json.dumps(row)}")
