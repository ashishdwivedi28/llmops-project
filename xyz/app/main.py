import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLMOps Pipeline", version="1.0.0")

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(
    ","
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_checks() -> None:
    # Check for Google Cloud Project ID for Vertex AI
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        logger.warning(
            "GOOGLE_CLOUD_PROJECT not set. Only mock_app will work (Gemini/Vertex AI requires this)."
        )


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "message": "LLMOps Pipeline is running"}


app.include_router(router)
