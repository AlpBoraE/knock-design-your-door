import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from .image_generator import generate_image_if_available
from .llm_generator import generate_creative_response
from .motif_extractor import extract_motifs
from .rag_context import load_context_bundle, retrieve_context_lenses
from .schemas import GenerateRequest, GenerateResponse
from .sentiment import analyze_emotion


def run_generation_pipeline(request: GenerateRequest) -> GenerateResponse:
    """Run the full AI artwork pipeline and persist the result."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    combined_user_text = "\n".join(
        [
            request.leave_behind.strip(),
            request.threshold.strip(),
            request.hope_to_hear.strip(),
        ]
    )

    emotion = analyze_emotion(combined_user_text)
    context_bundle = load_context_bundle()
    selected_lenses = retrieve_context_lenses(combined_user_text, emotion.dominant_emotion)
    motifs = extract_motifs(combined_user_text, emotion.dominant_emotion, selected_lenses)
    generated = generate_creative_response(request, emotion, context_bundle, selected_lenses, motifs)
    image_path = generate_image_if_available(generated["image_prompt"], timestamp)

    response = GenerateResponse(
        emotion=emotion.to_dict(),
        motifs=[motif.to_dict() for motif in motifs],
        context_lenses=selected_lenses,
        manifesto_text=generated["manifesto_text"],
        image_prompt=generated["image_prompt"],
        historical_influence=generated["historical_influence"],
        image_url_or_path=image_path,
    )

    _save_output(timestamp, request, response, context_bundle, selected_lenses)
    return response


def _save_output(
    timestamp: str,
    request: GenerateRequest,
    response: GenerateResponse,
    context_bundle: Dict[str, str],
    selected_lenses: list[Dict[str, object]],
) -> None:
    outputs_dir = Path(__file__).resolve().parents[1] / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / f"knock_output_{timestamp}.json"

    payload = {
        "timestamp": timestamp,
        "input": request.model_dump(),
        "output": response.model_dump(),
        "context_files_loaded": list(context_bundle.keys()),
        "selected_context_lenses": selected_lenses,
    }

    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
