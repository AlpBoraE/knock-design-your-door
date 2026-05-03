import json
import os
import re
from typing import Dict, List

from dotenv import load_dotenv

from .motif_extractor import Motif, format_motifs_for_prompt
from .rag_context import combined_context_text, format_context_lenses
from .schemas import GenerateRequest
from .sentiment import EmotionAnalysis

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
except ImportError:
    genai = None


load_dotenv()


def generate_creative_response(
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> Dict[str, str]:
    """Generate the manifesto, image prompt, and historical influence note."""
    provider = _choose_text_provider()

    if provider == "gemini":
        try:
            return _generate_with_gemini(user_input, emotion, context_bundle, selected_lenses, motifs)
        except Exception as exc:
            fallback = _generate_locally(user_input, emotion, context_bundle, selected_lenses, motifs)
            fallback["historical_influence"] += (
                "\n\nGemini generation was attempted, but the local fallback was used because "
                f"the API call failed. Backend note: {exc}"
            )
            return fallback

    if provider == "openai":
        try:
            return _generate_with_openai(user_input, emotion, context_bundle, selected_lenses, motifs)
        except Exception as exc:
            fallback = _generate_locally(user_input, emotion, context_bundle, selected_lenses, motifs)
            fallback["historical_influence"] += (
                "\n\nOpenAI generation was attempted, but the local fallback was used because "
                f"the API call failed. Backend note: {exc}"
            )
            return fallback

    return _generate_locally(user_input, emotion, context_bundle, selected_lenses, motifs)


def _choose_text_provider() -> str:
    provider = os.getenv("AI_PROVIDER", "auto").strip().lower()

    if provider == "gemini" and os.getenv("GEMINI_API_KEY") and genai is not None:
        return "gemini"
    if provider == "openai" and os.getenv("OPENAI_API_KEY") and OpenAI is not None:
        return "openai"
    if provider == "local":
        return "local"

    if os.getenv("GEMINI_API_KEY") and genai is not None:
        return "gemini"
    if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
        return "openai"
    return "local"


def _generate_with_openai(
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> Dict[str, str]:
    client = OpenAI()
    model = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.5")

    instructions = _generation_instructions()
    prompt = _build_generation_prompt(user_input, emotion, context_bundle, selected_lenses, motifs)

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
    )

    raw_text = getattr(response, "output_text", None) or str(response)
    parsed = _extract_json(raw_text)
    return _normalize_generated_payload(parsed, user_input, emotion, context_bundle, selected_lenses, motifs)


def _generate_with_gemini(
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> Dict[str, str]:
    if genai is None:
        raise RuntimeError("google-genai is not installed.")

    model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = (
        f"{_generation_instructions()}\n\n"
        f"{_build_generation_prompt(user_input, emotion, context_bundle, selected_lenses, motifs)}"
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    raw_text = getattr(response, "text", None) or str(response)
    parsed = _extract_json(raw_text)
    return _normalize_generated_payload(parsed, user_input, emotion, context_bundle, selected_lenses, motifs)


def _generation_instructions() -> str:
    return (
        "You are the creative AI engine for a student digital artwork titled "
        "'KNOCK: The Door I Knock On.' Generate original reflective writing. "
        "Do not quote or paraphrase Bob Dylan lyrics. Use only themes, history, "
        "and atmosphere. Return strict JSON with exactly these keys: "
        "manifesto_text, image_prompt, historical_influence."
    )


def _build_generation_prompt(
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> str:
    return f"""
Historical context:
{combined_context_text(context_bundle)}

Most relevant context lenses selected for this user's answers:
{format_context_lenses(selected_lenses)}

Detected symbolic motifs:
{format_motifs_for_prompt(motifs)}

Detected emotional tone:
{emotion.dominant_emotion} with confidence {emotion.score}.
Tone description: {emotion.description}

User answers:
1. What had to be left behind: {user_input.leave_behind}
2. Current threshold: {user_input.threshold}
3. What they hope to hear: {user_input.hope_to_hear}

Write:
- manifesto_text: 250-400 words, first-person, poetic but clear, original, emotionally reflective. Organically weave in the detected motifs without listing them mechanically.
- image_prompt: one detailed cinematic prompt for a symbolic door artwork. The door must be central. Include 1973, a western landscape, anti-war posters, a fallen badge, dust, sunset, farewell, transition, the search for meaning, and at least two detected motifs.
- historical_influence: 90-140 words explaining how Bob Dylan's 1973 moment, Vietnam-era anti-war atmosphere, Pat Garrett & Billy the Kid, mortality, farewell, and legacy shaped the result.

Do not quote song lyrics. Do not name any copyrighted lyric line. Keep the language suitable for a university presentation.
"""


def _extract_json(raw_text: str) -> Dict[str, str]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("The language model did not return JSON.")
        return json.loads(match.group(0))


def _normalize_generated_payload(
    payload: Dict[str, str],
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> Dict[str, str]:
    fallback = _generate_locally(user_input, emotion, context_bundle, selected_lenses, motifs)
    return {
        "manifesto_text": str(payload.get("manifesto_text") or fallback["manifesto_text"]).strip(),
        "image_prompt": str(payload.get("image_prompt") or fallback["image_prompt"]).strip(),
        "historical_influence": str(
            payload.get("historical_influence") or fallback["historical_influence"]
        ).strip(),
    }


def _generate_locally(
    user_input: GenerateRequest,
    emotion: EmotionAnalysis,
    context_bundle: Dict[str, str],
    selected_lenses: List[Dict[str, object]],
    motifs: List[Motif],
) -> Dict[str, str]:
    leave = _prepare_leave_fragment(user_input.leave_behind)
    threshold = _prepare_threshold_fragment(user_input.threshold)
    hope = _prepare_hope_fragment(user_input.hope_to_hear)
    tone = emotion.dominant_emotion
    tone_profile = TONE_PROFILES.get(tone, TONE_PROFILES["conflicted"])
    lens_phrase = _lens_phrase(selected_lenses)
    lens_titles = ", ".join(lens["title"] for lens in selected_lenses)
    motif_phrase = _motif_phrase(motifs)
    motif_symbols = "; ".join(motif.symbol for motif in motifs[:3])

    manifesto_text = f"""
I arrive at my door carrying the shape of what I had to leave behind: {leave}. It does not disappear when I name it. It changes weight. Some of it becomes dust on my sleeve; some of it becomes a mark in the wood. The door before me is made of {tone_profile["door_material"]}, and when I put my hand near it, I feel how every threshold asks for honesty before it opens.

The threshold before me is {threshold}. I imagine it in the color of 1973: a western sky, a tired street, paper anti-war posters curling on a wall, and a fallen badge catching the last light. The history gathered around this door is not a museum label. It carries {lens_phrase}. The symbols that rise from my own words are {motif_phrase}. Somewhere in that image, Pat Garrett and Billy the Kid turn farewell into landscape. A person can become a legend, but a legend can also become lonely when the world no longer knows what to do with them.

My emotional tone is {tone}. In this tone, the knock sounds {tone_profile["knock_sound"]}. It does not give me a simple answer. It tells me that transition can be both wound and invitation. Behind the door I hear the century arguing with itself: war and protest, silence and music, endings and the stubborn wish to mean something before the light changes.

If I knocked and heaven answered, I would hope to hear this: {hope}. Not as a perfect solution, but as a permission to continue. The door I design is a place where farewell becomes form. I do not ask it to erase mortality. I ask it to hold my fear, my memory, and my unfinished hope in the same frame. When it opens, I want to step through with {tone_profile["final_gesture"]}.
""".strip()

    image_prompt = (
        f"Cinematic symbolic digital artwork, a tall weathered wooden door made of {tone_profile['door_material']} "
        "as the central motif, "
        "standing alone in a dusty western landscape at sunset in 1973. Around the doorway are faded "
        "anti-war posters from the Vietnam War era, windblown paper, dry grass, and a fallen sheriff badge "
        "half-buried in dust. Warm amber sky, long shadows, traces of a road leading forward, atmosphere of "
        f"farewell and transition, emotional tone: {tone}. The door should feel personal and ritual-like, "
        f"with embedded symbolic motifs: {motif_symbols}. "
        "Suggest mortality, legacy, silence, and the search for meaning. Painterly cinematic lighting, "
        "high detail, no text, no copied lyrics, no direct portrait of Bob Dylan."
    )

    historical_influence = (
        "The result is shaped by 1973 as a year of cultural exhaustion and transition. Dylan's work for "
        "Pat Garrett & Billy the Kid connects the song's atmosphere to western myth, death, friendship, "
        "and farewell. The Vietnam War era and counterculture anti-war movement add public grief and moral "
        "pressure, turning the user's private threshold into part of a larger historical mood. Dust, badges, "
        "silence, and sunset become symbols of authority fading, violence ending, and meaning being searched "
        f"for after loss. For this response, the strongest retrieved context lenses were: {lens_titles}. "
        f"The detected motifs were: {', '.join(motif.name for motif in motifs)}."
    )

    return {
        "manifesto_text": manifesto_text,
        "image_prompt": image_prompt,
        "historical_influence": historical_influence,
    }


def _clean_fragment(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) > 260:
        return cleaned[:257].rstrip() + "..."
    return cleaned


def _strip_terminal_punctuation(text: str) -> str:
    return text.rstrip(" .!?;:")


def _prepare_leave_fragment(text: str) -> str:
    cleaned = _clean_fragment(text)
    cleaned = re.sub(r"^i had to leave behind\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i left behind\s+", "", cleaned, flags=re.IGNORECASE)
    return _strip_terminal_punctuation(cleaned)


def _prepare_threshold_fragment(text: str) -> str:
    cleaned = _clean_fragment(text)
    cleaned = re.sub(r"^i am standing before\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i am standing at\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i stand before\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i stand at\s+", "", cleaned, flags=re.IGNORECASE)
    return _strip_terminal_punctuation(cleaned)


def _prepare_hope_fragment(text: str) -> str:
    cleaned = _clean_fragment(text)
    cleaned = re.sub(r"^i would hope to hear\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^i hope to hear\s+", "", cleaned, flags=re.IGNORECASE)
    return _strip_terminal_punctuation(cleaned)


TONE_PROFILES = {
    "melancholic": {
        "door_material": "dark cedar, rubbed smooth by old departures",
        "knock_sound": "low and almost swallowed by dust",
        "final_gesture": "grief named clearly, not hidden",
    },
    "hopeful": {
        "door_material": "sun-warmed pine with a thin line of gold at the frame",
        "knock_sound": "hesitant at first, then bright enough to travel",
        "final_gesture": "the past beside me instead of around my throat",
    },
    "angry": {
        "door_material": "scarred oak, nailed with torn poster paper and heat",
        "knock_sound": "sharp, like a refusal to be quiet",
        "final_gesture": "my refusal changed into direction",
    },
    "nostalgic": {
        "door_material": "weathered walnut marked by fingerprints and road dust",
        "knock_sound": "familiar, as if memory has its own hand",
        "final_gesture": "memory carried carefully, not worshiped",
    },
    "peaceful": {
        "door_material": "pale worn wood, quiet as a chapel after sunset",
        "knock_sound": "soft, but certain",
        "final_gesture": "a calm breath and an open hand",
    },
    "conflicted": {
        "door_material": "split boards, half shadowed and half lit by sunset",
        "knock_sound": "uneven, caught between staying and beginning",
        "final_gesture": "doubt still present, but no longer in command",
    },
}


LENS_POETIC_PHRASES = {
    "Dylan's 1973 threshold": "the hush of a 1973 song-world where farewell becomes a passage",
    "Vietnam-era protest atmosphere": "the moral pressure of protest posters, war fatigue, and voices refusing silence",
    "Pat Garrett and the fallen badge": "the western sadness of a badge in the dust and a legend losing its shelter",
    "Counterculture as public grief": "the feeling that private grief can become public resistance",
    "Western sunset as transition": "the last amber light before one life closes and another begins",
}


def _lens_phrase(selected_lenses: List[Dict[str, object]]) -> str:
    if not selected_lenses:
        return "a crossing of western farewell, anti-war memory, and the search for meaning"

    phrases = [
        LENS_POETIC_PHRASES.get(str(lens["title"]), str(lens["summary"]).rstrip("."))
        for lens in selected_lenses[:3]
    ]
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]} and {phrases[1]}"

    return f"{phrases[0]}, {phrases[1]}, and {phrases[2]}"


def _motif_phrase(motifs: List[Motif]) -> str:
    if not motifs:
        return "a door, a road, and a silence waiting to be answered"

    symbols = [motif.symbol for motif in motifs[:3]]
    if len(symbols) == 1:
        return symbols[0]
    if len(symbols) == 2:
        return f"{symbols[0]} and {symbols[1]}"
    return f"{symbols[0]}, {symbols[1]}, and {symbols[2]}"
