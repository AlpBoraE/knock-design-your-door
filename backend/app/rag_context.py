from pathlib import Path
import re
from typing import Dict, List


CONTEXT_FILES = {
    "dylan_1973": "dylan_1973_context.txt",
    "vietnam_counterculture": "vietnam_counterculture_context.txt",
    "pat_garrett": "pat_garrett_context.txt",
}


def load_context_bundle() -> Dict[str, str]:
    """Load the small curated historical archive used by the generator."""
    context_dir = Path(__file__).resolve().parents[1] / "context"
    bundle: Dict[str, str] = {}

    for key, filename in CONTEXT_FILES.items():
        path = context_dir / filename
        try:
            bundle[key] = path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            bundle[key] = f"Missing context file: {filename}"

    return bundle


def combined_context_text(bundle: Dict[str, str]) -> str:
    sections = []
    for key, text in bundle.items():
        title = key.replace("_", " ").title()
        sections.append(f"[{title}]\n{text}")
    return "\n\n".join(sections)


CONTEXT_LENSES = [
    {
        "source": "dylan_1973",
        "title": "Dylan's 1973 threshold",
        "terms": {"song", "music", "death", "mortality", "farewell", "voice", "door", "legacy"},
        "summary": (
            "Dylan's 1973 film music turns a simple doorway image into a passage between "
            "farewell, mortality, and public legacy."
        ),
    },
    {
        "source": "vietnam_counterculture",
        "title": "Vietnam-era protest atmosphere",
        "terms": {"war", "protest", "anger", "authority", "future", "violence", "peace", "silence"},
        "summary": (
            "Vietnam-era counterculture adds moral pressure: protest posters, distrust of "
            "authority, and the wish to leave violence behind."
        ),
    },
    {
        "source": "pat_garrett",
        "title": "Pat Garrett and the fallen badge",
        "terms": {"badge", "western", "dust", "law", "rebel", "friendship", "betrayal", "legend"},
        "summary": (
            "Pat Garrett & Billy the Kid contributes western dust, fading law, aging legends, "
            "and the sadness of one world replacing another."
        ),
    },
    {
        "source": "vietnam_counterculture",
        "title": "Counterculture as public grief",
        "terms": {"grief", "campus", "poster", "community", "resist", "home", "memory", "lost"},
        "summary": (
            "The counterculture context frames private grief as part of a larger public refusal "
            "to accept official silence."
        ),
    },
    {
        "source": "pat_garrett",
        "title": "Western sunset as transition",
        "terms": {"threshold", "sunset", "road", "leave", "left", "behind", "change", "ending"},
        "summary": (
            "The western sunset becomes a visual language for transition: a road, a door, and "
            "the last light before an unknown future."
        ),
    },
]


EMOTION_LENS_PRIORS = {
    "angry": {"Vietnam-era protest atmosphere", "Counterculture as public grief"},
    "melancholic": {"Dylan's 1973 threshold", "Western sunset as transition"},
    "nostalgic": {"Counterculture as public grief", "Western sunset as transition"},
    "hopeful": {"Western sunset as transition", "Dylan's 1973 threshold"},
    "peaceful": {"Dylan's 1973 threshold", "Western sunset as transition"},
    "conflicted": {"Pat Garrett and the fallen badge", "Vietnam-era protest atmosphere"},
}


def retrieve_context_lenses(user_text: str, emotion: str, limit: int = 3) -> List[Dict[str, object]]:
    """Select the most relevant historical lenses for this specific user response."""
    tokens = set(_tokenize(user_text))
    lowered = user_text.lower()
    preferred_titles = EMOTION_LENS_PRIORS.get(emotion, set())
    scored_lenses = []

    for lens in CONTEXT_LENSES:
        matched_terms = sorted(term for term in lens["terms"] if term in tokens or term in lowered)
        score = len(matched_terms)
        if lens["title"] in preferred_titles:
            score += 1.25

        scored_lenses.append(
            {
                "source": lens["source"],
                "title": lens["title"],
                "summary": lens["summary"],
                "matched_terms": matched_terms,
                "relevance": round(score, 2),
            }
        )

    scored_lenses.sort(key=lambda item: item["relevance"], reverse=True)
    return scored_lenses[:limit]


def format_context_lenses(lenses: List[Dict[str, object]]) -> str:
    lines = []
    for lens in lenses:
        matched = ", ".join(lens.get("matched_terms", [])) or "emotion prior"
        lines.append(
            f"- {lens['title']} ({lens['source']}, score {lens['relevance']}): "
            f"{lens['summary']} Matched: {matched}."
        )
    return "\n".join(lines)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())
