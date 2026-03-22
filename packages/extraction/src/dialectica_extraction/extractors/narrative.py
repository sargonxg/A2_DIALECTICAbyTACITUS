"""
Narrative Frame Detection — Identify dominant and counter-narrative frames.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Frame indicator patterns
DIAGNOSTIC_SIGNALS = re.compile(
    r"\b(?:the problem is|the root cause|blame|responsible for|at fault|failed to)\b", re.IGNORECASE
)
PROGNOSTIC_SIGNALS = re.compile(
    r"\b(?:the solution is|we should|must|need to|propose|recommend|way forward)\b", re.IGNORECASE
)
MOTIVATIONAL_SIGNALS = re.compile(
    r"\b(?:we must act|urgent|critical|now is the time|cannot wait|moral duty)\b", re.IGNORECASE
)
IDENTITY_SIGNALS = re.compile(
    r"\b(?:our people|they are|we are|us vs them|our identity|their agenda)\b", re.IGNORECASE
)
LOSS_SIGNALS = re.compile(
    r"\b(?:lost|taken from|stolen|destroyed|threatened|at risk|danger)\b", re.IGNORECASE
)
GAIN_SIGNALS = re.compile(
    r"\b(?:opportunity|benefit|gain|improve|progress|advantage|win)\b", re.IGNORECASE
)


@dataclass
class FrameAnalysis:
    """Analysis of narrative framing in text."""

    diagnostic_score: float = 0.0
    prognostic_score: float = 0.0
    motivational_score: float = 0.0
    identity_score: float = 0.0
    loss_score: float = 0.0
    gain_score: float = 0.0

    @property
    def dominant_frame(self) -> str:
        scores = {
            "diagnostic": self.diagnostic_score,
            "prognostic": self.prognostic_score,
            "motivational": self.motivational_score,
            "identity": self.identity_score,
            "loss": self.loss_score,
            "gain": self.gain_score,
        }
        return max(scores, key=scores.get)  # type: ignore[arg-type]


def analyze_frame(text: str) -> FrameAnalysis:
    """Analyze narrative framing of a text passage.

    Returns scores for each frame type based on signal phrase density.
    """
    word_count = max(len(text.split()), 1)

    def _score(pattern: re.Pattern) -> float:
        matches = len(pattern.findall(text))
        return min(1.0, matches / (word_count / 50))

    return FrameAnalysis(
        diagnostic_score=_score(DIAGNOSTIC_SIGNALS),
        prognostic_score=_score(PROGNOSTIC_SIGNALS),
        motivational_score=_score(MOTIVATIONAL_SIGNALS),
        identity_score=_score(IDENTITY_SIGNALS),
        loss_score=_score(LOSS_SIGNALS),
        gain_score=_score(GAIN_SIGNALS),
    )
