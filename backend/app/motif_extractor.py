import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Motif:
    name: str
    symbol: str
    meaning: str
    score: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "symbol": self.symbol,
            "meaning": self.meaning,
            "score": self.score,
        }


MOTIF_LIBRARY = [
    {
        "name": "Home / Exile",
        "symbol": "a half-lit doorway with dust on the threshold",
        "meaning": "The answer carries the feeling of leaving a familiar place or version of the self.",
        "terms": {"home", "family", "childhood", "city", "room", "place", "belong", "leave", "left"},
    },
    {
        "name": "Silence / Voice",
        "symbol": "a quiet door with a small line of light under it",
        "meaning": "The answer searches for a voice, permission, truth, or a silence that can finally be understood.",
        "terms": {"hear", "voice", "silence", "quiet", "say", "said", "answer", "truth", "listen"},
    },
    {
        "name": "Badge / Authority",
        "symbol": "a fallen badge half-covered by western dust",
        "meaning": "The answer questions authority, safety, rules, duty, or the cost of obedience.",
        "terms": {"authority", "rule", "rules", "safe", "law", "duty", "badge", "power", "system"},
    },
    {
        "name": "Road / Beginning",
        "symbol": "a road continuing beyond a sunset door",
        "meaning": "The answer points toward movement, risk, graduation, a new future, or an unfinished beginning.",
        "terms": {"future", "begin", "beginning", "graduation", "move", "moving", "path", "road", "change"},
    },
    {
        "name": "War / Refusal",
        "symbol": "an anti-war poster curling in hot wind",
        "meaning": "The answer contains conflict, anger, protest, refusal, or a wish to end violence.",
        "terms": {"war", "anger", "angry", "fight", "violence", "peace", "refuse", "protest", "silent"},
    },
    {
        "name": "Memory / Legacy",
        "symbol": "old fingerprints on dark wood",
        "meaning": "The answer is shaped by memory, inheritance, old attachments, or the desire to be remembered well.",
        "terms": {"memory", "remember", "past", "old", "legacy", "before", "history", "photograph", "song"},
    },
    {
        "name": "Mortality / Sky",
        "symbol": "a sunset sky behind a narrow open door",
        "meaning": "The answer touches mortality, heaven, grief, acceptance, or the unknown beyond ordinary life.",
        "terms": {"heaven", "death", "dead", "grief", "loss", "lost", "end", "ending", "goodbye"},
    },
    {
        "name": "Dust / Time",
        "symbol": "dust lifting from the floorboards",
        "meaning": "The answer feels marked by time, erosion, waiting, distance, or slow transformation.",
        "terms": {"time", "wait", "waiting", "dust", "old", "long", "years", "slow", "tired"},
    },
]


EMOTION_PRIORS = {
    "melancholic": {"Mortality / Sky", "Dust / Time", "Memory / Legacy"},
    "hopeful": {"Road / Beginning", "Silence / Voice", "Home / Exile"},
    "angry": {"War / Refusal", "Badge / Authority", "Silence / Voice"},
    "nostalgic": {"Memory / Legacy", "Home / Exile", "Dust / Time"},
    "peaceful": {"Silence / Voice", "Mortality / Sky", "Road / Beginning"},
    "conflicted": {"Badge / Authority", "Road / Beginning", "War / Refusal"},
}


LENS_PRIORS = {
    "Vietnam-era protest atmosphere": {"War / Refusal", "Badge / Authority"},
    "Counterculture as public grief": {"War / Refusal", "Memory / Legacy"},
    "Pat Garrett and the fallen badge": {"Badge / Authority", "Dust / Time"},
    "Western sunset as transition": {"Road / Beginning", "Mortality / Sky"},
    "Dylan's 1973 threshold": {"Silence / Voice", "Mortality / Sky"},
}


def extract_motifs(
    user_text: str,
    emotion: str,
    selected_lenses: List[Dict[str, object]],
    limit: int = 4,
) -> List[Motif]:
    """Extract symbolic motifs from user language, emotion, and retrieved context."""
    tokens = set(_tokenize(user_text))
    lowered = user_text.lower()
    emotion_prior = EMOTION_PRIORS.get(emotion, set())
    lens_prior = _lens_prior_names(selected_lenses)
    scored: List[Motif] = []

    for motif in MOTIF_LIBRARY:
        matched_terms = [term for term in motif["terms"] if term in tokens or term in lowered]
        score = len(matched_terms) * 1.0
        if motif["name"] in emotion_prior:
            score += 0.8
        if motif["name"] in lens_prior:
            score += 0.7

        if score > 0:
            scored.append(
                Motif(
                    name=motif["name"],
                    symbol=motif["symbol"],
                    meaning=motif["meaning"],
                    score=round(score, 2),
                )
            )

    scored.sort(key=lambda item: item.score, reverse=True)
    return _ensure_minimum_motifs(scored, emotion, limit)


def format_motifs_for_prompt(motifs: List[Motif]) -> str:
    return "\n".join(
        f"- {motif.name} (score {motif.score}): {motif.symbol}. {motif.meaning}"
        for motif in motifs
    )


def _lens_prior_names(selected_lenses: List[Dict[str, object]]) -> set[str]:
    names = set()
    for lens in selected_lenses:
        names.update(LENS_PRIORS.get(str(lens.get("title", "")), set()))
    return names


def _ensure_minimum_motifs(scored: List[Motif], emotion: str, limit: int) -> List[Motif]:
    existing = {motif.name for motif in scored}
    for motif_name in EMOTION_PRIORS.get(emotion, set()):
        if motif_name in existing:
            continue

        source = next(item for item in MOTIF_LIBRARY if item["name"] == motif_name)
        scored.append(
            Motif(
                name=source["name"],
                symbol=source["symbol"],
                meaning=source["meaning"],
                score=0.8,
            )
        )
        existing.add(motif_name)

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored[:limit]


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())

