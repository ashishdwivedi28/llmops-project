import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def log_request(
    app_id: str,
    user_input: str,
    pipeline_executed: str,
    output: str,
    latency_ms: float,
    task_detection: dict,
    config: dict,
) -> None:
    """Log a structured record of a completed invoke request."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app_id": app_id,
        "pipeline_executed": pipeline_executed,
        "model": config.get("model", "unknown"),
        "latency_ms": round(latency_ms, 2),
        "task_detection": task_detection,
        "input_length": len(user_input),
        "output_length": len(output),
    }
    logger.info(f"INVOKE_LOG: {json.dumps(record)}")
