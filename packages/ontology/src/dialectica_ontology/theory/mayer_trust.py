"""
Mayer Trust Theory Framework — DIALECTICA implementation.

Mayer, Davis, and Schoorman's integrative model of organisational trust.
Trust = f(Ability, Benevolence, Integrity) moderated by Trustor's Propensity.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)


class MayerTrustFramework(TheoryFramework):
    """Mayer, Davis & Schoorman's integrative trust model.

    Trust is a function of three trustee attributes — Ability, Benevolence,
    and Integrity — moderated by the trustor's general propensity to trust.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Mayer-Davis-Schoorman Trust Model"
        self.author = "Roger Mayer, James Davis & F. David Schoorman"
        self.key_concepts = [
            "ability",
            "benevolence",
            "integrity",
            "propensity_to_trust",
            "trustworthiness",
            "vulnerability",
            "risk_taking_in_relationships",
        ]

    def describe(self) -> str:
        return (
            "The Mayer-Davis-Schoorman model defines trust as willingness to "
            "be vulnerable based on positive expectations. Trustworthiness "
            "has three components: Ability (competence in the relevant domain), "
            "Benevolence (genuine care for the trustor's interests), and "
            "Integrity (adherence to principles the trustor finds acceptable). "
            "These are moderated by the trustor's general propensity to trust."
        )

    def compute_trust(
        self,
        ability: float,
        benevolence: float,
        integrity: float,
        propensity: float = 0.5,
    ) -> float:
        """Compute a trust score from the three trustworthiness factors.

        Args:
            ability: Competence rating (0.0-1.0).
            benevolence: Care/goodwill rating (0.0-1.0).
            integrity: Principled behaviour rating (0.0-1.0).
            propensity: Trustor's general propensity to trust (0.0-1.0).

        Returns:
            Trust score between 0.0 and 1.0.
        """
        # Clamp inputs
        ability = max(0.0, min(1.0, ability))
        benevolence = max(0.0, min(1.0, benevolence))
        integrity = max(0.0, min(1.0, integrity))
        propensity = max(0.0, min(1.0, propensity))

        # Weighted combination: ABI factors contribute equally,
        # moderated by propensity as a multiplier
        abi_score = (ability + benevolence + integrity) / 3.0
        trust = abi_score * (0.5 + 0.5 * propensity)

        return round(min(1.0, max(0.0, trust)), 3)

    def assess_trust_level(self, score: float) -> str:
        """Classify a trust score into a qualitative level.

        Args:
            score: Trust score (0.0-1.0).

        Returns:
            One of 'very_low', 'low', 'moderate', 'high', 'very_high'.
        """
        if score >= 0.8:
            return "very_high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "moderate"
        elif score >= 0.2:
            return "low"
        return "very_low"

    def assess(self, graph_context: dict) -> dict:
        """Assess trust in a conflict context.

        Args:
            graph_context: Dict with optional keys:
                'ability' (float), 'benevolence' (float), 'integrity' (float),
                'propensity' (float), 'trust_indicators' (list[str]).

        Returns:
            Dict with trust score, level, component analysis, and recommendations.
        """
        context = graph_context.get("indicators", graph_context)

        ability = context.get("ability", 0.5)
        benevolence = context.get("benevolence", 0.5)
        integrity = context.get("integrity", 0.5)
        propensity = context.get("propensity", 0.5)

        trust_score = self.compute_trust(ability, benevolence, integrity, propensity)
        trust_level = self.assess_trust_level(trust_score)

        # Component analysis
        components = {
            "ability": {
                "score": ability,
                "assessment": "strong"
                if ability > 0.6
                else ("moderate" if ability > 0.3 else "weak"),
            },
            "benevolence": {
                "score": benevolence,
                "assessment": "strong"
                if benevolence > 0.6
                else ("moderate" if benevolence > 0.3 else "weak"),
            },
            "integrity": {
                "score": integrity,
                "assessment": "strong"
                if integrity > 0.6
                else ("moderate" if integrity > 0.3 else "weak"),
            },
        }

        # Find weakest component
        weakest = min(components, key=lambda k: components[k]["score"])

        recommendations = []
        if trust_level in ("very_low", "low"):
            recommendations.append(
                f"Trust is {trust_level}. Focus on rebuilding through "
                f"demonstrating {weakest} (the weakest component)."
            )
        if components["ability"]["assessment"] == "weak":
            recommendations.append("Build competence credibility through demonstrated capability.")
        if components["benevolence"]["assessment"] == "weak":
            recommendations.append("Show genuine concern for the other party's interests.")
        if components["integrity"]["assessment"] == "weak":
            recommendations.append("Demonstrate consistency between words and actions.")

        return {
            "trust_score": trust_score,
            "trust_level": trust_level,
            "components": components,
            "weakest_component": weakest,
            "propensity_to_trust": propensity,
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when trust-related data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        for key in ("ability", "benevolence", "integrity", "propensity"):
            if key in context:
                signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="How competent do you believe the other party is in the relevant area (1-10)?",  # noqa: E501
                framework=self.name,
                purpose="Assess ability component of trust",
                response_type="scale",
            ),
            DiagnosticQuestion(
                question="Do you believe the other party genuinely cares about your interests?",
                framework=self.name,
                purpose="Assess benevolence component of trust",
                response_type="boolean",
            ),
            DiagnosticQuestion(
                question="Does the other party consistently follow through on their commitments?",
                framework=self.name,
                purpose="Assess integrity component of trust",
                response_type="boolean",
            ),
        ]
