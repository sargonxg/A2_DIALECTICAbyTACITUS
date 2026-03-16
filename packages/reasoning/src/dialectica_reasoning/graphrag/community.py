"""
Graph Community Detector — Microsoft-style GraphRAG community summaries.

Detects communities in the workspace graph and generates natural language
summaries for global queries.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.network_metrics import NetworkAnalyzer, Community


@dataclass
class CommunitySummary:
    """Human-readable summary of a detected graph community."""
    community_id: int
    actor_names: list[str] = field(default_factory=list)
    dominant_issues: list[str] = field(default_factory=list)
    escalation_level: str = "unknown"
    summary: str = ""
    actor_count: int = 0
    key_actor: str | None = None


class GraphCommunityDetector:
    """Detects and summarises actor communities in workspace graphs."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._network = NetworkAnalyzer(graph_client)

    async def detect_and_summarise(self, workspace_id: str) -> list[CommunitySummary]:
        """Detect communities and generate summaries for each."""
        communities = await self._network.detect_communities(workspace_id)
        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        issues = await self._gc.get_nodes(workspace_id, label="Issue")
        edges = await self._gc.get_edges(workspace_id)

        actor_by_id = {a.id: a for a in actors}

        summaries: list[CommunitySummary] = []
        for comm in communities:
            actor_names = [
                getattr(actor_by_id[aid], "name", aid)
                for aid in comm.actor_ids
                if aid in actor_by_id
            ]

            # Find dominant issues: issues linked to actors in this community
            community_set = set(comm.actor_ids)
            related_issue_ids: dict[str, int] = {}
            for e in edges:
                if e.source_id in community_set or e.target_id in community_set:
                    for issue in issues:
                        if e.source_id == issue.id or e.target_id == issue.id:
                            related_issue_ids[issue.id] = related_issue_ids.get(issue.id, 0) + 1

            dominant_issues = [
                getattr(issues[i], "name", issues[i].id)
                for i, issue in enumerate(issues)
                if issue.id in related_issue_ids
            ][:3]

            key_actor = actor_names[0] if actor_names else None

            summary_text = (
                f"Community {comm.community_id} contains {len(comm.actor_ids)} actors"
            )
            if actor_names:
                summary_text += f" including {', '.join(actor_names[:3])}"
            if dominant_issues:
                summary_text += f". Key issues: {', '.join(dominant_issues)}"

            summaries.append(CommunitySummary(
                community_id=comm.community_id,
                actor_names=actor_names,
                dominant_issues=dominant_issues,
                escalation_level=comm.escalation_level,
                summary=summary_text,
                actor_count=len(comm.actor_ids),
                key_actor=key_actor,
            ))

        return summaries
