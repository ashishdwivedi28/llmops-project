# LLMOps Frontend (Next.js)

Production-ready frontend for testing your LLMOps backend end-to-end.

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- API integration with FastAPI backend (`GET /`, `POST /invoke`)

## Routes

- `/chat` — ChatGPT-style chat UI with:
	- message history
	- loading state
	- error handling
	- markdown rendering
	- app selector for `app_id` (`mock_app`, `default_llm`, `rag_bot`, `code_agent`)
- `/admin` — system admin view with:
	- app config inspector
	- last invoke diagnostics from localStorage
	- clear note that `/manifest` is not exposed by backend
- `/health` — backend liveness and invoke smoke test

## Environment

Create `.env.local` from `.env.example`:

```bash
cp .env.example .env.local
```

Set backend base URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Cloud Run, set for example:

```env
NEXT_PUBLIC_API_URL=https://your-service-xyz-uc.a.run.app
```

## Run Locally (pnpm)

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`.

## Backend Endpoints

### `GET /`

Response:

```json
{
	"status": "ok",
	"message": "LLMOps Pipeline is running"
}
```

### `POST /invoke`

Request:

```json
{
	"app_id": "default_llm",
	"user_input": "Explain quantum computing in one sentence"
}
```

Response:

```json
{
	"app_id": "default_llm",
	"user_input": "Explain quantum computing in one sentence",
	"config": {
		"pipeline": "llm",
		"model": "gemini-2.0-flash"
	},
	"task_detection": {
		"needs_rag": false,
		"needs_agent": false
	},
	"pipeline_executed": "LLMPipeline",
	"output": "...",
	"latency_ms": 1240
}
```

## How end-to-end flow works

User → Frontend (`/chat`) → FastAPI `POST /invoke` → Task detection / orchestration / pipeline execution → response → Frontend

## Build for production

```bash
pnpm build
pnpm start
```

## Deploy to Vercel

1. Push this frontend project to GitHub.
2. Import project in Vercel.
3. Set environment variable in Vercel Project Settings:
	 - `NEXT_PUBLIC_API_URL` = your backend URL
4. Deploy.

### Recommended for Cloud Run backend

- Configure CORS on backend (already broad in your FastAPI server).
- Use HTTPS backend URL in Vercel env vars.
- If backend requires auth headers, add them in `src/lib/api.ts`.
