"""
Galtung Theory Framework — DIALECTICA implementation.

Johan Galtung's violence triangle (direct, structural, cultural) and
peace theory (positive vs negative peace). Foundational framework for
understanding multi-layered violence and comprehensive peacebuilding.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

# Violence types with descriptions
VIOLENCE_TYPES: dict[str, dict[str, str]] = {
    "direct": {
        "description": "Visible, physical or verbal violence between identifiable actors.",
        "examples": "assault, war, verbal abuse, intimidation",
        "indicators": "physical_harm,verbal_abuse,intimidation,coercion,threats",
    },
    "structural": {
        "description": "Violence built into social structures causing unequal life chances.",
        "examples": "poverty, discrimination, exploitation, institutional racism",
        "indicators": "inequality,exploitation,discrimination,exclusion,marginalisation",
    },
    "cultural": {
        "description": "Aspects of culture that legitimise direct and structural violence.",
        "examples": "ideology, religion misused, nationalism, dehumanising language",
        "indicators": "dehumanisation,ideology,propaganda,othering,legitimisation",
    },
}

PEACE_TYPES: dict[str, str] = {
    "negative": "Absence of direct violence (ceasefire, end of hostilities).",
    "positive": (
        "Presence of social justice, equity, and structural conditions "
        "that address root causes of violence."
    ),
}


class GaltungFramework(TheoryFramework):
    """Johan Galtung's violence triangle and peace theory.

    Analyses three types of violence (direct, structural, cultural) and
    distinguishes between negative peace (absence of violence) and
    positive peace (presence of justice and equity).
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Galtung Violence Triangle & Peace Theory"
        self.author = "Johan Galtung"
        self.key_concepts = [
            "direct_violence",
            "structural_violence",
            "cultural_violence",
            "negative_peace",
            "positive_peace",
            "violence_triangle",
            "conflict_transformation",
        ]

    def describe(self) -> str:
        return (
            "Galtung's framework distinguishes three types of violence: "
            "direct (visible acts), structural (built into institutions), "
            "and cultural (legitimating ideologies). True peace requires "
            "not just the absence of direct violence (negative peace) but "
            "the presence of justice and equity (positive peace)."
        )

    def assess_violence_types(self, context: dict) -> dict:
        """Assess presence and severity of each violence type.

        Args:
            context: Dict with optional keys: 'keywords' (list[str]),
                'direct_violence' (float 0-1), 'structural_violence' (float 0-1),
                'cultural_violence' (float 0-1), 'indicators' (list[str]).

        Returns:
            Dict mapping each violence type to its assessed severity and evidence.
        """
        keywords = set(context.get("keywords", []) + context.get("indicators", []))
        result = {}

        for v_type, v_data in VIOLENCE_TYPES.items():
            # Check explicit score
            explicit = context.get(f"{v_type}_violence")
            if explicit is not None:
                severity = float(explicit)
            else:
                # Keyword-based heuristic
                type_indicators = set(v_data["indicators"].split(","))
                overlap = len(keywords & type_indicators)
                severity = min(1.0, overlap / max(1, len(type_indicators) * 0.5))

            if severity > 0.7:
                level = "high"
            elif severity > 0.3:
                level = "moderate"
            elif severity > 0.0:
                level = "low"
            else:
                level = "none_detected"

            result[v_type] = {
                "severity": round(severity, 2),
                "level": level,
                "description": v_data["description"],
            }

        return result

    def _assess_peace_type(self, context: dict) -> dict:
        """Determine whether the situation reflects negative or positive peace."""
        violence = self.assess_violence_types(context)
        direct_sev = violence["direct"]["severity"]
        structural_sev = violence["structural"]["severity"]
        cultural_sev = violence["cultural"]["severity"]

        if direct_sev < 0.1 and structural_sev < 0.2 and cultural_sev < 0.2:
            peace_type = "positive"
            description = "Low violence across all dimensions — approaching positive peace."
        elif direct_sev < 0.2:
            peace_type = "negative"
            description = (
                "Direct violence is low, but structural/cultural violence persists. "
                "This is negative peace — absence of overt conflict without justice."
            )
        else:
            peace_type = "none"
            description = "Active violence present — neither positive nor negative peace."

        return {"peace_type": peace_type, "description": description}

    def assess(self, graph_context: dict) -> dict:
        """Full Galtung assessment of a conflict context.

        Returns violence triangle analysis and peace type assessment.
        """
        context = graph_context.get("indicators", graph_context)
        violence = self.assess_violence_types(context)
        peace = self._assess_peace_type(context)

        # Determine dominant violence type
        severities = {vt: v["severity"] for vt, v in violence.items()}
        dominant = max(severities, key=severities.get)  # type: ignore[arg-type]

        recommendations = []
        if violence["direct"]["severity"] > 0.5:
            recommendations.append("Priority: Stop direct violence through ceasefire or intervention.")
        if violence["structural"]["severity"] > 0.3:
            recommendations.append("Address structural inequalities driving the conflict.")
        if violence["cultural"]["severity"] > 0.3:
            recommendations.append("Challenge cultural narratives that legitimise violence.")

        return {
            "violence_triangle": violence,
            "dominant_violence_type": dominant,
            "peace_assessment": peace,
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when violence indicators are present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 5

        for v_type in VIOLENCE_TYPES:
            if context.get(f"{v_type}_violence") is not None:
                signals += 1
        if context.get("keywords") or context.get("indicators"):
            signals += 1
        if graph_context.get("issues"):
            signals += 1

        return round(min(1.0, signals / total), 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="Is there physical violence or threat of physical harm?",
                framework=self.name,
                purpose="Assess direct violence",
                response_type="boolean",
            ),
            DiagnosticQuestion(
                question="Are there institutional or systemic inequalities affecting the parties?",
                framework=self.name,
                purpose="Assess structural violence",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Are there cultural beliefs, narratives, or ideologies that justify the conflict?",
                framework=self.name,
                purpose="Assess cultural violence",
                response_type="open",
            ),
        ]
