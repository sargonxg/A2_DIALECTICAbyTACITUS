"""
Mediator Agent — Fisher/Ury interest mapping, BATNA analysis, intervention strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.ripeness import RipenessAssessment, RipenessScorer
from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer


@dataclass
class MediationStrategy:
    workspace_id: str
    ripeness: RipenessAssessment | None = None
    trust_summary: str = ""
    interests_by_actor: dict[str, list[str]] = field(default_factory=dict)
    batna_assessment: str = ""
    recommended_process: str = ""
    intervention_steps: list[str] = field(default_factory=list)
    confidence: float = 0.5


class MediatorAgent:
    """Generates Fisher/Ury-grounded mediation strategies."""

    def __init__(self, graph_client: GraphClient, gemini_client: object | None = None) -> None:
        self._gc = graph_client
        self._ripeness = RipenessScorer(graph_client)
        self._trust = TrustAnalyzer(graph_client)

    async def run(self, workspace_id: str) -> MediationStrategy:
        strategy = MediationStrategy(workspace_id=workspace_id)
        strategy.ripeness = await self._ripeness.compute_ripeness(workspace_id)

        interests = await self._gc.get_nodes(workspace_id, label="Interest")
        edges = await self._gc.get_edges(workspace_id)
        for e in edges:
            if getattr(e, "type", "") == "HAS_INTEREST":
                interest = next((i for i in interests if i.id == e.target_id), None)
                if interest:
                    strategy.interests_by_actor.setdefault(e.source_id, []).append(
                        getattr(interest, "name", interest.id)
                    )

        trust_matrix = await self._trust.compute_trust_matrix(workspace_id)
        strategy.trust_summary = (
            f"Average trust: {trust_matrix.average_trust:.2f}. "
            f"Lowest: {trust_matrix.lowest_trust_pair}"
        )

        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        has_batna = any(getattr(a, "batna_strength", None) is not None for a in actors)
        strategy.batna_assessment = (
            "BATNA data available — leverage in process design."
            if has_batna
            else "BATNA not mapped — estimate from power analysis."
        )

        ripe = strategy.ripeness
        if ripe and ripe.is_ripe:
            strategy.recommended_process = "Formal mediation — ripe for intervention."
            strategy.intervention_steps = [
                "1. Establish contact via trusted intermediary.",
                "2. Agree on process framework.",
                "3. Conduct separate interest-mapping sessions.",
                "4. Identify package deals across issues.",
                "5. Draft framework agreement with verification.",
            ]
        else:
            strategy.recommended_process = "Pre-mediation confidence-building before formal talks."
            strategy.intervention_steps = [
                "1. Begin track-II dialogue.",
                "2. Implement confidence-building measures.",
                "3. Address humanitarian concerns.",
                "4. Build political space for compromise.",
                "5. Reassess ripeness in 30-60 days.",
            ]
        strategy.confidence = ripe.overall_score if ripe else 0.3
        return strategy
