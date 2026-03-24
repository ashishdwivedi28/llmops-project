# PHASE 2 — What Is Missing & The Complete Architecture Plan
# Read this before running any prompts.
# Written from the perspective of a senior LLMOps architect.

==========================================================================
WHAT YOU BUILT IN PHASE 1 (WHAT YOU HAVE)
==========================================================================

  FastAPI backend with POST /invoke
  Config-driven pipeline routing (llm / rag / agent)
  Basic LLM provider abstraction (Gemini + Claude)
  Next.js frontend with app selector and metadata display
  GitHub Actions CI/CD
  Cloud Run deployment (backend + frontend)
  Terraform for GCP resources

This is a working skeleton. A user can send a request and get a response.
But it is NOT yet an LLMOps pipeline — it is a single-serving LLM API.

==========================================================================
WHAT IS MISSING (THE GAP BETWEEN SKELETON AND INDUSTRY STANDARD)
==========================================================================

Gap 1 — RAG pipeline has no real storage
  Your rag_pipeline.py exists but has no real vector database connected.
  Documents are not ingested anywhere. There is no index to search.
  FIX: Connect Vertex AI RAG Engine (managed vector store) + KFP ingestion pipeline.

Gap 2 — No automation — everything is manual
  If HR uploads a new document, NOTHING happens automatically.
  If evaluation finds a bad prompt, nothing changes automatically.
  FIX: KFP pipelines triggered by GCS events + Cloud Scheduler.

Gap 3 — Logging writes to console only
  logging_service.py prints to stdout. That data is gone after the request.
  There is no queryable history of requests, outputs, latencies, or quality scores.
  FIX: Write every request to BigQuery with a fixed schema.

Gap 4 — No evaluation — you do not know if your system is good
  You have no way to measure if your LLM responses are correct, relevant, or safe.
  You cannot compare two models or two prompt versions against each other.
  FIX: KFP evaluation pipeline using LLM-as-judge (Gemini evaluates Gemini output).

Gap 5 — Config is a static JSON file
  config.json is committed to git. To change a prompt, you redeploy.
  There is no versioning, no rollback, no A/B testing between prompt versions.
  FIX: Move config to Firestore. Each app_id has a live document. 
       Prompt versions are stored as sub-documents. Active version is a pointer.

Gap 6 — No model performance comparison
  If Gemini performs poorly on rag_bot, you have no way to test Claude against it.
  FIX: Experiment pipeline that runs both models on the same input set,
       scores them with LLM-as-judge, and writes comparison to BigQuery.

Gap 7 — Task detection is binary and static
  Task detector returns needs_rag / needs_agent. It cannot select between
  prompt_v1 vs prompt_v2 or gemini vs claude for the same app.
  FIX: Extend task detector to also read active prompt version from Firestore
       and support model selection based on evaluation scores.

Gap 8 — ADK agent has no real tools
  agent_pipeline.py has a mock calculator. No real tools exist.
  FIX: Add BigQuery query tool, GCS file reader tool, structured as ADK tools.

Gap 9 — No API Gateway (authentication at scale)
  Cloud Run allows unauthenticated requests. Anyone can call your API.
  FIX: Cloud Endpoints or API Gateway in front of Cloud Run.
       For MVP: Firebase Auth token validation in FastAPI middleware.

Gap 10 — No monitoring or alerting
  You cannot see when latency spikes, when error rates increase,
  or when model quality degrades.
  FIX: Cloud Monitoring dashboards + alert policies on BigQuery eval scores.

==========================================================================
COMPLETE PHASE 2 ARCHITECTURE
==========================================================================

SERVING PATH (real-time, unchanged from Phase 1 except improvements):

  User → API Gateway (Firebase Auth middleware)
       → FastAPI /invoke
       → Config loaded from Firestore (not JSON file)
       → Task Detector (LLM + reads active prompt version from Firestore)
       → Orchestrator → [LLM / RAG / ADK Agent] Pipeline
       → Model Abstraction (Gemini or Claude, from config)
       → Guardrails
       → BigQuery Logger (every request logged)
       → Response to user

AUTOMATION PATH (KFP on Vertex AI Pipelines):

  Pipeline 1 — RAG Ingestion (trigger: GCS upload via Pub/Sub)
    GCS file upload
    → KFP: load_document_component
    → KFP: chunk_and_embed_component (Vertex AI text-embedding-004)
    → KFP: upsert_to_rag_engine_component (Vertex AI RAG Engine corpus)

  Pipeline 2 — Nightly Evaluation (trigger: Cloud Scheduler, 2am)
    → KFP: fetch_logs_component (BigQuery → last 24h)
    → KFP: llm_judge_component (Gemini scores each response 1-5)
    → KFP: write_scores_component (BigQuery evaluation_results table)
    → KFP: update_config_component (if score < threshold → promote better prompt)

  Pipeline 3 — Model Experiment (trigger: manual or scheduled weekly)
    → KFP: load_test_set_component (GCS test questions)
    → KFP: run_model_a_component (e.g., Gemini Flash)
    → KFP: run_model_b_component (e.g., Gemini Pro or Claude)
    → KFP: compare_and_score_component (LLM-as-judge for both)
    → KFP: write_experiment_results_component (BigQuery)
    → KFP: update_active_model_component (if model B wins → update Firestore)

CONFIG MANAGEMENT (Firestore document structure):

  configs/{app_id}
    active_prompt_version: "v3"
    active_model: "gemini"
    pipeline: "rag"
    top_k: 3
    evaluation_threshold: 4.0

  configs/{app_id}/prompts/{version}
    version: "v3"
    system_prompt: "..."
    prompt_template: "..."
    created_at: timestamp
    score: 4.3
    status: "active"  # or "candidate" or "retired"

  configs/{app_id}/experiments/{experiment_id}
    model_a: "gemini-flash"
    model_b: "claude-haiku"
    score_a: 4.1
    score_b: 4.6
    winner: "claude-haiku"
    promoted: true

BIGQUERY TABLES:

  llmops.requests          ← every /invoke call
  llmops.evaluation_results ← nightly LLM judge scores
  llmops.experiments       ← model A vs model B results
  llmops.prompt_history    ← record of prompt version changes

==========================================================================
HOW THE PIECES CONNECT — THE FULL STORY
==========================================================================

Step 1: HR team uploads policy.pdf to gs://company-docs/hr_bot/

Step 2: GCS fires Pub/Sub event → Eventarc triggers KFP RAG Ingestion pipeline

Step 3: KFP pipeline runs:
  - Reads PDF from GCS
  - Chunks into 500-char pieces with 50-char overlap
  - Embeds each chunk with Vertex AI text-embedding-004
  - Upserts to Vertex AI RAG Engine corpus tagged for hr_bot

Step 4: User asks "What is our maternity leave policy?"

Step 5: FastAPI loads hr_bot config from Firestore
  - Gets active_prompt_version = "v3"
  - Gets active_model = "gemini"
  - Gets rag_corpus_id = "projects/.../corpora/hr_bot_corpus"

Step 6: Task detector runs → needs_rag = true

Step 7: RAG pipeline calls Vertex AI RAG Engine with the corpus_id
  - Retrieves top 3 chunks from hr_bot corpus ONLY
  - Builds prompt using prompt v3 template
  - Calls Gemini with grounded context

Step 8: Response returned to user. Full row logged to BigQuery.

Step 9: At 2am, KFP Evaluation pipeline runs:
  - Fetches last 24h of hr_bot logs from BigQuery
  - Gemini Pro (judge model) scores each response
  - Average score = 3.7 (below threshold 4.0)
  - Pipeline finds prompt_v4 in Firestore with status=candidate
  - Promotes v4 to active

Step 10: Next user request to hr_bot AUTOMATICALLY uses prompt_v4.
  No redeployment. No human action needed.

==========================================================================
EXECUTION ORDER FOR PHASE 2
==========================================================================

Run A:  BigQuery schema + Firestore config migration
Run B:  RAG pipeline with Vertex AI RAG Engine
Run C:  ADK agent with real tools
Run D:  KFP pipeline 1 — RAG ingestion
Run E:  KFP pipeline 2 — Evaluation (LLM-as-judge)
Run F:  KFP pipeline 3 — Model experiment
Run G:  API Gateway (Firebase Auth middleware)
Run H:  Terraform additions for new GCP resources
Run I:  Cloud Monitoring + alerts setup

Do them in this order. Each run depends on the previous.
