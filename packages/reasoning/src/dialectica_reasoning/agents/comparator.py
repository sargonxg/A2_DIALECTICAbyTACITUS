"""
Comparator Agent — Cross-workspace structural conflict comparison.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.ripeness import RipenessScorer


@dataclass
class WorkspaceSummary:
    workspace_id: str
    actor_count: int = 0
    event_count: int = 0
    glasl_stage: str = "unknown"
    ripeness_score: float = 0.0
    top_patterns: list[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    workspace_a: WorkspaceSummary
    workspace_b: WorkspaceSummary
    structural_similarity: float = 0.0
    key_differences: list[str] = field(default_factory=list)
    key_similarities: list[str] = field(default_factory=list)
    insights: str = ""


class ComparatorAgent:
    """Compares two workspace conflict graphs structurally."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._escalation = EscalationDetector(graph_client)
        self._ripeness = RipenessScorer(graph_client)

    async def _summarise(self, workspace_id: str) -> WorkspaceSummary:
        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        events = await self._gc.get_nodes(workspace_id, label="Event")
        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        return WorkspaceSummary(
            workspace_id=workspace_id,
            actor_count=len(actors),
            event_count=len(events),
            glasl_stage=str(glasl.stage),
            ripeness_score=ripe.overall_score,
        )

    async def compare(self, workspace_a: str, workspace_b: str) -> ComparisonResult:
        summary_a = await self._summarise(workspace_a)
        summary_b = await self._summarise(workspace_b)

        # Structural similarity: normalised difference in key metrics
        actor_sim = 1.0 - abs(summary_a.actor_count - summary_b.actor_count) / max(
            summary_a.actor_count + summary_b.actor_count, 1
        )
        event_sim = 1.0 - abs(summary_a.event_count - summary_b.event_count) / max(
            summary_a.event_count + summary_b.event_count, 1
        )
        ripeness_sim = 1.0 - abs(summary_a.ripeness_score - summary_b.ripeness_score)
        similarity = round((actor_sim + event_sim + ripeness_sim) / 3, 3)

        differences = []
        similarities = []

        if abs(summary_a.actor_count - summary_b.actor_count) > 3:
            differences.append(
                f"Actor count differs: {workspace_a}={summary_a.actor_count}, "
                f"{workspace_b}={summary_b.actor_count}"
            )
        else:
            similarities.append("Similar number of actors")

        if summary_a.glasl_stage != summary_b.glasl_stage:
            differences.append(
                f"Escalation stage differs: {workspace_a}={summary_a.glasl_stage}, "
                f"{workspace_b}={summary_b.glasl_stage}"
            )
        else:
            similarities.append(f"Both at Glasl stage {summary_a.glasl_stage}")

        if abs(summary_a.ripeness_score - summary_b.ripeness_score) < 0.1:
            similarities.append(f"Similar ripeness scores (~{summary_a.ripeness_score:.2f})")
        else:
            differences.append(
                f"Ripeness differs: {workspace_a}={summary_a.ripeness_score:.2f}, "
                f"{workspace_b}={summary_b.ripeness_score:.2f}"
            )

        return ComparisonResult(
            workspace_a=summary_a,
            workspace_b=summary_b,
            structural_similarity=similarity,
            key_differences=differences,
            key_similarities=similarities,
            insights=(
                f"Structural similarity: {similarity:.0%}. "
                f"{'Conflicts show strong structural parallels.' if similarity > 0.7 else 'Conflicts differ significantly in structure.'}"
            ),
        )
