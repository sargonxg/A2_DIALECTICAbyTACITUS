"""
Plutchik Theory Framework — DIALECTICA implementation.

Robert Plutchik's wheel of emotions: 8 primary emotions arranged in
opposite pairs, with dyads formed by combining adjacent emotions.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

# 8 primary emotions in wheel order
PRIMARY_EMOTIONS: list[str] = [
    "joy",
    "trust",
    "fear",
    "surprise",
    "sadness",
    "disgust",
    "anger",
    "anticipation",
]

# Opposite pairs
OPPOSITES: dict[str, str] = {
    "joy": "sadness",
    "sadness": "joy",
    "trust": "disgust",
    "disgust": "trust",
    "fear": "anger",
    "anger": "fear",
    "surprise": "anticipation",
    "anticipation": "surprise",
}

# Primary dyads (adjacent emotions on the wheel)
PRIMARY_DYADS: dict[tuple[str, str], str] = {
    ("joy", "trust"): "love",
    ("trust", "fear"): "submission",
    ("fear", "surprise"): "awe",
    ("surprise", "sadness"): "disapproval",
    ("sadness", "disgust"): "remorse",
    ("disgust", "anger"): "contempt",
    ("anger", "anticipation"): "aggressiveness",
    ("anticipation", "joy"): "optimism",
}

# Secondary dyads (one emotion apart)
SECONDARY_DYADS: dict[tuple[str, str], str] = {
    ("joy", "fear"): "guilt",
    ("trust", "surprise"): "curiosity",
    ("fear", "sadness"): "despair",
    ("surprise", "disgust"): "unbelief",
    ("sadness", "anger"): "envy",
    ("disgust", "anticipation"): "cynicism",
    ("anger", "joy"): "pride",
    ("anticipation", "trust"): "fatalism",
}

# Tertiary dyads (two emotions apart)
TERTIARY_DYADS: dict[tuple[str, str], str] = {
    ("joy", "surprise"): "delight",
    ("trust", "sadness"): "sentimentality",
    ("fear", "disgust"): "shame",
    ("surprise", "anger"): "outrage",
    ("sadness", "anticipation"): "pessimism",
    ("disgust", "joy"): "morbidness",
    ("anger", "trust"): "dominance",
    ("anticipation", "fear"): "anxiety",
}

# Combined dyads for easy lookup
_ALL_DYADS: dict[tuple[str, str], str] = {}
_ALL_DYADS.update(PRIMARY_DYADS)
_ALL_DYADS.update(SECONDARY_DYADS)
_ALL_DYADS.update(TERTIARY_DYADS)


class PlutchikFramework(TheoryFramework):
    """Robert Plutchik's wheel of emotions.

    8 primary emotions arranged in 4 opposite pairs, with dyads formed
    by combining adjacent emotions. Useful for analysing the emotional
    landscape of a conflict.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Plutchik Wheel of Emotions"
        self.author = "Robert Plutchik"
        self.key_concepts = [
            "primary_emotions",
            "emotion_opposites",
            "primary_dyads",
            "secondary_dyads",
            "tertiary_dyads",
            "emotion_intensity",
            "emotion_wheel",
        ]

    def describe(self) -> str:
        return (
            "Plutchik's wheel arranges 8 primary emotions (joy, trust, fear, "
            "surprise, sadness, disgust, anger, anticipation) in opposite pairs. "
            "Adjacent emotions combine into dyads (e.g., joy + trust = love, "
            "anger + disgust = contempt). Emotions vary in intensity and can "
            "reveal the underlying emotional dynamics of a conflict."
        )

    def get_dyad(self, emotion1: str, emotion2: str) -> str | None:
        """Look up the dyad formed by combining two emotions.

        Args:
            emotion1: First primary emotion.
            emotion2: Second primary emotion.

        Returns:
            Name of the resulting dyad, or None if no dyad exists.
        """
        e1 = emotion1.lower()
        e2 = emotion2.lower()

        # Check both orderings
        result = _ALL_DYADS.get((e1, e2))
        if result:
            return result
        return _ALL_DYADS.get((e2, e1))

    def get_opposite(self, emotion: str) -> str:
        """Return the opposite emotion on Plutchik's wheel.

        Args:
            emotion: A primary emotion name.

        Returns:
            The opposite emotion, or the input unchanged if not found.
        """
        return OPPOSITES.get(emotion.lower(), emotion)

    def _analyse_emotional_landscape(self, emotions: list[str]) -> dict:
        """Analyse a set of emotions present in a conflict."""
        present = [e.lower() for e in emotions if e.lower() in PRIMARY_EMOTIONS]
        absent = [e for e in PRIMARY_EMOTIONS if e not in present]

        # Find dyads among present emotions
        detected_dyads = {}
        for i, e1 in enumerate(present):
            for e2 in present[i + 1 :]:
                dyad = self.get_dyad(e1, e2)
                if dyad:
                    detected_dyads[dyad] = (e1, e2)

        # Find opposite tensions
        tensions = []
        for e in present:
            opp = self.get_opposite(e)
            if opp in present:
                pair = tuple(sorted([e, opp]))
                if pair not in tensions:
                    tensions.append(pair)

        return {
            "present_emotions": present,
            "absent_emotions": absent,
            "detected_dyads": detected_dyads,
            "opposite_tensions": [list(t) for t in tensions],
            "emotional_complexity": len(present),
        }

    def assess(self, graph_context: dict) -> dict:
        """Assess the emotional landscape of a conflict.

        Args:
            graph_context: Dict with optional key 'emotions' (list[str]).

        Returns:
            Dict with emotional landscape analysis, dyads, tensions, and recommendations.
        """
        emotions = graph_context.get("emotions", [])
        landscape = self._analyse_emotional_landscape(emotions)

        recommendations = []
        if landscape["opposite_tensions"]:
            for tension in landscape["opposite_tensions"]:
                recommendations.append(
                    f"Emotional tension between {tension[0]} and {tension[1]} "
                    f"suggests internal ambivalence or inter-party polarisation."
                )

        dyads = landscape["detected_dyads"]
        if "contempt" in dyads:
            recommendations.append(
                "Contempt (disgust + anger) detected — a strong predictor of relationship "
                "breakdown. Address underlying disgust and anger directly."
            )
        if "love" in dyads:
            recommendations.append(
                "Love (joy + trust) detected — leverage this positive emotional "
                "foundation to build resolution."
            )
        if "despair" in dyads:
            recommendations.append(
                "Despair (fear + sadness) detected — parties may feel hopeless. "
                "Rebuild sense of agency and possibility."
            )

        if not emotions:
            recommendations.append(
                "No emotional data provided. Explore the emotional dimensions of the conflict."
            )

        return {
            "emotional_landscape": landscape,
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when emotional data is present."""
        emotions = graph_context.get("emotions", [])
        if not emotions:
            return 0.0

        # More emotions = more relevant
        present = [e for e in emotions if e.lower() in PRIMARY_EMOTIONS]
        return round(min(1.0, len(present) / 4), 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="What primary emotions are each party experiencing (joy, trust, fear, surprise, sadness, disgust, anger, anticipation)?",  # noqa: E501
                framework=self.name,
                purpose="Map the emotional landscape",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Are there conflicting emotions present within either party?",
                framework=self.name,
                purpose="Detect emotional ambivalence",
                response_type="open",
            ),
        ]
