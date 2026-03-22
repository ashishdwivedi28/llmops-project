# LLMOps Pipeline

A config-driven LLM orchestration system with RAG, Agents, and direct LLM support.

## Quick Start (local)

### 1. Backend
cd xyz
cp .env.example .env
# Edit .env and add your GOOGLE_CLOUD_PROJECT (for Vertex AI)
pip install -r requirements.txt
uvicorn app.main:app --reload
# Backend runs at http://localhost:8000

### 2. Frontend
cd final-frontend-llmops
cp .env.example .env.local
# .env.local already points to localhost:8000
npm install
npm run dev
# Frontend runs at http://localhost:3000

### 3. Test
curl http://localhost:8000/
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"app_id":"mock_app","user_input":"Hello"}'

## API Reference

### GET /
Returns backend health status.
Response: {"status": "ok", "message": "..."}

### POST /invoke
Main AI endpoint. Config-driven pipeline selection.
Request:  {"app_id": "default_llm", "user_input": "your question"}
Response: {"output": "...", "pipeline_executed": "llm", "latency_ms": 840, ...}

Valid app_id values:
- mock_app     → LLM pipeline, mock model (no API key needed)
- default_llm  → LLM pipeline, Gemini (Vertex AI)
- rag_bot      → RAG pipeline, Gemini (Vertex AI)
- code_agent   → Agent pipeline, Gemini (Vertex AI)

## Cloud Deployment

This project uses **Google Vertex AI** for Gemini models. No API keys are required for Gemini, but the Cloud Run service account must have `roles/aiplatform.user` permissions.

See CLOUD_SETUP.md for full GCP deployment instructions.

## Architecture

Request → FastAPI /invoke → Config Loader → Task Detector → Orchestrator
  → [LLM | RAG | Agent] Pipeline → LLM Provider (Vertex AI) → Response → Logger
