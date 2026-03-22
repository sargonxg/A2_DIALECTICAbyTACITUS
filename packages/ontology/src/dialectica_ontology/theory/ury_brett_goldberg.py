"""
Ury-Brett-Goldberg Theory Framework — DIALECTICA implementation.

William Ury, Jeanne Brett, and Stephen Goldberg's dispute resolution
framework distinguishing three approaches: interests, rights, and power.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

APPROACHES: dict[str, dict[str, str]] = {
    "interests": {
        "description": "Resolving disputes by reconciling underlying interests and needs.",
        "methods": "Negotiation, mediation, problem-solving workshops.",
        "cost": "Low — preserves relationships and generates durable agreements.",
        "when_appropriate": (
            "When parties have ongoing relationships, when creative solutions "
            "are possible, when underlying needs can be articulated."
        ),
        "indicators": "needs,interests,negotiation,mediation,mutual_gain,problem_solving",
    },
    "rights": {
        "description": "Resolving disputes by determining who is right based on rules, norms, or law.",  # noqa: E501
        "methods": "Arbitration, adjudication, legal proceedings, grievance procedures.",
        "cost": "Medium — may strain relationships but provides clear outcomes.",
        "when_appropriate": (
            "When clear rules or precedents exist, when a binding decision is "
            "needed, when parties cannot negotiate productively."
        ),
        "indicators": "law,rule,precedent,arbitration,adjudication,rights,entitlement,fairness",
    },
    "power": {
        "description": "Resolving disputes through the exercise of coercive power.",
        "methods": "Strikes, lockouts, warfare, political pressure, economic sanctions.",
        "cost": "High — damages relationships, expensive, and outcomes may be unstable.",
        "when_appropriate": (
            "When other approaches have failed, when a fundamental power "
            "imbalance must be corrected, as a last resort."
        ),
        "indicators": "coercion,force,strike,sanction,threat,power_play,dominance,warfare",
    },
}


class UryBrettGoldbergFramework(TheoryFramework):
    """Ury, Brett & Goldberg's interest/rights/power framework.

    Disputes can be resolved through three approaches: reconciling interests,
    determining rights, or exercising power. Effective dispute resolution
    systems emphasise interest-based approaches, with rights and power as
    backstops.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Ury-Brett-Goldberg Dispute Resolution"
        self.author = "William Ury, Jeanne Brett & Stephen Goldberg"
        self.key_concepts = [
            "interests_based",
            "rights_based",
            "power_based",
            "dispute_system_design",
            "loop_back",
            "motivation",
        ]

    def describe(self) -> str:
        return (
            "Ury, Brett, and Goldberg identify three approaches to dispute "
            "resolution: interests (negotiating underlying needs), rights "
            "(applying rules and norms), and power (exercising coercion). "
            "Effective systems prioritise interests, use rights as a backstop, "
            "and resort to power only when necessary. 'Looping back' from "
            "power/rights to interests is a key design principle."
        )

    def recommend_approach(self, context: dict) -> str:
        """Recommend the most appropriate dispute resolution approach.

        Args:
            context: Dict with optional keys:
                'relationship_ongoing' (bool), 'clear_rules' (bool),
                'power_imbalance' (bool), 'negotiation_failed' (bool),
                'keywords' (list[str]).

        Returns:
            One of 'interests', 'rights', 'power'.
        """
        # If negotiation hasn't been tried, start with interests
        if not context.get("negotiation_failed", False):
            return "interests"

        # If clear rules exist and negotiation failed, try rights
        if context.get("clear_rules", False):
            return "rights"

        # If there's a power imbalance that needs correcting
        if context.get("power_imbalance", False):
            return "power"

        # Keyword-based classification
        keywords = set(context.get("keywords", []))
        best_approach = "interests"
        best_score = 0
        for approach, data in APPROACHES.items():
            indicators = set(data["indicators"].split(","))
            overlap = len(keywords & indicators)
            if overlap > best_score:
                best_score = overlap
                best_approach = approach

        return best_approach

    def assess_dispute_system(self, context: dict) -> dict:
        """Assess the current dispute resolution system/approach being used.

        Args:
            context: Dict with optional keys:
                'current_approach' (str), 'approaches_tried' (list[str]),
                'relationship_ongoing' (bool), 'clear_rules' (bool),
                'keywords' (list[str]).

        Returns:
            Dict with current approach analysis, recommended approach,
            system assessment, and recommendations.
        """
        current = context.get("current_approach", "unknown")
        tried = set(context.get("approaches_tried", []))

        # Assess current approach
        if current in APPROACHES:
            current_data = APPROACHES[current]
            current_analysis = {
                "approach": current,
                "description": current_data["description"],
                "cost": current_data["cost"],
            }
        else:
            current_analysis = {
                "approach": "unknown",
                "description": "Current approach not identified.",
            }

        # Recommend approach
        recommended = self.recommend_approach(context)
        recommended_data = APPROACHES[recommended]

        # System health assessment
        if "power" in tried and "interests" not in tried:
            system_health = "poor"
            system_note = "Power-based approach used without trying interest-based negotiation."
        elif "interests" in tried and current == "interests":
            system_health = "good"
            system_note = "Interest-based approach being used — preferred resolution method."
        elif "interests" in tried and current in ("rights", "power"):
            system_health = "moderate"
            system_note = "Escalated from interests to higher-cost approach. Consider looping back."
        else:
            system_health = "unclear"
            system_note = "Insufficient data to assess dispute system health."

        recommendations = []
        if current == "power":
            recommendations.append(
                "Consider 'looping back' to interest-based negotiation. "
                "Power-based resolution is costly and unstable."
            )
        if current == "rights" and context.get("relationship_ongoing"):
            recommendations.append(
                "Rights-based approach may strain the ongoing relationship. "
                "Consider returning to interest-based negotiation."
            )
        if "interests" not in tried:
            recommendations.append(
                "Interest-based negotiation has not been attempted. This should "
                "be the first approach tried."
            )

        return {
            "current_approach": current_analysis,
            "recommended_approach": {
                "approach": recommended,
                "description": recommended_data["description"],
                "when_appropriate": recommended_data["when_appropriate"],
            },
            "approaches_tried": list(tried),
            "system_health": system_health,
            "system_note": system_note,
            "recommendations": recommendations,
        }

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict using the interest/rights/power framework."""
        context = graph_context.get("indicators", graph_context)
        return self.assess_dispute_system(context)

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when dispute resolution data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if context.get("current_approach"):
            signals += 1
        if context.get("approaches_tried"):
            signals += 1
        if "negotiation_failed" in context or "clear_rules" in context:
            signals += 1
        if context.get("keywords"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="How is this dispute currently being addressed — through negotiation, rules/law, or force?",  # noqa: E501
                framework=self.name,
                purpose="Identify current dispute resolution approach",
                response_type="choice",
            ),
            DiagnosticQuestion(
                question="Have interest-based negotiation approaches been tried?",
                framework=self.name,
                purpose="Assess whether lower-cost approaches have been attempted",
                response_type="boolean",
            ),
        ]
