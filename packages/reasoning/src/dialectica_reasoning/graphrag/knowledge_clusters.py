"""
Knowledge Cluster Detector — Subdomain-aware community analysis for DIALECTICA.

Combines Leiden community detection with subdomain classification and theory
enrichment. Each detected community is classified by its conflict subdomain
and enriched with applicable theories from the SubdomainSpec.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.subdomains import (
    SUBDOMAIN_SPECS,
    ConflictSubdomain,
    detect_subdomain,
)
from dialectica_reasoning.graphrag.community import GraphCommunityDetector

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeCluster:
    """A knowledge cluster — a graph community enriched with subdomain and theory metadata."""

    cluster_id: int
    subdomain: str
    community: str = ""
    applicable_theories: list[str] = field(default_factory=list)
    primary_node_types: list[str] = field(default_factory=list)
    escalation_indicators: list[str] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0


@dataclass
class ClusterReport:
    """Full cluster analysis report for a workspace."""

    workspace_id: str
    clusters: list[KnowledgeCluster] = field(default_factory=list)
    subdomain: str = ""
    cross_cluster_edges: int = 0


class KnowledgeClusterDetector:
    """Detects knowledge clusters by combining community detection with subdomain classification.

    Workflow:
        1. Fetch all nodes and edges from the workspace.
        2. Detect the overall subdomain from node/edge type distributions.
        3. Run Leiden community detection.
        4. Classify each community by its subdomain.
        5. Enrich clusters with applicable theories from SubdomainSpec.
        6. Count cross-cluster edges.
    """

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._community_detector = GraphCommunityDetector(graph_client)

    async def detect_clusters(
        self,
        workspace_id: str,
        resolution: float = 1.5,
    ) -> ClusterReport:
        """Detect knowledge clusters in the workspace.

        Args:
            workspace_id: The workspace to analyse.
            resolution: Leiden resolution parameter (higher = smaller communities).

        Returns:
            A ClusterReport with classified and enriched clusters.
        """
        # 1. Fetch all nodes and edges
        nodes = await self._gc.get_nodes(workspace_id)
        edges = await self._gc.get_edges(workspace_id)

        if not nodes:
            return ClusterReport(workspace_id=workspace_id)

        # 2. Detect overall subdomain from graph structure
        node_labels = [getattr(n, "label", type(n).__name__) for n in nodes]
        edge_types = [getattr(e, "type", "") for e in edges]
        overall_subdomain = detect_subdomain(node_labels, edge_types)

        # 3. Run community detection at the requested resolution
        communities = await self._community_detector.detect_and_summarise(
            workspace_id, resolutions=[resolution]
        )

        if not communities:
            return ClusterReport(
                workspace_id=workspace_id,
                subdomain=overall_subdomain.value,
            )

        # Build membership map: node_id -> community_id
        membership: dict[str, int] = {}
        for comm in communities:
            for member_id in comm.member_ids:
                membership[member_id] = comm.community_id

        # 4–5. Classify each community and enrich with theories
        node_by_id = {getattr(n, "id", ""): n for n in nodes}
        clusters: list[KnowledgeCluster] = []

        for comm in communities:
            # Collect node labels for this community
            comm_node_labels = [
                getattr(node_by_id.get(mid), "label", type(node_by_id.get(mid)).__name__)
                for mid in comm.member_ids
                if mid in node_by_id
            ]
            # Collect edge types within this community
            member_set = set(comm.member_ids)
            comm_edge_types: list[str] = []
            comm_edge_count = 0
            for e in edges:
                src = getattr(e, "source_id", "")
                tgt = getattr(e, "target_id", "")
                if src in member_set or tgt in member_set:
                    comm_edge_types.append(getattr(e, "type", ""))
                    if src in member_set and tgt in member_set:
                        comm_edge_count += 1

            # Classify this community's subdomain
            comm_subdomain = detect_subdomain(comm_node_labels, comm_edge_types)
            spec = SUBDOMAIN_SPECS.get(comm_subdomain)

            # Compute density
            n = len(comm.member_ids)
            max_edges = n * (n - 1) / 2 if n > 1 else 1
            density = comm_edge_count / max_edges if max_edges > 0 else 0.0

            # Unique node types in this community
            primary_types = sorted(set(comm_node_labels))

            clusters.append(
                KnowledgeCluster(
                    cluster_id=comm.community_id,
                    subdomain=comm_subdomain.value,
                    community=comm.summary,
                    applicable_theories=spec.applicable_theories if spec else [],
                    primary_node_types=primary_types,
                    escalation_indicators=spec.escalation_indicators if spec else [],
                    node_count=len(comm.member_ids),
                    edge_count=comm_edge_count,
                    density=round(density, 4),
                )
            )

        # 6. Count cross-cluster edges
        cross_cluster = 0
        for e in edges:
            src_comm = membership.get(getattr(e, "source_id", ""))
            tgt_comm = membership.get(getattr(e, "target_id", ""))
            if src_comm is not None and tgt_comm is not None and src_comm != tgt_comm:
                cross_cluster += 1

        return ClusterReport(
            workspace_id=workspace_id,
            clusters=clusters,
            subdomain=overall_subdomain.value,
            cross_cluster_edges=cross_cluster,
        )
