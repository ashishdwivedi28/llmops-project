import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.orchestrator.router import get_pipeline
from app.services.logging_service import log_request
from app.services.task_detector import detect
from utils.config_loader import load_config

router = APIRouter()


class InvokeRequest(BaseModel):
    app_id: str
    user_input: str


class TaskDetectionResult(BaseModel):
    needs_rag: bool
    needs_agent: bool


class InvokeResponse(BaseModel):
    app_id: str
    user_input: str
    config: dict[str, Any]
    task_detection: TaskDetectionResult
    pipeline_executed: str
    output: str
    latency_ms: float


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_pipeline(request: InvokeRequest) -> InvokeResponse:
    start_time = time.time()

    try:
        # 1. Load config
        try:
            config = load_config(request.app_id)
        except KeyError as e:
            raise HTTPException(
                status_code=404, detail=f"App ID '{request.app_id}' not found."
            ) from e
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail="Configuration file missing.") from e

        # 2. Task Detection
        try:
            # We pass the model from config to task detector
            model_name = config.get("model", "mock")
            detection_data = detect(request.user_input, model_name)
        except Exception:
            # Fallback is handled inside detect(), but extra safety here
            detection_data = {"needs_rag": False, "needs_agent": False}

        # 3. Route to Pipeline
        try:
            pipeline = get_pipeline(config, detection_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}") from e

        # 4. Execute Pipeline
        try:
            output = pipeline.execute(request.user_input)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Pipeline execution failed: {str(e)}"
            ) from e

        # The AgentPipeline may return a tuple (response, status_code)
        final_output = output[0] if isinstance(output, tuple) else output

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # 5. Logging
        try:
            log_request(
                app_id=request.app_id,
                user_input=request.user_input,
                pipeline_executed=type(pipeline).__name__,
                output=final_output,
                latency_ms=latency_ms,
                task_detection=detection_data,
                config=config,
            )
        except Exception as e:
            # Don't fail the request if logging fails, but log the error
            print(f"Logging failed: {e}")

        return InvokeResponse(
            app_id=request.app_id,
            user_input=request.user_input,
            config=config,
            task_detection=TaskDetectionResult(**detection_data),
            pipeline_executed=type(pipeline).__name__,
            output=final_output,
            latency_ms=latency_ms,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}") from e
