"""
Graph Community Detector — Leiden community detection at multiple resolutions.

Detects communities in the workspace graph using leidenalg at 3 resolutions
(gamma=0.8, 1.5, 3.0) and generates natural language summaries.
Community summaries can be stored in Qdrant for global query support.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.primitives import ConflictNode

logger = logging.getLogger(__name__)

RESOLUTIONS = [0.8, 1.5, 3.0]


@dataclass
class CommunitySummary:
    """Human-readable summary of a detected graph community."""
    community_id: int
    resolution: float = 1.0
    actor_names: list[str] = field(default_factory=list)
    dominant_issues: list[str] = field(default_factory=list)
    escalation_level: str = "unknown"
    summary: str = ""
    actor_count: int = 0
    key_actor: str | None = None
    member_ids: list[str] = field(default_factory=list)


class GraphCommunityDetector:
    """Detects and summarises actor communities using Leiden algorithm."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def detect_and_summarise(
        self,
        workspace_id: str,
        resolutions: list[float] | None = None,
    ) -> list[CommunitySummary]:
        """Detect communities at multiple resolutions and summarise each."""
        resolutions = resolutions or RESOLUTIONS
        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        issues = await self._gc.get_nodes(workspace_id, label="Issue")
        edges = await self._gc.get_edges(workspace_id)

        if not actors:
            return []

        actor_by_id = {a.id: a for a in actors}
        actor_ids = list(actor_by_id.keys())
        id_to_idx = {aid: i for i, aid in enumerate(actor_ids)}

        # Build adjacency from edges connecting actors
        adjacency: list[tuple[int, int, float]] = []
        for e in edges:
            src_idx = id_to_idx.get(e.source_id)
            tgt_idx = id_to_idx.get(e.target_id)
            if src_idx is not None and tgt_idx is not None:
                weight = float(getattr(e, "weight", 1.0) or 1.0)
                adjacency.append((src_idx, tgt_idx, weight))

        all_summaries: list[CommunitySummary] = []

        for gamma in resolutions:
            partitions = self._leiden_partition(len(actor_ids), adjacency, gamma)

            # Group actor IDs by community
            communities: dict[int, list[str]] = {}
            for idx, comm_id in enumerate(partitions):
                communities.setdefault(comm_id, []).append(actor_ids[idx])

            for comm_id, member_ids in communities.items():
                actor_names = [
                    getattr(actor_by_id[aid], "name", aid)
                    for aid in member_ids if aid in actor_by_id
                ]

                # Find issues linked to community members
                member_set = set(member_ids)
                related_issues: dict[str, int] = {}
                for e in edges:
                    if e.source_id in member_set or e.target_id in member_set:
                        for issue in issues:
                            if e.source_id == issue.id or e.target_id == issue.id:
                                related_issues[issue.id] = related_issues.get(issue.id, 0) + 1

                dominant_issues = [
                    getattr(iss, "name", iss.id)
                    for iss in issues if iss.id in related_issues
                ][:3]

                key_actor = actor_names[0] if actor_names else None
                summary_text = (
                    f"Community {comm_id} (γ={gamma}) contains {len(member_ids)} actors"
                )
                if actor_names:
                    summary_text += f" including {', '.join(actor_names[:3])}"
                if dominant_issues:
                    summary_text += f". Key issues: {', '.join(dominant_issues)}"

                all_summaries.append(CommunitySummary(
                    community_id=comm_id,
                    resolution=gamma,
                    actor_names=actor_names,
                    dominant_issues=dominant_issues,
                    summary=summary_text,
                    actor_count=len(member_ids),
                    key_actor=key_actor,
                    member_ids=member_ids,
                ))

        return all_summaries

    @staticmethod
    def _leiden_partition(
        n_nodes: int,
        edges: list[tuple[int, int, float]],
        resolution: float,
    ) -> list[int]:
        """Run Leiden community detection. Falls back to connected components."""
        if n_nodes == 0:
            return []

        try:
            import igraph as ig
            import leidenalg

            g = ig.Graph(n=n_nodes, directed=False)
            if edges:
                edge_list = [(s, t) for s, t, _ in edges]
                weights = [w for _, _, w in edges]
                g.add_edges(edge_list)
            else:
                weights = None

            partition = leidenalg.find_partition(
                g,
                leidenalg.RBConfigurationVertexPartition,
                weights=weights if weights else None,
                resolution_parameter=resolution,
            )
            return list(partition.membership)

        except ImportError:
            logger.warning(
                "leidenalg/igraph not installed — falling back to simple connected components"
            )
            # Simple fallback: each node is its own community
            return list(range(n_nodes))
