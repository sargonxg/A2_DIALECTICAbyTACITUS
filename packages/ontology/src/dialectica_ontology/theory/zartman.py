"""
Zartman Theory Framework — DIALECTICA implementation.

I. William Zartman's ripeness theory: conflicts become ripe for resolution
when parties perceive a mutually hurting stalemate (MHS) and/or a
mutually enticing opportunity (MEO), combined with a perceived way out.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)


class ZartmanFramework(TheoryFramework):
    """I. William Zartman's ripeness theory.

    A conflict is 'ripe' for resolution when:
    1. Parties perceive a mutually hurting stalemate (MHS)
    2. Parties perceive a mutually enticing opportunity (MEO)
    3. A perceived way out exists

    Ripeness is a necessary (not sufficient) condition for negotiation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Zartman Ripeness Theory"
        self.author = "I. William Zartman"
        self.key_concepts = [
            "ripeness",
            "mutually_hurting_stalemate",
            "mutually_enticing_opportunity",
            "way_out",
            "ripe_moment",
            "negotiation_readiness",
        ]

    def describe(self) -> str:
        return (
            "Zartman's ripeness theory holds that conflicts become amenable "
            "to resolution when parties perceive a mutually hurting stalemate "
            "(MHS) — where continued conflict is costly to all — or a mutually "
            "enticing opportunity (MEO) — where a beneficial outcome becomes "
            "visible. A perceived 'way out' must also exist for ripeness."
        )

    def mutually_hurting_stalemate(self, context: dict) -> bool:
        """Assess whether a mutually hurting stalemate exists.

        Args:
            context: Dict with optional keys: 'stalemate' (bool),
                'mutual_costs' (bool), 'exhaustion' (bool),
                'pain_level_a' (float 0-1), 'pain_level_b' (float 0-1),
                'keywords' (list[str]).

        Returns:
            True if MHS conditions are detected.
        """
        if context.get("stalemate") and context.get("mutual_costs"):
            return True

        pain_a = context.get("pain_level_a", 0.0)
        pain_b = context.get("pain_level_b", 0.0)
        if pain_a > 0.6 and pain_b > 0.6:
            return True

        if context.get("exhaustion"):
            return True

        keywords = set(context.get("keywords", []))
        mhs_keywords = {"stalemate", "impasse", "exhaustion", "mutual_damage", "hurting_stalemate", "deadlock"}
        if len(keywords & mhs_keywords) >= 2:
            return True

        return False

    def mutually_enticing_opportunity(self, context: dict) -> bool:
        """Assess whether a mutually enticing opportunity exists.

        Args:
            context: Dict with optional keys: 'opportunity' (bool),
                'mutual_benefit' (bool), 'external_incentive' (bool),
                'keywords' (list[str]).

        Returns:
            True if MEO conditions are detected.
        """
        if context.get("opportunity") and context.get("mutual_benefit"):
            return True

        if context.get("external_incentive"):
            return True

        keywords = set(context.get("keywords", []))
        meo_keywords = {"opportunity", "mutual_gain", "incentive", "benefit", "enticing", "breakthrough"}
        if len(keywords & meo_keywords) >= 2:
            return True

        return False

    def _assess_way_out(self, context: dict) -> bool:
        """Assess whether parties perceive a viable way out."""
        if context.get("way_out") or context.get("proposed_solution"):
            return True

        keywords = set(context.get("keywords", []))
        way_out_keywords = {"proposal", "solution", "framework", "mediator", "negotiation", "way_out"}
        return len(keywords & way_out_keywords) >= 1

    def assess_ripeness(self, context: dict) -> dict:
        """Full ripeness assessment.

        Returns:
            Dict with 'mhs', 'meo', 'way_out', 'ripe', and 'assessment'.
        """
        mhs = self.mutually_hurting_stalemate(context)
        meo = self.mutually_enticing_opportunity(context)
        way_out = self._assess_way_out(context)

        ripe = (mhs or meo) and way_out

        if ripe and mhs and meo:
            assessment = "Highly ripe — both MHS and MEO present with a perceived way out."
        elif ripe and mhs:
            assessment = "Ripe through stalemate — parties are hurting and see a way out."
        elif ripe and meo:
            assessment = "Ripe through opportunity — mutual benefit visible with a way out."
        elif mhs or meo:
            assessment = "Partially ripe — conditions exist but no clear way out perceived."
        else:
            assessment = "Not ripe — neither MHS nor MEO detected. Conflict may need to evolve."

        return {
            "mutually_hurting_stalemate": mhs,
            "mutually_enticing_opportunity": meo,
            "way_out": way_out,
            "ripe": ripe,
            "assessment": assessment,
        }

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict context using ripeness theory."""
        context = graph_context.get("indicators", graph_context)
        return self.assess_ripeness(context)

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when ripeness indicators are present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 5

        if "stalemate" in context or "mutual_costs" in context:
            signals += 1
        if "pain_level_a" in context or "pain_level_b" in context:
            signals += 1
        if "opportunity" in context or "mutual_benefit" in context:
            signals += 1
        if context.get("keywords"):
            signals += 1
        if "way_out" in context or "proposed_solution" in context:
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="Do both parties feel that continuing the conflict is too costly?",
                framework=self.name,
                purpose="Assess mutually hurting stalemate",
                response_type="boolean",
            ),
            DiagnosticQuestion(
                question="Is there a potential outcome that both parties would find attractive?",
                framework=self.name,
                purpose="Assess mutually enticing opportunity",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Do the parties see a viable path to resolution (mediator, framework, proposal)?",
                framework=self.name,
                purpose="Assess perceived way out",
                response_type="boolean",
            ),
        ]
