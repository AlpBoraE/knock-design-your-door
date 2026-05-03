from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    leave_behind: str = Field(
        ...,
        min_length=1,
        max_length=1200,
        description="Something the user had to leave behind.",
    )
    threshold: str = Field(
        ...,
        min_length=1,
        max_length=1200,
        description="The threshold the user feels they are standing before.",
    )
    hope_to_hear: str = Field(
        ...,
        min_length=1,
        max_length=1200,
        description="What the user hopes to hear if they knock.",
    )


class EmotionResult(BaseModel):
    dominant_emotion: str
    score: float
    description: str


class MotifResult(BaseModel):
    name: str
    symbol: str
    meaning: str
    score: float


class ContextLensResult(BaseModel):
    source: str
    title: str
    summary: str
    matched_terms: List[str] = Field(default_factory=list)
    relevance: float


class GenerateResponse(BaseModel):
    emotion: EmotionResult
    motifs: List[MotifResult] = Field(default_factory=list)
    context_lenses: List[ContextLensResult] = Field(default_factory=list)
    manifesto_text: str
    image_prompt: str
    historical_influence: str
    image_url_or_path: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    project: str
    ai_configured: bool = False
    openai_configured: bool = False
    gemini_configured: bool = False
    text_provider: str = "local"
