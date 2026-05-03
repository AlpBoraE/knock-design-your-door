from pathlib import Path

from app.pipeline import run_generation_pipeline
from app.schemas import GenerateRequest


def main() -> None:
    outputs_dir = Path(__file__).resolve().parent / "outputs"
    before = set(outputs_dir.glob("knock_output_*.json"))

    request = GenerateRequest(
        leave_behind="an old room, a family memory, and a silence I carried",
        threshold="graduation and a road into a new city",
        hope_to_hear="that I can begin again without forgetting the past",
    )

    result = run_generation_pipeline(request)

    assert result.emotion.dominant_emotion, "Emotion was not detected."
    assert result.motifs, "No symbolic motifs were extracted."
    assert result.context_lenses, "No historical context lenses were selected."
    assert "1973" in result.image_prompt, "Image prompt does not include 1973."
    assert "Pat Garrett" in result.historical_influence, "Historical influence is missing Pat Garrett context."
    assert result.manifesto_text, "Manifesto text is empty."

    after = set(outputs_dir.glob("knock_output_*.json"))
    created = after - before

    print("KNOCK verification passed.")
    print(f"Emotion: {result.emotion.dominant_emotion}")
    print("Motifs:", ", ".join(motif.name for motif in result.motifs))
    print("Context lenses:", ", ".join(lens.title for lens in result.context_lenses))
    print(f"Generated output files during check: {len(created)}")

    for path in created:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

