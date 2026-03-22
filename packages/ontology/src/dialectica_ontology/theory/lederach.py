"""
Lederach Theory Framework — DIALECTICA implementation.

John Paul Lederach's nested paradigm of conflict transformation,
operating across micro (personal), meso (relational/community),
and macro (structural/systemic) levels. Emphasises moral imagination
as the capacity to envision a future beyond the current conflict.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

LEVELS: dict[str, dict[str, str]] = {
    "micro": {
        "name": "Micro (Personal/Individual)",
        "description": "Individual-level issues: personal grievances, emotions, trauma, identity.",
        "actors": "individuals, families",
        "indicators": "personal_grievance,trauma,emotion,identity_threat,fear",
        "intervention": "Counselling, dialogue, personal transformation processes.",
    },
    "meso": {
        "name": "Meso (Relational/Community)",
        "description": "Community and relational dynamics: intergroup tensions, local leadership.",
        "actors": "community leaders, organisations, ethnic/religious groups",
        "indicators": "intergroup_tension,community_division,leadership_conflict,social_cohesion",
        "intervention": "Community dialogue, mediation, relationship building, local peace committees.",  # noqa: E501
    },
    "macro": {
        "name": "Macro (Structural/Systemic)",
        "description": "Large-scale structural issues: policy, governance, institutional inequality.",  # noqa: E501
        "actors": "governments, international organisations, systemic actors",
        "indicators": "policy_failure,institutional_inequality,governance,systemic_discrimination,state_violence",  # noqa: E501
        "intervention": "Policy reform, institutional change, peace agreements, structural transformation.",  # noqa: E501
    },
}


class LederachFramework(TheoryFramework):
    """John Paul Lederach's nested paradigm of conflict transformation.

    Analyses conflict at three nested levels (micro, meso, macro) and
    emphasises moral imagination — the capacity to imagine and generate
    constructive responses that transcend existing patterns of violence.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Lederach Conflict Transformation"
        self.author = "John Paul Lederach"
        self.key_concepts = [
            "nested_paradigm",
            "micro_level",
            "meso_level",
            "macro_level",
            "moral_imagination",
            "conflict_transformation",
            "web_of_relationships",
        ]

    def describe(self) -> str:
        return (
            "Lederach's nested paradigm views conflict across three levels: "
            "micro (personal), meso (relational/community), and macro "
            "(structural/systemic). His concept of moral imagination calls "
            "for the capacity to envision a future that transcends current "
            "patterns of violence while grounded in present realities."
        )

    def assess_level(self, context: dict) -> str:
        """Determine the primary level at which the conflict operates.

        Args:
            context: Dict with optional keys: 'keywords' (list[str]),
                'num_parties' (int), 'scope' (str: 'personal'|'community'|'systemic'),
                'actors' (list[str]).

        Returns:
            Level identifier: 'micro', 'meso', or 'macro'.
        """
        # Explicit scope override
        scope = context.get("scope", "")
        if scope == "personal":
            return "micro"
        if scope == "community":
            return "meso"
        if scope == "systemic":
            return "macro"

        keywords = set(context.get("keywords", []))

        # Score each level by keyword overlap
        best_level = "micro"
        best_score = 0
        for level_id, level_data in LEVELS.items():
            level_keywords = set(level_data["indicators"].split(","))
            overlap = len(keywords & level_keywords)
            if overlap > best_score:
                best_score = overlap
                best_level = level_id

        # Party count heuristic
        num_parties = context.get("num_parties", len(context.get("parties", [])))
        if num_parties > 10 and best_level == "micro":
            best_level = "macro"
        elif num_parties > 3 and best_level == "micro":
            best_level = "meso"

        return best_level

    def _assess_moral_imagination(self, context: dict) -> dict:
        """Assess indicators of moral imagination in the conflict context."""
        keywords = set(context.get("keywords", []))
        imagination_indicators = {
            "creativity",
            "vision",
            "empathy",
            "transcendence",
            "relationship_building",
            "future_oriented",
            "reconciliation",
        }
        overlap = keywords & imagination_indicators

        if len(overlap) >= 3:
            level = "high"
            description = "Strong indicators of moral imagination present."
        elif len(overlap) >= 1:
            level = "moderate"
            description = "Some moral imagination present; could be cultivated further."
        else:
            level = "low"
            description = (
                "Limited moral imagination detected. Consider processes that "
                "help parties envision a shared future beyond the conflict."
            )

        return {"level": level, "indicators_found": list(overlap), "description": description}

    def assess(self, graph_context: dict) -> dict:
        """Full Lederach assessment of a conflict context.

        Returns primary level, level details, moral imagination assessment,
        and multi-level analysis.
        """
        context = graph_context.get("indicators", graph_context)
        primary_level = self.assess_level(context)
        level_data = LEVELS[primary_level]
        moral_imagination = self._assess_moral_imagination(context)

        # Multi-level analysis
        multi_level = {}
        keywords = set(context.get("keywords", []))
        for level_id, ldata in LEVELS.items():
            level_keywords = set(ldata["indicators"].split(","))
            overlap = keywords & level_keywords
            multi_level[level_id] = {
                "relevance": "high" if len(overlap) >= 2 else ("moderate" if overlap else "low"),
                "indicators_found": list(overlap),
            }

        return {
            "primary_level": primary_level,
            "level_name": level_data["name"],
            "level_description": level_data["description"],
            "recommended_intervention": level_data["intervention"],
            "moral_imagination": moral_imagination,
            "multi_level_analysis": multi_level,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when nested-level indicators are present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if context.get("keywords"):
            signals += 1
        if context.get("scope") or context.get("num_parties"):
            signals += 1
        if context.get("actors") or context.get("parties"):
            signals += 1
        if graph_context.get("history"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="Is this conflict primarily personal, community-level, or systemic?",
                framework=self.name,
                purpose="Identify primary conflict level",
                response_type="choice",
            ),
            DiagnosticQuestion(
                question="Can the parties envision a future where they coexist constructively?",
                framework=self.name,
                purpose="Assess moral imagination",
                response_type="open",
            ),
        ]
