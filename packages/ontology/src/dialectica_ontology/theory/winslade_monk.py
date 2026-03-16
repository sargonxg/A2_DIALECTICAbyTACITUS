"""
Winslade-Monk Theory Framework — DIALECTICA implementation.

John Winslade and Gerald Monk's narrative mediation approach.
Conflicts are understood as shaped by dominant narratives; resolution
involves identifying and developing alternative/counter narratives.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

NARRATIVE_TYPES: dict[str, dict[str, str]] = {
    "dominant": {
        "description": "The prevailing story that shapes how the conflict is understood.",
        "characteristics": "Widely accepted, self-reinforcing, often simplistic, resistant to change.",
        "indicators": "mainstream,accepted,prevailing,official,established",
    },
    "alternative": {
        "description": "A different story that challenges the dominant narrative without directly opposing it.",
        "characteristics": "Offers different perspective, may coexist with dominant narrative.",
        "indicators": "different_perspective,reframe,new_angle,alternative_view",
    },
    "counter": {
        "description": "A narrative that directly opposes and seeks to replace the dominant narrative.",
        "characteristics": "Explicitly challenges power structures, confrontational.",
        "indicators": "opposition,challenge,resist,counter,protest,reject",
    },
    "subjugated": {
        "description": "Stories that have been marginalised, silenced, or rendered invisible.",
        "characteristics": "Suppressed voices, hidden experiences, unheard perspectives.",
        "indicators": "silenced,marginalised,unheard,suppressed,invisible,excluded",
    },
}


class WinsladeMonkFramework(TheoryFramework):
    """Winslade and Monk's narrative mediation approach.

    Understands conflicts as shaped by stories (narratives) that parties
    tell about themselves, each other, and the conflict. Resolution involves
    deconstructing dominant conflict-saturated narratives and developing
    alternative stories that open space for resolution.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Winslade-Monk Narrative Mediation"
        self.author = "John Winslade & Gerald Monk"
        self.key_concepts = [
            "dominant_narrative",
            "alternative_narrative",
            "counter_narrative",
            "subjugated_narrative",
            "externalisation",
            "deconstruction",
            "re_authoring",
            "double_listening",
        ]

    def describe(self) -> str:
        return (
            "Winslade and Monk's narrative mediation views conflicts as shaped "
            "by the stories parties construct. Dominant narratives define the "
            "conflict; alternative and counter narratives challenge it; "
            "subjugated narratives are silenced voices. Mediation involves "
            "externalising the problem, deconstructing conflict-saturated "
            "stories, and helping parties re-author their narratives."
        )

    def assess_narrative_landscape(self, context: dict) -> dict:
        """Assess the narrative landscape of a conflict.

        Args:
            context: Dict with optional keys:
                'narratives' (list[dict]): Each with 'text' and optional 'type'.
                'dominant_narrative' (str): The prevailing story.
                'alternative_narratives' (list[str]): Alternative stories.
                'silenced_voices' (list[str]): Marginalised perspectives.
                'keywords' (list[str]).

        Returns:
            Dict with narrative type analysis, gaps, and recommendations.
        """
        keywords = set(context.get("keywords", []))
        narratives = context.get("narratives", [])

        # Classify narratives if not already typed
        classified = {nt: [] for nt in NARRATIVE_TYPES}
        for narr in narratives:
            if isinstance(narr, dict):
                n_type = narr.get("type", self._classify_narrative(narr.get("text", ""), keywords))
                text = narr.get("text", "")
            else:
                text = str(narr)
                n_type = self._classify_narrative(text, keywords)
            classified[n_type].append(text)

        # Add explicitly provided narratives
        if context.get("dominant_narrative"):
            classified["dominant"].append(context["dominant_narrative"])
        for alt in context.get("alternative_narratives", []):
            classified["alternative"].append(alt)
        for sv in context.get("silenced_voices", []):
            classified["subjugated"].append(sv)

        # Identify narrative gaps
        gaps = []
        if not classified["dominant"]:
            gaps.append("No dominant narrative identified — clarify the prevailing story.")
        if not classified["alternative"] and not classified["counter"]:
            gaps.append("No alternative or counter narratives detected — explore different perspectives.")
        if not classified["subjugated"]:
            gaps.append("No subjugated narratives identified — seek out marginalised voices.")

        recommendations = []
        if classified["dominant"] and not classified["alternative"]:
            recommendations.append(
                "The dominant narrative is unchallenged. Use double listening "
                "to identify alternative stories hidden within the conflict talk."
            )
        if classified["subjugated"]:
            recommendations.append(
                "Subjugated narratives present. Create safe space for these "
                "voices to be heard and validated."
            )
        recommendations.append(
            "Consider externalising the problem: separate the conflict story "
            "from the identities of the parties."
        )

        return {
            "narrative_landscape": {
                n_type: {
                    "count": len(texts),
                    "narratives": texts,
                    "description": NARRATIVE_TYPES[n_type]["description"],
                }
                for n_type, texts in classified.items()
            },
            "gaps": gaps,
            "recommendations": recommendations,
        }

    def _classify_narrative(self, text: str, keywords: set) -> str:
        """Heuristically classify a narrative's type."""
        t = text.lower()

        for n_type, n_data in NARRATIVE_TYPES.items():
            indicators = set(n_data["indicators"].split(","))
            if indicators & keywords:
                return n_type
            for indicator in indicators:
                if indicator.replace("_", " ") in t:
                    return n_type

        return "dominant"  # default

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict using narrative mediation framework."""
        context = graph_context.get("indicators", graph_context)
        return self.assess_narrative_landscape(context)

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when narrative data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if context.get("narratives"):
            signals += 1
        if context.get("dominant_narrative"):
            signals += 1
        if context.get("alternative_narratives") or context.get("silenced_voices"):
            signals += 1
        if graph_context.get("history"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="What is the dominant story each party tells about this conflict?",
                framework=self.name,
                purpose="Identify dominant narratives",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Are there voices or perspectives that have been silenced or marginalised?",
                framework=self.name,
                purpose="Identify subjugated narratives",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Can you think of a different way to tell the story of this conflict?",
                framework=self.name,
                purpose="Generate alternative narratives",
                response_type="open",
            ),
        ]
