"""
Tests for dialectica_graph — Schema, CRUD, traversal, vector search, analytics.

Uses MockGraphClient for unit tests (no Spanner emulator required).
Integration tests with Spanner emulator are marked with @pytest.mark.integration.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

import pytest

from dialectica_ontology.primitives import Actor, Conflict, ConflictNode, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

from dialectica_graph import create_graph_client
from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)
from dialectica_graph.spanner_schema import get_ddl_statements, get_index_ddl, get_table_ddl
from dialectica_graph.tenant import TenantContext, TenantFilter
from dialectica_graph.vector import (
    cosine_distance,
    cosine_similarity,
    normalize_embedding,
    validate_embedding,
)
from dialectica_graph.writer import WriteResult, bulk_upsert
from dialectica_graph.traversal import PathResult

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from conftest import (
    TEST_TENANT_ID,
    TEST_WORKSPACE_ID,
    MockGraphClient,
    make_actor,
    make_conflict,
    make_edge,
    make_event,
)


# ═══════════════════════════════════════════════════════════════════════════
#  SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSpannerSchema:
    def test_get_ddl_statements_returns_list(self):
        ddl = get_ddl_statements()
        assert isinstance(ddl, list)
        assert len(ddl) > 0

    def test_ddl_includes_all_tables(self):
        ddl = get_ddl_statements()
        combined = "\n".join(ddl)
        for table in [
            "Nodes",
            "Edges",
            "Workspaces",
            "TheoryAssessments",
            "APIKeys",
            "UsageLogs",
            "ExtractionJobs",
            "SchemaMigrations",
        ]:
            assert f"CREATE TABLE {table}" in combined, f"Missing table: {table}"

    def test_ddl_includes_property_graph(self):
        ddl = get_ddl_statements()
        combined = "\n".join(ddl)
        assert "CREATE OR REPLACE PROPERTY GRAPH ConflictGraph" in combined

    def test_ddl_includes_vector_index(self):
        ddl = get_ddl_statements()
        combined = "\n".join(ddl)
        assert "VECTOR INDEX" in combined
        assert "COSINE" in combined

    def test_nodes_table_has_tenant_pk(self):
        ddl = get_ddl_statements()
        nodes_ddl = [d for d in ddl if "CREATE TABLE Nodes" in d][0]
        assert "PRIMARY KEY (tenant_id, workspace_id, id)" in nodes_ddl

    def test_edges_table_has_source_target(self):
        ddl = get_ddl_statements()
        edges_ddl = [d for d in ddl if "CREATE TABLE Edges" in d][0]
        assert "source_id" in edges_ddl
        assert "target_id" in edges_ddl

    def test_embedding_column_768_dim(self):
        ddl = get_ddl_statements()
        nodes_ddl = [d for d in ddl if "CREATE TABLE Nodes" in d][0]
        assert "vector_length=768" in nodes_ddl

    def test_get_table_ddl_returns_only_tables(self):
        tables = get_table_ddl()
        assert all("CREATE TABLE" in t for t in tables)

    def test_get_index_ddl_returns_indexes(self):
        indexes = get_index_ddl()
        assert all("INDEX" in i for i in indexes)


# ═══════════════════════════════════════════════════════════════════════════
#  NODE CRUD TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestNodeCRUD:
    @pytest.mark.asyncio
    async def test_upsert_and_get_node(self, mock_client: MockGraphClient):
        actor = make_actor("Alice")
        nid = await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        assert nid == actor.id

        retrieved = await mock_client.get_node(actor.id, TEST_WORKSPACE_ID)
        assert retrieved is not None
        assert retrieved.id == actor.id

    @pytest.mark.asyncio
    async def test_get_node_not_found(self, mock_client: MockGraphClient):
        result = await mock_client.get_node("nonexistent", TEST_WORKSPACE_ID)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_nodes_by_label(self, mock_client: MockGraphClient):
        a1 = make_actor("Actor 1")
        a2 = make_actor("Actor 2")
        c1 = make_conflict("Conflict 1")

        await mock_client.upsert_node(a1, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(a2, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c1, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        actors = await mock_client.get_nodes(TEST_WORKSPACE_ID, label="Actor")
        assert len(actors) == 2

        conflicts = await mock_client.get_nodes(TEST_WORKSPACE_ID, label="Conflict")
        assert len(conflicts) == 1

    @pytest.mark.asyncio
    async def test_get_nodes_pagination(self, mock_client: MockGraphClient):
        for i in range(10):
            await mock_client.upsert_node(
                make_actor(f"Actor {i}"), TEST_WORKSPACE_ID, TEST_TENANT_ID
            )

        page1 = await mock_client.get_nodes(TEST_WORKSPACE_ID, limit=3, offset=0)
        page2 = await mock_client.get_nodes(TEST_WORKSPACE_ID, limit=3, offset=3)
        assert len(page1) == 3
        assert len(page2) == 3
        assert page1[0].id != page2[0].id

    @pytest.mark.asyncio
    async def test_soft_delete_node(self, mock_client: MockGraphClient):
        actor = make_actor("To Delete")
        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.delete_node(actor.id, TEST_WORKSPACE_ID, hard=False)
        result = await mock_client.get_node(actor.id, TEST_WORKSPACE_ID)
        assert result is None  # Soft-deleted, not visible

    @pytest.mark.asyncio
    async def test_hard_delete_node(self, mock_client: MockGraphClient):
        actor = make_actor("To Hard Delete")
        conflict = make_conflict("Related")
        edge = make_edge(actor, conflict)

        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(conflict, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_edge(edge, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.delete_node(actor.id, TEST_WORKSPACE_ID, hard=True)
        assert await mock_client.get_node(actor.id, TEST_WORKSPACE_ID) is None
        # Connected edges should also be removed
        edges = await mock_client.get_edges(TEST_WORKSPACE_ID)
        assert len(edges) == 0

    @pytest.mark.asyncio
    async def test_workspace_isolation(self, mock_client: MockGraphClient):
        actor = make_actor("Isolated")
        await mock_client.upsert_node(actor, "ws-A", TEST_TENANT_ID)

        # Not visible in different workspace
        result = await mock_client.get_node(actor.id, "ws-B")
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════
#  EDGE CRUD TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCRUD:
    @pytest.mark.asyncio
    async def test_upsert_and_get_edge(self, mock_client: MockGraphClient):
        actor = make_actor("Actor")
        conflict = make_conflict("Conflict")
        edge = make_edge(actor, conflict, EdgeType.PARTY_TO)

        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(conflict, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        eid = await mock_client.upsert_edge(edge, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        assert eid == edge.id
        edges = await mock_client.get_edges(TEST_WORKSPACE_ID)
        assert len(edges) == 1
        assert edges[0].type == EdgeType.PARTY_TO

    @pytest.mark.asyncio
    async def test_get_edges_by_type(self, mock_client: MockGraphClient):
        a1 = make_actor("A1")
        a2 = make_actor("A2")
        c1 = make_conflict("C1")

        await mock_client.upsert_node(a1, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(a2, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c1, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.upsert_edge(
            make_edge(a1, c1, EdgeType.PARTY_TO), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )
        await mock_client.upsert_edge(
            make_edge(a1, a2, EdgeType.ALLIED_WITH), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )

        party_edges = await mock_client.get_edges(TEST_WORKSPACE_ID, edge_type="PARTY_TO")
        assert len(party_edges) == 1

        ally_edges = await mock_client.get_edges(TEST_WORKSPACE_ID, edge_type="ALLIED_WITH")
        assert len(ally_edges) == 1


# ═══════════════════════════════════════════════════════════════════════════
#  TRAVERSAL TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestTraversal:
    @pytest.mark.asyncio
    async def test_traverse_1_hop(self, mock_client: MockGraphClient):
        actor = make_actor("Center")
        conflict = make_conflict("Connected")
        edge = make_edge(actor, conflict, EdgeType.PARTY_TO)

        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(conflict, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_edge(edge, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        result = await mock_client.traverse(actor.id, TEST_WORKSPACE_ID, hops=1)
        assert isinstance(result, SubgraphResult)
        assert result.node_count >= 1
        assert result.edge_count >= 1

    @pytest.mark.asyncio
    async def test_traverse_with_edge_filter(self, mock_client: MockGraphClient):
        a1 = make_actor("A")
        a2 = make_actor("B")
        c1 = make_conflict("C")

        await mock_client.upsert_node(a1, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(a2, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c1, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.upsert_edge(
            make_edge(a1, c1, EdgeType.PARTY_TO), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )
        await mock_client.upsert_edge(
            make_edge(a1, a2, EdgeType.ALLIED_WITH), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )

        result = await mock_client.traverse(
            a1.id, TEST_WORKSPACE_ID, hops=1, edge_types=["PARTY_TO"]
        )
        # Should only follow PARTY_TO edges
        edge_types = {str(e.type) for e in result.edges}
        assert "ALLIED_WITH" not in edge_types

    @pytest.mark.asyncio
    async def test_traverse_multi_hop(self, mock_client: MockGraphClient):
        a = make_actor("A")
        c = make_conflict("C")
        e = make_event("E")

        await mock_client.upsert_node(a, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(e, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.upsert_edge(
            make_edge(a, c, EdgeType.PARTY_TO), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )
        await mock_client.upsert_edge(
            make_edge(e, c, EdgeType.PART_OF), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )

        result = await mock_client.traverse(a.id, TEST_WORKSPACE_ID, hops=2)
        node_ids = {n.id for n in result.nodes}
        assert a.id in node_ids
        assert c.id in node_ids
        # Event should be reachable via 2 hops
        assert e.id in node_ids


# ═══════════════════════════════════════════════════════════════════════════
#  VECTOR SEARCH TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestVectorSearch:
    @pytest.mark.asyncio
    async def test_vector_search_returns_similar(self, mock_client: MockGraphClient):
        emb_a = [1.0] * 768
        emb_b = [0.99] * 768
        emb_c = [0.0] * 768  # orthogonal

        a = make_actor("Similar A")
        a.embedding = emb_a
        b = make_actor("Similar B")
        b.embedding = emb_b
        c = make_actor("Different C")
        c.embedding = emb_c

        await mock_client.upsert_node(a, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(b, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        results = await mock_client.vector_search(
            emb_a, TEST_WORKSPACE_ID, top_k=2
        )
        assert len(results) >= 1
        assert isinstance(results[0], ScoredNode)
        # First result should be the most similar
        assert results[0].score > 0.9

    @pytest.mark.asyncio
    async def test_vector_search_with_label_filter(self, mock_client: MockGraphClient):
        emb = [1.0] * 768
        actor = make_actor("Actor")
        actor.embedding = emb
        conflict = make_conflict("Conflict")
        conflict.embedding = emb

        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(conflict, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        results = await mock_client.vector_search(
            emb, TEST_WORKSPACE_ID, label="Actor", top_k=10
        )
        for r in results:
            assert r.node.label == "Actor"


# ═══════════════════════════════════════════════════════════════════════════
#  ANALYTICS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAnalytics:
    @pytest.mark.asyncio
    async def test_workspace_stats(self, mock_client: MockGraphClient):
        a1 = make_actor("A1")
        a2 = make_actor("A2")
        c1 = make_conflict("C1")

        await mock_client.upsert_node(a1, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(a2, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(c1, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        await mock_client.upsert_edge(
            make_edge(a1, c1, EdgeType.PARTY_TO), TEST_WORKSPACE_ID, TEST_TENANT_ID
        )

        stats = await mock_client.get_workspace_stats(TEST_WORKSPACE_ID)
        assert isinstance(stats, WorkspaceStats)
        assert stats.total_nodes == 3
        assert stats.total_edges == 1
        assert stats.node_counts_by_label["Actor"] == 2
        assert stats.node_counts_by_label["Conflict"] == 1
        assert stats.density > 0

    @pytest.mark.asyncio
    async def test_actor_network(self, mock_client: MockGraphClient):
        actor = make_actor("Center")
        await mock_client.upsert_node(actor, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        result = await mock_client.get_actor_network(actor.id, TEST_WORKSPACE_ID)
        assert isinstance(result, ActorNetworkResult)
        assert result.actor.id == actor.id

    @pytest.mark.asyncio
    async def test_timeline(self, mock_client: MockGraphClient):
        events = [make_event(f"E{i}") for i in range(3)]
        for e in events:
            await mock_client.upsert_node(e, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        timeline = await mock_client.get_timeline(TEST_WORKSPACE_ID)
        assert len(timeline) == 3

    @pytest.mark.asyncio
    async def test_escalation_trajectory(self, mock_client: MockGraphClient):
        result = await mock_client.get_escalation_trajectory(TEST_WORKSPACE_ID)
        assert isinstance(result, EscalationResult)


# ═══════════════════════════════════════════════════════════════════════════
#  BATCH OPERATIONS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestBatchOperations:
    @pytest.mark.asyncio
    async def test_batch_upsert_nodes(self, mock_client: MockGraphClient):
        actors = [make_actor(f"Batch Actor {i}") for i in range(5)]
        ids = await mock_client.batch_upsert_nodes(
            actors, TEST_WORKSPACE_ID, TEST_TENANT_ID
        )
        assert len(ids) == 5
        nodes = await mock_client.get_nodes(TEST_WORKSPACE_ID)
        assert len(nodes) == 5

    @pytest.mark.asyncio
    async def test_batch_upsert_edges(self, mock_client: MockGraphClient):
        actors = [make_actor(f"A{i}") for i in range(3)]
        conflict = make_conflict("C")
        for a in actors:
            await mock_client.upsert_node(a, TEST_WORKSPACE_ID, TEST_TENANT_ID)
        await mock_client.upsert_node(conflict, TEST_WORKSPACE_ID, TEST_TENANT_ID)

        edges = [make_edge(a, conflict, EdgeType.PARTY_TO) for a in actors]
        ids = await mock_client.batch_upsert_edges(
            edges, TEST_WORKSPACE_ID, TEST_TENANT_ID
        )
        assert len(ids) == 3

    @pytest.mark.asyncio
    async def test_bulk_upsert_writer(self, mock_client: MockGraphClient):
        actors = [make_actor(f"W{i}") for i in range(3)]
        conflict = make_conflict("WC")
        edges = [make_edge(a, conflict, EdgeType.PARTY_TO) for a in actors]

        result = await bulk_upsert(
            mock_client,
            actors + [conflict],
            edges,
            TEST_WORKSPACE_ID,
            TEST_TENANT_ID,
        )
        assert isinstance(result, WriteResult)
        assert result.success
        assert result.total_written == 7  # 4 nodes + 3 edges


# ═══════════════════════════════════════════════════════════════════════════
#  VECTOR UTILITY TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestVectorUtils:
    def test_cosine_similarity_identical(self):
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_cosine_distance(self):
        v = [1.0, 2.0, 3.0]
        assert cosine_distance(v, v) == pytest.approx(0.0)

    def test_normalize_embedding(self):
        v = [3.0, 4.0]
        normed = normalize_embedding(v)
        length = math.sqrt(sum(x * x for x in normed))
        assert length == pytest.approx(1.0)

    def test_validate_embedding_valid(self):
        assert validate_embedding(None) is True
        assert validate_embedding([0.0] * 768) is True
        assert validate_embedding([0.0] * 128) is True

    def test_validate_embedding_invalid(self):
        assert validate_embedding([0.0] * 100) is False


# ═══════════════════════════════════════════════════════════════════════════
#  TENANT ISOLATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestTenantIsolation:
    def test_tenant_context_validation(self):
        ctx = TenantContext(tenant_id="t1", workspace_id="w1")
        ctx.validate()  # Should not raise

    def test_tenant_context_empty_fails(self):
        ctx = TenantContext(tenant_id="", workspace_id="w1")
        with pytest.raises(ValueError):
            ctx.validate()

    def test_spanner_node_filter(self):
        where, params = TenantFilter.spanner_node_filter(
            workspace_id="ws1", tenant_id="t1"
        )
        assert "workspace_id = @ws" in where
        assert "tenant_id = @tid" in where
        assert "deleted_at IS NULL" in where
        assert params["ws"] == "ws1"
        assert params["tid"] == "t1"

    def test_cypher_node_filter(self):
        where, params = TenantFilter.cypher_node_filter(
            workspace_id="ws1", tenant_id="t1"
        )
        assert "workspace_id = $ws" in where
        assert "tenant_id = $tid" in where

    def test_validate_access(self):
        assert TenantFilter.validate_access("t1", "w1", "t1", "w1") is True
        assert TenantFilter.validate_access("t1", "w1", "t2", "w1") is False
        assert TenantFilter.validate_access("t1", "w1", "t1", "w2") is False


# ═══════════════════════════════════════════════════════════════════════════
#  FACTORY TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFactory:
    def test_create_graph_client_invalid_backend(self):
        with pytest.raises(ValueError, match="Unsupported graph backend"):
            create_graph_client(backend="invalid")

    def test_models_subgraph_result(self):
        result = SubgraphResult()
        assert result.node_count == 0
        assert result.edge_count == 0

    def test_models_workspace_stats_density(self):
        stats = WorkspaceStats(total_nodes=10, total_edges=20)
        density = stats.compute_density()
        assert density == pytest.approx(20 / 90)  # 20 / (10 * 9)

    def test_escalation_trajectory_point(self):
        point = EscalationTrajectoryPoint(
            timestamp=datetime.utcnow(), glasl_stage=5, evidence="test"
        )
        assert point.glasl_stage == 5
