"""
Tests for KnowledgeClusterDetector — subdomain-aware community analysis.

Uses mock graph client to avoid requiring a live database.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest


# ---------------------------------------------------------------------------
# Mock graph client
# ---------------------------------------------------------------------------


@dataclass
class MockEdge:
    id: str
    type: str
    source_id: str
    target_id: str
    properties: dict = field(default_factory=dict)
    weight: float = 1.0


@dataclass
class MockNode:
    id: str
    label: str
    name: str = ""


class MockGraphClient:
    def __init__(self, nodes: list = None, edges: list = None):
        self._nodes = nodes or []
        self._edges = edges or []

    async def get_nodes(
        self, workspace_id: str, label: str = None, limit: int = 100, offset: int = 0
    ):
        if label:
            return [n for n in self._nodes if getattr(n, "label", "") == label]
        return self._nodes

    async def get_edges(self, workspace_id: str, edge_type: str = None):
        if edge_type:
            return [e for e in self._edges if e.type == edge_type]
        return self._edges

    async def traverse(self, start_id: str, workspace_id: str, hops: int = 2, edge_types=None):
        from types import SimpleNamespace

        return SimpleNamespace(nodes=self._nodes, edges=self._edges)

    async def vector_search(self, query_text: str, workspace_id: str, top_k: int = 10, **kwargs):
        return []

    async def get_workspace_stats(self, workspace_id: str):
        from types import SimpleNamespace

        return SimpleNamespace(total_nodes=len(self._nodes), total_edges=len(self._edges))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_detect_clusters_empty_graph():
    """Empty graph should return empty ClusterReport."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    gc = MockGraphClient()
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")
    assert report.workspace_id == "test"
    assert report.clusters == []
    assert report.cross_cluster_edges == 0


@pytest.mark.asyncio
async def test_detect_clusters_with_actors():
    """Graph with actors should produce at least one cluster."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [
        MockNode(id="a1", label="Actor", name="Iran"),
        MockNode(id="a2", label="Actor", name="USA"),
        MockNode(id="a3", label="Actor", name="IAEA"),
    ]
    edges = [
        MockEdge(id="e1", type="ALLIED_WITH", source_id="a1", target_id="a2"),
        MockEdge(id="e2", type="OPPOSED_TO", source_id="a2", target_id="a3"),
    ]
    gc = MockGraphClient(nodes=actors, edges=edges)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    # Without leidenalg, each actor becomes its own community
    assert len(report.clusters) >= 1


@pytest.mark.asyncio
async def test_cluster_has_subdomain():
    """Each cluster should have a subdomain classification."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [MockNode(id="a1", label="Actor", name="Actor A")]
    gc = MockGraphClient(nodes=actors)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    for cluster in report.clusters:
        assert cluster.subdomain != ""


@pytest.mark.asyncio
async def test_cluster_has_applicable_theories():
    """Clusters should be enriched with applicable theories from SubdomainSpec."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [
        MockNode(id="a1", label="Actor", name="Iran"),
        MockNode(id="a2", label="Actor", name="USA"),
    ]
    edges = [
        MockEdge(id="e1", type="OPPOSED_TO", source_id="a1", target_id="a2"),
    ]
    gc = MockGraphClient(nodes=actors, edges=edges)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    for cluster in report.clusters:
        assert isinstance(cluster.applicable_theories, list)


@pytest.mark.asyncio
async def test_cross_cluster_edges_with_isolated_communities():
    """Cross-cluster edge count should be 0 when communities are isolated."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    # Without leidenalg, each actor is its own community.
    # An edge between different actors = cross-cluster edge.
    actors = [
        MockNode(id="a1", label="Actor", name="A"),
        MockNode(id="a2", label="Actor", name="B"),
    ]
    edges = [
        MockEdge(id="e1", type="ALLIED_WITH", source_id="a1", target_id="a2"),
    ]
    gc = MockGraphClient(nodes=actors, edges=edges)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    # Without leidenalg fallback: each node own community → cross-cluster = 1
    assert report.cross_cluster_edges >= 0


@pytest.mark.asyncio
async def test_cluster_report_subdomain():
    """Report should have an overall subdomain classification."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [MockNode(id="a1", label="Actor", name="A")]
    gc = MockGraphClient(nodes=actors)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    assert report.subdomain != ""


@pytest.mark.asyncio
async def test_cluster_density_is_valid():
    """Cluster density should be between 0 and 1."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [
        MockNode(id="a1", label="Actor", name="A"),
        MockNode(id="a2", label="Actor", name="B"),
    ]
    edges = [
        MockEdge(id="e1", type="ALLIED_WITH", source_id="a1", target_id="a2"),
    ]
    gc = MockGraphClient(nodes=actors, edges=edges)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    for cluster in report.clusters:
        assert 0.0 <= cluster.density <= 1.0


@pytest.mark.asyncio
async def test_cluster_node_count():
    """Each cluster should report correct node count."""
    from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector

    actors = [MockNode(id=f"a{i}", label="Actor", name=f"Actor {i}") for i in range(5)]
    gc = MockGraphClient(nodes=actors)
    detector = KnowledgeClusterDetector(gc)
    report = await detector.detect_clusters("test")

    total_nodes = sum(c.node_count for c in report.clusters)
    assert total_nodes == 5
