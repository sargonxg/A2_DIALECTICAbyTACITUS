"""
Emotion Extraction — Plutchik model emotion detection from text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Plutchik primary emotions and their lexical indicators
EMOTION_LEXICON: dict[str, list[str]] = {
    "joy": ["happy", "joyful", "pleased", "satisfied", "delighted", "grateful", "celebrated", "relief"],
    "trust": ["trust", "confident", "reliable", "faith", "believe", "credible", "assured"],
    "fear": ["fear", "afraid", "anxious", "worried", "threatened", "scared", "panic", "alarm"],
    "surprise": ["surprised", "shocked", "unexpected", "astonished", "stunned", "amazed"],
    "sadness": ["sad", "grief", "mourning", "despair", "disappointed", "devastated", "sorrow"],
    "disgust": ["disgust", "repulsed", "appalled", "outraged", "revolted", "contempt"],
    "anger": ["angry", "furious", "enraged", "hostile", "resentment", "indignant", "frustrated"],
    "anticipation": ["anticipate", "expect", "hope", "await", "look forward", "prepare"],
}


@dataclass
class EmotionDetection:
    """Detected emotion in text."""

    emotion: str
    intensity: str  # low/medium/high/extreme
    evidence: str
    score: float


def detect_emotions(text: str) -> list[EmotionDetection]:
    """Detect Plutchik primary emotions in text.

    Returns list of detected emotions with intensity and evidence.
    """
    text_lower = text.lower()
    detections: list[EmotionDetection] = []

    for emotion, keywords in EMOTION_LEXICON.items():
        matches = []
        for kw in keywords:
            pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                context = text[max(0, m.start() - 30):m.end() + 30]
                matches.append(context)

        if matches:
            count = len(matches)
            if count >= 3:
                intensity = "high"
            elif count >= 2:
                intensity = "medium"
            else:
                intensity = "low"

            detections.append(EmotionDetection(
                emotion=emotion,
                intensity=intensity,
                evidence=matches[0],
                score=min(1.0, count * 0.3),
            ))

    # Sort by score descending
    detections.sort(key=lambda d: d.score, reverse=True)
    return detections
