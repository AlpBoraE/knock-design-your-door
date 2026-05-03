from dataclasses import dataclass
from typing import Dict

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:  # The app still starts if dependencies are incomplete.
    SentimentIntensityAnalyzer = None


@dataclass
class EmotionAnalysis:
    dominant_emotion: str
    score: float
    description: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "dominant_emotion": self.dominant_emotion,
            "score": self.score,
            "description": self.description,
        }


KEYWORDS = {
    "angry": {
        "angry",
        "rage",
        "furious",
        "injustice",
        "betrayal",
        "fight",
        "shout",
        "violence",
        "burn",
        "war",
    },
    "nostalgic": {
        "remember",
        "memory",
        "childhood",
        "home",
        "old",
        "past",
        "once",
        "photograph",
        "family",
        "song",
    },
    "hopeful": {
        "hope",
        "future",
        "light",
        "begin",
        "beginning",
        "heal",
        "forgive",
        "grow",
        "alive",
        "open",
    },
    "peaceful": {
        "peace",
        "quiet",
        "calm",
        "rest",
        "still",
        "accept",
        "gentle",
        "soft",
        "breathe",
        "silence",
    },
    "melancholic": {
        "loss",
        "lost",
        "leave",
        "left",
        "behind",
        "goodbye",
        "grief",
        "miss",
        "lonely",
        "end",
        "farewell",
    },
    "conflicted": {
        "but",
        "however",
        "between",
        "unsure",
        "confused",
        "afraid",
        "ready",
        "not ready",
        "both",
        "torn",
    },
}


DESCRIPTIONS = {
    "melancholic": "Your answers carry a tender sense of loss and farewell, as if the door is opening after something meaningful has already ended.",
    "hopeful": "Your answers lean toward renewal, suggesting that the door is less an ending than a difficult opening.",
    "angry": "Your answers hold pressure and refusal, the feeling of knocking against a world that has asked too much.",
    "nostalgic": "Your answers look backward with care, keeping memory close while still approaching the threshold.",
    "peaceful": "Your answers move with acceptance, as if the knock is quiet but deliberate.",
    "conflicted": "Your answers contain mixed weather: hesitation, desire, grief, and possibility standing together at the same door.",
}


def analyze_emotion(text: str) -> EmotionAnalysis:
    """Classify a short personal reflection into a presentation-friendly tone."""
    cleaned = " ".join(text.lower().split())
    tokens = set(cleaned.replace(",", " ").replace(".", " ").split())

    keyword_counts = {
        emotion: sum(1 for word in words if word in tokens or word in cleaned)
        for emotion, words in KEYWORDS.items()
    }

    scores = _vader_scores(text)
    compound = scores["compound"]
    positive = scores["pos"]
    negative = scores["neg"]

    dominant = _choose_emotion(keyword_counts, compound, positive, negative)
    keyword_strength = min(keyword_counts.get(dominant, 0), 5) * 0.07
    sentiment_strength = min(abs(compound), 1.0) * 0.35
    mixed_strength = 0.18 if dominant == "conflicted" and positive > 0.1 and negative > 0.1 else 0
    confidence = min(0.96, round(0.52 + keyword_strength + sentiment_strength + mixed_strength, 2))

    return EmotionAnalysis(
        dominant_emotion=dominant,
        score=confidence,
        description=DESCRIPTIONS[dominant],
    )


def _vader_scores(text: str) -> Dict[str, float]:
    if SentimentIntensityAnalyzer is None:
        return _simple_sentiment_scores(text)

    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(text)


def _simple_sentiment_scores(text: str) -> Dict[str, float]:
    positive_words = KEYWORDS["hopeful"] | KEYWORDS["peaceful"]
    negative_words = KEYWORDS["angry"] | KEYWORDS["melancholic"]
    words = text.lower().split()
    if not words:
        return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0}

    pos = sum(1 for word in words if word.strip(".,!?;:") in positive_words)
    neg = sum(1 for word in words if word.strip(".,!?;:") in negative_words)
    total = max(len(words), 1)
    compound = max(-1.0, min(1.0, (pos - neg) / max(pos + neg, 1)))
    return {"compound": compound, "pos": pos / total, "neg": neg / total, "neu": 1 - ((pos + neg) / total)}


def _choose_emotion(keyword_counts: Dict[str, int], compound: float, positive: float, negative: float) -> str:
    if keyword_counts["angry"] >= 2 and negative >= positive:
        return "angry"
    if keyword_counts["conflicted"] >= 2 or (positive > 0.15 and negative > 0.15):
        return "conflicted"
    if keyword_counts["nostalgic"] >= 2:
        return "nostalgic"
    if keyword_counts["peaceful"] >= 2 and compound > -0.2:
        return "peaceful"
    if keyword_counts["hopeful"] >= 2 and compound >= -0.1:
        return "hopeful"
    if keyword_counts["melancholic"] >= 2:
        return "melancholic"
    if compound >= 0.35:
        return "hopeful"
    if compound <= -0.35:
        return "melancholic"
    if negative > positive + 0.12:
        return "melancholic"
    if positive > negative + 0.12:
        return "hopeful"
    return "peaceful"

