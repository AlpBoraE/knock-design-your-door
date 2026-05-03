import base64
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


load_dotenv()


def generate_image_if_available(image_prompt: str, timestamp: str) -> Optional[str]:
    """Generate a PNG when OpenAI image generation is configured; otherwise return None."""
    if not _image_generation_enabled():
        return None

    outputs_dir = Path(__file__).resolve().parents[1] / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / f"door_image_{timestamp}.png"

    try:
        client = OpenAI()
        model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")
        response = client.images.generate(
            model=model,
            prompt=image_prompt,
            size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),
            n=1,
        )

        image_item = response.data[0]
        image_base64 = getattr(image_item, "b64_json", None)

        if image_base64:
            output_path.write_bytes(base64.b64decode(image_base64))
            return f"/outputs/{output_path.name}"

        image_url = getattr(image_item, "url", None)
        return image_url
    except Exception:
        return None


def _image_generation_enabled() -> bool:
    wants_images = os.getenv("OPENAI_GENERATE_IMAGES", "true").lower() in {"1", "true", "yes", "on"}
    return bool(os.getenv("OPENAI_API_KEY") and OpenAI is not None and wants_images)
