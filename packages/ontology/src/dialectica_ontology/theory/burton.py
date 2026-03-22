"""
Burton Theory Framework — DIALECTICA implementation.

John Burton's Basic Human Needs theory of conflict. Conflicts arise when
fundamental human needs (security, identity, recognition, participation)
are denied or threatened. Unlike interests, needs are non-negotiable.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import TheoryFramework

BASIC_NEEDS: dict[str, dict[str, str]] = {
    "security": {
        "description": "Physical safety and predictability of environment",
        "denial_indicators": "threat, violence, instability, persecution, displacement",
        "conflict_expression": "Fear-driven behaviour, pre-emptive aggression, flight response",
    },
    "identity": {
        "description": "Sense of self, group belonging, cultural continuity",
        "denial_indicators": "assimilation pressure, cultural suppression, dehumanisation, erasure",
        "conflict_expression": "Identity-based mobilisation, ethnic/religious polarisation",
    },
    "recognition": {
        "description": "Acknowledgment of worth, status, and legitimacy",
        "denial_indicators": "marginalisation, exclusion, humiliation, delegitimisation",
        "conflict_expression": "Demands for respect, status-seeking behaviour, face-saving",
    },
    "participation": {
        "description": "Ability to influence decisions affecting one's life",
        "denial_indicators": "disenfranchisement, autocracy, silencing, procedural exclusion",
        "conflict_expression": "Protests, demands for representation, democratic movements",
    },
}


class BurtonFramework(TheoryFramework):
    """John Burton's Basic Human Needs theory.

    Core insight: Deep-rooted conflicts arise from the denial of
    fundamental human needs (security, identity, recognition, participation).
    Unlike interests, needs are non-negotiable and universal. Resolution
    requires satisfying underlying needs, not just brokering compromises.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Burton Basic Human Needs"
        self.author = "John Burton"
        self.key_concepts = [
            "basic_human_needs",
            "security",
            "identity",
            "recognition",
            "participation",
            "deep_rooted_conflict",
            "needs_vs_interests",
            "problem_solving_workshop",
        ]

    def describe(self) -> str:
        return (
            "Burton's Basic Human Needs theory posits that deep-rooted conflicts "
            "arise when fundamental human needs — security, identity, recognition, "
            "and participation — are denied. Unlike interests which can be "
            "negotiated, needs are non-negotiable and universal. Resolution "
            "requires restructuring relationships and institutions to satisfy "
            "underlying needs through analytical problem-solving workshops."
        )

    def assess_needs_satisfaction(self, context: dict) -> dict:
        """Assess which basic human needs are satisfied or denied.

        Args:
            context: Dict with optional keys:
                'needs_status': dict mapping need name to satisfaction level (0-1)
                'indicators': list of observed indicators
                'keywords': list of relevant keywords

        Returns:
            Dict with need-by-need analysis and overall assessment.
        """
        needs_status = context.get("needs_status", {})
        indicators = set(context.get("indicators", []))
        keywords = set(context.get("keywords", []))

        results: dict[str, dict] = {}
        denied_needs = []

        for need_name, need_data in BASIC_NEEDS.items():
            status = needs_status.get(need_name, 0.5)
            denial_keywords = set(need_data["denial_indicators"].split(", "))
            matches = denial_keywords & (indicators | keywords)

            if matches or status < 0.3:
                denied_needs.append(need_name)

            results[need_name] = {
                "satisfaction": status,
                "description": need_data["description"],
                "denied": status < 0.3 or bool(matches),
                "denial_indicators_found": list(matches),
                "conflict_expression": need_data["conflict_expression"],
            }

        recommendations = []
        if denied_needs:
            recommendations.append(
                f"Denied needs detected: {', '.join(denied_needs)}. "
                "These are non-negotiable and require structural solutions."
            )
            if "identity" in denied_needs:
                recommendations.append(
                    "Identity needs denied — consider recognition-based "
                    "interventions and cultural dialogue."
                )
            if "security" in denied_needs:
                recommendations.append(
                    "Security needs denied — address safety concerns before "
                    "substantive negotiation."
                )
        else:
            recommendations.append(
                "No acute needs denial detected. Conflict may be interest-based "
                "rather than needs-based."
            )

        return {
            "needs_analysis": results,
            "denied_needs": denied_needs,
            "conflict_depth": "deep_rooted" if denied_needs else "surface",
            "recommendations": recommendations,
        }

    def assess(self, graph_context: dict) -> dict:
        context = graph_context.get("indicators", graph_context)
        return self.assess_needs_satisfaction(context)

    def score(self, graph_context: dict) -> float:
        """Score: higher when needs-denial indicators are present."""
        context = graph_context.get("indicators", graph_context)
        result = self.assess_needs_satisfaction(context)
        denied = len(result.get("denied_needs", []))
        return min(1.0, denied / 4.0)
