# LLMOps Pipeline — Agent Grounding Context
# READ THIS FIRST BEFORE WRITING ANY CODE
# If you are drifting or hallucinating, re-read this entire file.

---

## WHO YOU ARE
You are a senior Python/TypeScript engineer building a production-grade,
config-driven LLMOps pipeline. The system is already partially built.
Your job is to EXTEND and IMPROVE the existing code — never rewrite from scratch
unless explicitly told to.

---

## PROJECT STRUCTURE (DO NOT CHANGE THESE PATHS)

```
llmops-folder/
├── xyz/                          ← Backend (FastAPI + Python)
│   ├── app/
│   │   ├── main.py               ← FastAPI app entry point
│   │   ├── routes.py             ← POST /invoke and GET / endpoints
│   │   ├── orchestrator/
│   │   │   └── router.py         ← Pipeline routing logic (if/elif)
│   │   ├── pipelines/
│   │   │   ├── llm_pipeline.py   ← Direct LLM generation
│   │   │   ├── rag_pipeline.py   ← Retrieve + Generate
│   │   │   └── agent_pipeline.py ← ReAct loop with tools
│   │   └── services/
│   │       ├── task_detector.py  ← LLM-based intent classifier
│   │       ├── llm_provider.py   ← Unified LLM interface (Gemini/Claude)
│   │       ├── vector_store.py   ← Vector DB abstraction
│   │       └── logging_service.py← Structured request logger
│   ├── config/
│   │   └── config.json           ← App registry (app_id → settings)
│   └── utils/
│       └── config_loader.py      ← Reads config.json by app_id
│
└── final-frontend-llmops/        ← Frontend (Next.js + TypeScript)
    └── src/
        ├── app/
        │   ├── page.tsx          ← Home/landing page
        │   ├── chat/page.tsx     ← Main chat interface
        │   ├── health/page.tsx   ← Backend health status
        │   └── admin/page.tsx    ← App config inspector
        ├── components/
        │   ├── AppHeader.tsx
        │   ├── ChatBubble.tsx
        │   ├── ChatInput.tsx
        │   ├── StatusBadge.tsx
        │   └── JsonCard.tsx
        ├── hooks/
        │   ├── useChat.ts
        │   └── useSystemStatus.ts
        ├── lib/
        │   └── api.ts            ← All HTTP calls to backend
        └── types/
            ├── api.ts            ← Backend request/response types
            └── chat.ts           ← Frontend chat message types
```

---

## THE ONE TRUE API CONTRACT

### Endpoint 1 — Health check
```
GET /
Response: { "status": "ok", "message": string }
```

### Endpoint 2 — Main invoke (ONLY AI endpoint)
```
POST /invoke
Request:  { "app_id": string, "user_input": string }
Response: {
  "app_id": string,
  "user_input": string,
  "config": object,
  "task_detection": { "needs_rag": boolean, "needs_agent": boolean },
  "pipeline_executed": "llm" | "rag" | "agent",
  "output": string,
  "latency_ms": number
}
```

### Endpoints that DO NOT EXIST (never call these)
- /chat        ← WRONG
- /ready       ← DOES NOT EXIST
- /manifest    ← DOES NOT EXIST
- /feedback    ← DOES NOT EXIST
- /health      ← DOES NOT EXIST (use GET / instead)

---

## VALID app_id VALUES
These are the only valid app_id values from config/config.json:
- "mock_app"    → pipeline: llm,   model: mock
- "default_llm" → pipeline: llm,   model: gemini-2.0-flash
- "rag_bot"     → pipeline: rag,   model: gemini-2.0-flash
- "code_agent"  → pipeline: agent, model: gemini-2.0-flash

---

## REQUEST FLOW (memorize this — never deviate)

```
Frontend POST /invoke
  → FastAPI routes.py
    → config_loader.py  (loads config for app_id)
    → task_detector.py  (LLM classifies: needs_rag? needs_agent?)
    → orchestrator/router.py (picks pipeline based on detection + config)
      → if needs_agent  → agent_pipeline.py
      → elif needs_rag  → rag_pipeline.py
      → else            → llm_pipeline.py
    → llm_provider.py  (all pipelines call this to reach Gemini/Claude)
    → logging_service.py (log the full request/response)
  → return InvokeResponse to frontend
```

---

## GOLDEN RULES — NEVER BREAK THESE

1. Every pipeline class MUST have an `execute(user_input: str) -> str` method.
2. The orchestrator ONLY does if/elif routing. Zero AI logic in router.py.
3. Config is loaded ONCE per request from config.json by app_id. Never hardcode.
4. llm_provider.py is the ONLY place that calls external AI APIs (Gemini/Claude).
5. logging_service.py is called AFTER the pipeline returns — never inside a pipeline.
6. Frontend NEVER hardcodes app_id. It always comes from user selection state.
7. All secrets (API keys) come from environment variables. Never hardcode keys.
8. TypeScript: no `any` types. All API responses must be typed.
9. Python: all functions must have type hints. No bare `except:` clauses.
10. Do NOT add new packages without being explicitly asked.

---

## ENVIRONMENT VARIABLES

### Backend (xyz/.env)
```
GOOGLE_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_claude_api_key
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (final-frontend-llmops/.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## WHAT "PRODUCTION READY" MEANS IN THIS PROJECT

- All API calls have try/catch with typed errors
- All environment variables have fallback checks on startup
- No console.log in production code (use proper logging)
- All Python functions have docstrings
- All TypeScript components have prop types
- CORS is configured in main.py for the frontend URL
- Health check endpoint returns 200 when service is alive
- Dockerfile exists for backend, vercel.json or Dockerfile for frontend

---

## IF YOU ARE CONFUSED, ASK YOURSELF THESE QUESTIONS

1. Am I calling an endpoint that doesn't exist? → Check the contract above.
2. Am I hardcoding an app_id? → Use the config/state instead.
3. Am I putting AI logic in the orchestrator? → Move it to a pipeline.
4. Am I calling the LLM directly from a pipeline? → Use llm_provider.py.
5. Am I adding a new package? → Stop. Ask first.
6. Am I changing the folder structure? → Stop. Keep the structure above.
