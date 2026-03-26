import json
import os

from kfp import compiler, dsl

# --- CONFIG ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
PIPELINE_ROOT = os.getenv(
    "GCS_PIPELINE_ROOT", f"gs://{PROJECT_ID}-vertex-pipelines/root"
)


@dsl.component(
    base_image="python:3.10",
    packages_to_install=["google-cloud-bigquery", "pandas", "db-dtypes", "pyarrow"],
)
def extract_logs_op(project_id: str, dataset_id: str, table_id: str) -> str:
    """Extracts latest logs from BigQuery as a JSON string."""
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id)
    # Fetch last 5 logs for demo purposes
    query = f"""
        SELECT user_input, output
        FROM `{project_id}.{dataset_id}.{table_id}`
        ORDER BY timestamp DESC
        LIMIT 5
    """
    try:
        df = client.query(query).to_dataframe()
        return df.to_json(orient="records")
    except Exception as e:
        print(f"Query failed: {e}")
        return "[]"


@dsl.component(
    base_image="python:3.10", packages_to_install=["google-cloud-aiplatform", "pandas"]
)
def evaluate_quality_op(logs_json: str, project_id: str, location: str) -> float:
    """LLM Judge component."""
    import vertexai
    from vertexai.generative_models import GenerativeModel

    if logs_json == "[]":
        return 0.0

    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.5-flash")

    logs = json.loads(logs_json)
    total_score = 0.0

    for log in logs:
        prompt = (
            f"Rate this response 1-10 for helpfulness.\n"
            f"User: {log.get('user_input', '')}\nBot: {log.get('output', '')}\n"
            f"Output ONLY the number."
        )
        try:
            resp = model.generate_content(prompt)
            score = float(resp.text.strip())
            total_score += score
        except:
            pass  # Skip invalid

    return total_score / len(logs) if logs else 0.0


@dsl.component(base_image="python:3.10")
def decision_op(avg_score: float, threshold: float) -> str:
    """Gates the pipeline based on quality."""
    if avg_score >= threshold:
        return f"✅ PASSED: Score {avg_score:.2f} >= {threshold}"
    # In a real CD pipeline, you might raise an error here to stop deployment
    return f"❌ FAILED: Score {avg_score:.2f} < {threshold}"


@dsl.pipeline(
    name="llmops-eval-pipeline",
    description="Automated Offline Evaluation Pipeline",
    pipeline_root=PIPELINE_ROOT,
)
def eval_pipeline(
    project_id: str = PROJECT_ID,
    location: str = LOCATION,
    bq_dataset: str = "llmops_logs",
    bq_table: str = "request_logs",
    min_score: float = 7.0,
):
    # 1. Extract Logs
    logs_task = extract_logs_op(
        project_id=project_id, dataset_id=bq_dataset, table_id=bq_table
    )

    # 2. Evaluate Quality
    score_task = evaluate_quality_op(
        logs_json=logs_task.output, project_id=project_id, location=location
    )

    # 3. Make Decision
    decision_op(avg_score=score_task.output, threshold=min_score)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=eval_pipeline, package_path="llmops_pipeline.json"
    )
    print("🚀 Pipeline compiled to llmops_pipeline.json")
