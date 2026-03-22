"""
Causal Chain Detection — Identify causal relationships between events.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Causal signal phrases
CAUSAL_SIGNALS = [
    r"\b(?:caused|led to|resulted in|triggered|provoked|prompted)\b",
    r"\b(?:because of|due to|as a result of|owing to|stemming from)\b",
    r"\b(?:consequently|therefore|thus|hence|accordingly)\b",
    r"\b(?:in response to|following|after which|which led to)\b",
    r"\b(?:escalated into|deteriorated into|evolved into)\b",
]

_CAUSAL_PATTERN = re.compile("|".join(CAUSAL_SIGNALS), re.IGNORECASE)


@dataclass
class CausalSignal:
    """A detected causal signal in text."""

    text: str
    signal_phrase: str
    start: int
    end: int
    strength: float = 0.7  # default strength


def detect_causal_signals(text: str) -> list[CausalSignal]:
    """Detect causal signal phrases in text.

    Returns list of CausalSignal with position and strength.
    """
    signals = []
    for match in _CAUSAL_PATTERN.finditer(text):
        # Determine strength based on signal type
        phrase = match.group().lower()
        if phrase in ("caused", "triggered", "provoked"):
            strength = 0.9
        elif phrase in ("led to", "resulted in"):
            strength = 0.85
        elif phrase in ("because of", "due to", "as a result of"):
            strength = 0.8
        else:
            strength = 0.7

        signals.append(
            CausalSignal(
                text=text[max(0, match.start() - 50) : match.end() + 50],
                signal_phrase=match.group(),
                start=match.start(),
                end=match.end(),
                strength=strength,
            )
        )
    return signals


def has_causal_language(text: str) -> bool:
    """Check if text contains causal language."""
    return bool(_CAUSAL_PATTERN.search(text))
