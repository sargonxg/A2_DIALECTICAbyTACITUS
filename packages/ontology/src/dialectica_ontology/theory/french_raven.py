"""
French-Raven Theory Framework — DIALECTICA implementation.

John French and Bertram Raven's six bases of social power:
coercive, reward, legitimate, expert, referent, and informational.
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

POWER_BASES: dict[str, dict[str, str]] = {
    "coercive": {
        "description": "Power based on the ability to punish or impose negative consequences.",
        "source": "Control over punishments, sanctions, threats.",
        "effect": "Compliance through fear; breeds resentment and resistance.",
        "indicators": "threat,punishment,sanction,coercion,fear,force",
    },
    "reward": {
        "description": "Power based on the ability to provide rewards or positive outcomes.",
        "source": "Control over resources, incentives, benefits.",
        "effect": "Compliance through incentive; effective but may not build commitment.",
        "indicators": "incentive,reward,benefit,resource_control,bonus,compensation",
    },
    "legitimate": {
        "description": "Power based on formal authority or position.",
        "source": "Organisational role, elected office, cultural norms.",
        "effect": "Compliance based on accepted authority; depends on legitimacy perception.",
        "indicators": "authority,position,role,title,mandate,legitimacy",
    },
    "expert": {
        "description": "Power based on knowledge, skills, or expertise.",
        "source": "Specialised knowledge, technical skill, experience.",
        "effect": "Influence through credibility; highly effective when expertise is relevant.",
        "indicators": "expertise,knowledge,skill,competence,experience,specialist",
    },
    "referent": {
        "description": "Power based on personal charisma, identification, or admiration.",
        "source": "Personal qualities, relationships, group membership.",
        "effect": "Influence through desire to identify with the power holder.",
        "indicators": "charisma,respect,admiration,identification,loyalty,role_model",
    },
    "informational": {
        "description": "Power based on control over information others need.",
        "source": "Access to data, intelligence, communication channels.",
        "effect": "Influence through selective sharing or withholding of information.",
        "indicators": "information,data,intelligence,communication,gatekeeping,access",
    },
}


class FrenchRavenFramework(TheoryFramework):
    """French and Raven's six bases of social power.

    Analyses the power dynamics in a conflict by identifying which bases
    of power each party holds and how power asymmetries affect the conflict.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "French-Raven Bases of Social Power"
        self.author = "John French & Bertram Raven"
        self.key_concepts = [
            "coercive_power",
            "reward_power",
            "legitimate_power",
            "expert_power",
            "referent_power",
            "informational_power",
            "power_asymmetry",
        ]

    def describe(self) -> str:
        return (
            "French and Raven identified six bases of social power: coercive "
            "(ability to punish), reward (ability to reward), legitimate "
            "(formal authority), expert (knowledge), referent (charisma), "
            "and informational (control of information). Understanding which "
            "power bases each party holds reveals dynamics and intervention points."
        )

    def assess_power_bases(self, context: dict) -> dict:
        """Assess which power bases are present in the conflict.

        Args:
            context: Dict with optional keys:
                'power_indicators' (list[str]): Keywords indicating power types.
                'party_a_power' (list[str]): Power bases held by party A.
                'party_b_power' (list[str]): Power bases held by party B.
                'keywords' (list[str]).

        Returns:
            Dict with each power base's detected presence and party distribution.
        """
        keywords = set(context.get("keywords", []) + context.get("power_indicators", []))
        party_a = set(context.get("party_a_power", []))
        party_b = set(context.get("party_b_power", []))

        result = {}
        for base_name, base_data in POWER_BASES.items():
            base_indicators = set(base_data["indicators"].split(","))
            detected = (
                bool(keywords & base_indicators) or base_name in party_a or base_name in party_b
            )

            holders = []
            if base_name in party_a:
                holders.append("party_a")
            if base_name in party_b:
                holders.append("party_b")

            result[base_name] = {
                "detected": detected,
                "holders": holders,
                "description": base_data["description"],
                "effect": base_data["effect"],
            }

        # Power asymmetry assessment
        a_count = sum(1 for b in POWER_BASES if b in party_a)
        b_count = sum(1 for b in POWER_BASES if b in party_b)
        if a_count > b_count + 1:
            asymmetry = "party_a_dominant"
        elif b_count > a_count + 1:
            asymmetry = "party_b_dominant"
        elif a_count == 0 and b_count == 0:
            asymmetry = "unclear"
        else:
            asymmetry = "relatively_balanced"

        result["_asymmetry"] = asymmetry

        return result

    def assess(self, graph_context: dict) -> dict:
        """Full power analysis of a conflict context."""
        context = graph_context.get("indicators", graph_context)
        power_assessment = self.assess_power_bases(context)

        asymmetry = power_assessment.pop("_asymmetry")
        detected_bases = [b for b, v in power_assessment.items() if v["detected"]]

        recommendations = []
        if asymmetry in ("party_a_dominant", "party_b_dominant"):
            recommendations.append(
                "Significant power asymmetry detected. Consider power-balancing "
                "interventions before negotiation."
            )
        if any(power_assessment.get("coercive", {}).get("detected", False) for _ in [1]):
            recommendations.append(
                "Coercive power detected. Monitor for intimidation and ensure safe process."
            )
        if not detected_bases:
            recommendations.append(
                "Insufficient power data. Investigate each party's sources of influence."
            )

        return {
            "power_bases": power_assessment,
            "detected_bases": detected_bases,
            "power_asymmetry": asymmetry,
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when power-related data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if context.get("power_indicators") or context.get("keywords"):
            signals += 1
        if context.get("party_a_power"):
            signals += 1
        if context.get("party_b_power"):
            signals += 1
        if graph_context.get("power_dynamics"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="What sources of power does each party hold (authority, expertise, resources, relationships)?",  # noqa: E501
                framework=self.name,
                purpose="Identify power bases",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Is there a significant power imbalance between the parties?",
                framework=self.name,
                purpose="Assess power asymmetry",
                response_type="boolean",
            ),
        ]
