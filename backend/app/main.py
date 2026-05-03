import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .pipeline import run_generation_pipeline
from .schemas import EmotionResult, GenerateRequest, GenerateResponse, HealthResponse


load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KNOCK: The Door I Knock On",
    description="An AI-assisted interactive artwork about farewell, transition, and meaning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:8010",
        "http://127.0.0.1:8010",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


@app.get("/")
def root() -> dict[str, object]:
    return {
        "project": "KNOCK: The Door I Knock On",
        "message": (
            "The backend is running. Open the frontend at http://127.0.0.1:5500 "
            "and use /api/health or /api/generate for API access."
        ),
        "frontend_url": "http://127.0.0.1:5500",
        "health_url": "/api/health",
        "generate_url": "/api/generate",
        "text_provider": _configured_text_provider(),
    }


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    return HealthResponse(
        status="ok",
        project="KNOCK: The Door I Knock On",
        ai_configured=has_openai or has_gemini,
        openai_configured=has_openai,
        gemini_configured=has_gemini,
        text_provider=_configured_text_provider(),
    )


@app.post("/api/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        return run_generation_pipeline(request)
    except Exception as exc:
        logger.exception("Generation pipeline failed")
        return GenerateResponse(
            emotion=EmotionResult(
                dominant_emotion="conflicted",
                score=0.5,
                description="The system met an error, but the artwork keeps the threshold visible.",
            ),
            motifs=[],
            context_lenses=[],
            manifesto_text=(
                "The door could not fully open this time, but the knock was still heard. "
                "This fallback response keeps the artwork present while the backend records the error."
            ),
            image_prompt="A symbolic closed door at sunset, dust in the air, waiting to be tried again.",
            historical_influence=(
                "Even in error, the project keeps its central historical frame: a threshold shaped by "
                "farewell, 1973, western dust, protest memory, mortality, and the search for meaning."
            ),
            image_url_or_path=None,
        )


def _configured_text_provider() -> str:
    provider = os.getenv("AI_PROVIDER", "auto").strip().lower()
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))

    if provider == "gemini" and has_gemini:
        return "gemini"
    if provider == "openai" and has_openai:
        return "openai"
    if provider == "local":
        return "local"
    if has_gemini:
        return "gemini"
    if has_openai:
        return "openai"
    return "local"
