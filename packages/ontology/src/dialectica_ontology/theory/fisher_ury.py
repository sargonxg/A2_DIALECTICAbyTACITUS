"""
Fisher-Ury Theory Framework — DIALECTICA implementation.

Roger Fisher and William Ury's principled negotiation framework from
'Getting to Yes'. Focuses on interests over positions, BATNA analysis,
ZOPA identification, and objective criteria.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)


class FisherUryFramework(TheoryFramework):
    """Fisher and Ury's principled negotiation (Getting to Yes).

    Core principles:
    1. Separate the people from the problem
    2. Focus on interests, not positions
    3. Invent options for mutual gain
    4. Insist on objective criteria

    Provides BATNA analysis, ZOPA computation, and interest-based assessment.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Fisher-Ury Principled Negotiation"
        self.author = "Roger Fisher & William Ury"
        self.key_concepts = [
            "positions_vs_interests",
            "batna",
            "zopa",
            "objective_criteria",
            "mutual_gain",
            "separate_people_problem",
        ]

    def describe(self) -> str:
        return (
            "Fisher and Ury's principled negotiation framework advocates "
            "separating people from problems, focusing on underlying interests "
            "rather than stated positions, generating options for mutual gain, "
            "and using objective criteria. BATNA (Best Alternative to a "
            "Negotiated Agreement) anchors each party's negotiation power, "
            "while ZOPA (Zone of Possible Agreement) defines the bargaining range."
        )

    def compute_zopa(
        self, party_a_reservation: float, party_b_reservation: float
    ) -> float | None:
        """Compute the Zone of Possible Agreement.

        Args:
            party_a_reservation: Party A's reservation value (minimum they'll accept).
            party_b_reservation: Party B's reservation value (maximum they'll pay).

        Returns:
            Width of the ZOPA if positive (agreement possible), or None if
            no ZOPA exists (negative bargaining zone).
        """
        zopa = party_b_reservation - party_a_reservation
        if zopa >= 0:
            return zopa
        return None

    def assess_batna_strength(self, batna_description: str) -> str:
        """Assess the relative strength of a BATNA description.

        Uses keyword heuristics to classify BATNA strength.

        Args:
            batna_description: Free-text description of a party's BATNA.

        Returns:
            One of 'strong', 'moderate', or 'weak'.
        """
        desc = batna_description.lower()

        strong_indicators = [
            "excellent", "strong", "viable", "multiple options",
            "competitive offer", "walk away", "alternative deal",
            "better offer", "other partners", "independent",
        ]
        weak_indicators = [
            "no alternative", "weak", "dependent", "desperate",
            "no choice", "must agree", "stuck", "trapped",
            "only option", "no leverage",
        ]

        strong_count = sum(1 for kw in strong_indicators if kw in desc)
        weak_count = sum(1 for kw in weak_indicators if kw in desc)

        if strong_count > weak_count:
            return "strong"
        elif weak_count > strong_count:
            return "weak"
        return "moderate"

    def _detect_positions_vs_interests(self, context: dict) -> dict:
        """Analyse whether parties are stating positions or interests."""
        positions = context.get("positions", [])
        interests = context.get("interests", [])

        if interests and not positions:
            stance = "interest_focused"
        elif positions and not interests:
            stance = "position_locked"
        elif interests and positions:
            stance = "mixed"
        else:
            stance = "unclear"

        return {
            "stance": stance,
            "positions_identified": len(positions),
            "interests_identified": len(interests),
            "recommendation": (
                "Help parties articulate underlying interests behind their positions."
                if stance in ("position_locked", "unclear")
                else "Good — interests are being explored. Look for mutual gains."
            ),
        }

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict context using principled negotiation concepts.

        Args:
            graph_context: Dict with optional keys: 'positions', 'interests',
                'batna_a', 'batna_b', 'reservation_a', 'reservation_b',
                'objective_criteria'.

        Returns:
            Dict with 'positions_vs_interests', 'zopa_analysis',
            'batna_assessment', 'objective_criteria_present',
            and 'recommendations'.
        """
        result: dict = {}

        # Positions vs interests analysis
        result["positions_vs_interests"] = self._detect_positions_vs_interests(
            graph_context
        )

        # ZOPA analysis
        res_a = graph_context.get("reservation_a")
        res_b = graph_context.get("reservation_b")
        if res_a is not None and res_b is not None:
            zopa = self.compute_zopa(res_a, res_b)
            result["zopa_analysis"] = {
                "zopa_exists": zopa is not None,
                "zopa_width": zopa,
                "recommendation": (
                    f"ZOPA of {zopa} exists — focus negotiation within this range."
                    if zopa is not None
                    else "No ZOPA — parties should re-examine interests or improve BATNAs."
                ),
            }
        else:
            result["zopa_analysis"] = {
                "zopa_exists": None,
                "recommendation": "Insufficient data to compute ZOPA. Identify reservation values.",
            }

        # BATNA assessment
        batna_a = graph_context.get("batna_a", "")
        batna_b = graph_context.get("batna_b", "")
        if batna_a or batna_b:
            result["batna_assessment"] = {}
            if batna_a:
                result["batna_assessment"]["party_a"] = self.assess_batna_strength(batna_a)
            if batna_b:
                result["batna_assessment"]["party_b"] = self.assess_batna_strength(batna_b)

        # Objective criteria
        criteria = graph_context.get("objective_criteria", [])
        result["objective_criteria_present"] = len(criteria) > 0
        if not criteria:
            result["recommendations"] = [
                "Identify objective criteria (market value, precedent, expert opinion) "
                "to anchor the negotiation."
            ]
        else:
            result["recommendations"] = [
                f"Use identified criteria ({', '.join(criteria)}) as a basis for agreement."
            ]

        return result

    def score(self, graph_context: dict) -> float:
        """Score relevance of principled negotiation framework."""
        signals = 0
        total = 5

        if graph_context.get("positions") or graph_context.get("interests"):
            signals += 1
        if graph_context.get("reservation_a") or graph_context.get("reservation_b"):
            signals += 1
        if graph_context.get("batna_a") or graph_context.get("batna_b"):
            signals += 1
        if graph_context.get("objective_criteria"):
            signals += 1
        if len(graph_context.get("parties", [])) >= 2:
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="What does each party really want (interests), beyond what they are asking for (positions)?",
                framework=self.name,
                purpose="Separate positions from interests",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="What is each party's best alternative if no agreement is reached?",
                framework=self.name,
                purpose="Assess BATNA strength",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Are there objective standards or criteria both parties would accept as fair?",
                framework=self.name,
                purpose="Identify objective criteria",
                response_type="open",
            ),
        ]
