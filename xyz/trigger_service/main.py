"""
Trigger Service — Cloud Run function that receives events and submits
the master pipeline to Vertex AI with the correct trigger_type.

Receives:
  - Pub/Sub push from GCS (document upload)    → trigger_type=rag_ingestion
  - HTTP POST from Cloud Scheduler (nightly)   → trigger_type=evaluation
  - HTTP POST (manual experiment request)      → trigger_type=experiment

This is the bridge between GCP events and Vertex AI Pipelines.
"""

import base64
import json
import logging
import os

import google.cloud.aiplatform as aip
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
LOCATION = os.environ.get("PIPELINE_LOCATION", "us-central1")
PIPELINE_ROOT = os.environ.get("PIPELINE_ROOT_GCS", "")
MASTER_PIPELINE_URI = os.environ.get("MASTER_PIPELINE_URI", "")
PIPELINE_SA = os.environ.get("PIPELINE_SA", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


def submit_master_pipeline(trigger_type: str, app_id: str, extra_params: dict) -> str:
    """Submit the master pipeline to Vertex AI Pipelines."""
    aip.init(project=PROJECT_ID, location=LOCATION)

    params = {
        "trigger_type": trigger_type,
        "app_id": app_id,
        "project_id": PROJECT_ID,
        "pipeline_root": PIPELINE_ROOT,
        "google_api_key": GOOGLE_API_KEY,
        **extra_params,
    }

    job = aip.PipelineJob(
        display_name=f"master-{trigger_type}-{app_id}",
        template_uri=MASTER_PIPELINE_URI,
        pipeline_root=PIPELINE_ROOT,
        parameter_values=params,
        enable_caching=False,
    )
    job.submit(service_account=PIPELINE_SA)
    logger.info(f"Pipeline submitted: {trigger_type} for {app_id}")
    return job.name


@app.route("/gcs-upload", methods=["POST"])
def handle_gcs_upload():
    """Handle Pub/Sub push for GCS document uploads → trigger RAG ingestion."""
    try:
        envelope = request.get_json()
        if not envelope or "message" not in envelope:
            return jsonify({"error": "Invalid Pub/Sub message"}), 400

        message_data = base64.b64decode(envelope["message"]["data"]).decode("utf-8")
        gcs_event = json.loads(message_data)

        gcs_uri = f"gs://{gcs_event['bucket']}/{gcs_event['name']}"

        # Determine app_id from folder structure (bucket/app_id/filename.pdf)
        path_parts = gcs_event["name"].split("/")
        app_id = path_parts[0] if len(path_parts) > 1 else "rag_bot"

        logger.info(f"GCS upload detected: {gcs_uri} → app_id={app_id}")

        job_name = submit_master_pipeline(
            trigger_type="rag_ingestion",
            app_id=app_id,
            extra_params={
                "gcs_document_uri": gcs_uri,
                "document_display_name": gcs_event["name"].split("/")[-1],
            },
        )
        return jsonify({"status": "submitted", "job": job_name}), 200

    except Exception as e:
        logger.error(f"GCS upload handler error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/trigger", methods=["POST"])
def handle_trigger():
    """Handle Cloud Scheduler and manual triggers."""
    try:
        data = request.get_json() or {}
        trigger_type = data.get("trigger_type", "evaluation")
        app_id = data.get("app_id", "default_llm")
        extra = {k: v for k, v in data.items() if k not in ("trigger_type", "app_id")}

        job_name = submit_master_pipeline(trigger_type, app_id, extra)
        return jsonify({"status": "submitted", "job": job_name}), 200

    except Exception as e:
        logger.error(f"Trigger handler error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "llmops-trigger"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
