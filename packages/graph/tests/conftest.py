"""
Pytest configuration for graph package tests.

Provides:
  - Mock GraphClient for unit tests (no Spanner/Neo4j required)
  - Spanner emulator fixture for integration tests (requires docker-compose)
  - Common test data factories
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from dialectica_ontology.primitives import Actor, Conflict, ConflictNode, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)

TEST_WORKSPACE_ID = "ws-test-001"
TEST_TENANT_ID = "tenant-test-001"


# ── Test Data Factories ────────────────────────────────────────────────────


def make_actor(name: str = "Test Actor", **kwargs: Any) -> Actor:
    return Actor(
        name=name,
        actor_type="person",
        workspace_id=TEST_WORKSPACE_ID,
        tenant_id=TEST_TENANT_ID,
        **kwargs,
    )


def make_conflict(name: str = "Test Conflict", **kwargs: Any) -> Conflict:
    return Conflict(
        name=name,
        scale="micro",
        domain="political",
        status="active",
        workspace_id=TEST_WORKSPACE_ID,
        tenant_id=TEST_TENANT_ID,
        **kwargs,
    )


def make_event(description: str = "Test Event", **kwargs: Any) -> Event:
    return Event(
        event_type="consult",
        severity=0.5,
        occurred_at=datetime.utcnow(),
        description=description,
        workspace_id=TEST_WORKSPACE_ID,
        tenant_id=TEST_TENANT_ID,
        **kwargs,
    )


def make_edge(
    source: ConflictNode,
    target: ConflictNode,
    edge_type: EdgeType = EdgeType.PARTY_TO,
    **kwargs: Any,
) -> ConflictRelationship:
    return ConflictRelationship(
        type=edge_type,
        source_id=source.id,
        target_id=target.id,
        source_label=source.label,
        target_label=target.label,
        workspace_id=TEST_WORKSPACE_ID,
        tenant_id=TEST_TENANT_ID,
        **kwargs,
    )


# ── Mock Graph Client ──────────────────────────────────────────────────────


class MockGraphClient(GraphClient):
    """In-memory GraphClient for unit testing."""

    def __init__(self) -> None:
        self._nodes: dict[str, ConflictNode] = {}
        self._edges: dict[str, ConflictRelationship] = {}

    async def initialize_schema(self) -> None:
        pass

    async def upsert_node(
        self, node: ConflictNode, workspace_id: str, tenant_id: str
    ) -> str:
        node.workspace_id = workspace_id
        node.tenant_id = tenant_id
        self._nodes[node.id] = node
        return node.id

    async def delete_node(
        self, node_id: str, workspace_id: str, hard: bool = False
    ) -> bool:
        if hard:
            self._nodes.pop(node_id, None)
            self._edges = {
                eid: e
                for eid, e in self._edges.items()
                if e.source_id != node_id and e.target_id != node_id
            }
        else:
            node = self._nodes.get(node_id)
            if node:
                node.metadata["deleted_at"] = datetime.utcnow().isoformat()
        return True

    async def get_node(
        self, node_id: str, workspace_id: str
    ) -> ConflictNode | None:
        node = self._nodes.get(node_id)
        if node and node.workspace_id == workspace_id:
            if "deleted_at" not in node.metadata:
                return node
        return None

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        nodes = [
            n
            for n in self._nodes.values()
            if n.workspace_id == workspace_id and "deleted_at" not in n.metadata
        ]
        if label:
            nodes = [n for n in nodes if n.label == label]
        return nodes[offset : offset + limit]

    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        edge.workspace_id = workspace_id
        edge.tenant_id = tenant_id
        self._edges[edge.id] = edge
        return edge.id

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        edges = [e for e in self._edges.values() if e.workspace_id == workspace_id]
        if edge_type:
            edges = [e for e in edges if str(e.type) == edge_type]
        return edges

    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        visited: set[str] = set()
        current = {start_id}
        all_nodes: list[ConflictNode] = []
        all_edges: list[ConflictRelationship] = []

        for _ in range(hops):
            next_ids: set[str] = set()
            for nid in current:
                if nid in visited:
                    continue
                visited.add(nid)
                node = await self.get_node(nid, workspace_id)
                if node:
                    all_nodes.append(node)
                for edge in self._edges.values():
                    if edge_types and str(edge.type) not in edge_types:
                        continue
                    if edge.source_id == nid and edge.target_id not in visited:
                        all_edges.append(edge)
                        next_ids.add(edge.target_id)
                    elif edge.target_id == nid and edge.source_id not in visited:
                        all_edges.append(edge)
                        next_ids.add(edge.source_id)
            current = next_ids

        # Pick up remaining in current
        for nid in current:
            if nid not in visited:
                node = await self.get_node(nid, workspace_id)
                if node:
                    all_nodes.append(node)

        return SubgraphResult(nodes=all_nodes, edges=all_edges)

    async def vector_search(
        self,
        embedding: list[float],
        workspace_id: str,
        label: str | None = None,
        top_k: int = 10,
    ) -> list[ScoredNode]:
        from dialectica_graph.vector import cosine_similarity

        candidates = await self.get_nodes(workspace_id, label=label)
        scored = []
        for node in candidates:
            if node.embedding:
                sim = cosine_similarity(embedding, node.embedding)
                scored.append(ScoredNode(node=node, score=sim, distance=1.0 - sim))
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:top_k]

    async def execute_query(
        self, query: str, params: dict | None = None
    ) -> list[dict]:
        return []

    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        stats = WorkspaceStats()
        nodes = await self.get_nodes(workspace_id)
        for node in nodes:
            stats.node_counts_by_label[node.label] = (
                stats.node_counts_by_label.get(node.label, 0) + 1
            )
            stats.total_nodes += 1
        edges = await self.get_edges(workspace_id)
        for edge in edges:
            t = str(edge.type)
            stats.edge_counts_by_type[t] = stats.edge_counts_by_type.get(t, 0) + 1
            stats.total_edges += 1
        stats.compute_density()
        return stats

    async def get_actor_network(
        self, actor_id: str, workspace_id: str
    ) -> ActorNetworkResult:
        actor = await self.get_node(actor_id, workspace_id)
        if not actor:
            raise ValueError(f"Actor {actor_id} not found")
        return ActorNetworkResult(actor=actor)

    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        events = await self.get_nodes(workspace_id, label="Event")
        return sorted(events, key=lambda e: e.created_at)

    async def get_escalation_trajectory(
        self, workspace_id: str
    ) -> EscalationResult:
        return EscalationResult()

    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for node in nodes:
            nid = await self.upsert_node(node, workspace_id, tenant_id)
            ids.append(nid)
        return ids

    async def batch_upsert_edges(
        self,
        edges: list[ConflictRelationship],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for edge in edges:
            eid = await self.upsert_edge(edge, workspace_id, tenant_id)
            ids.append(eid)
        return ids

    async def close(self) -> None:
        pass


@pytest.fixture
def mock_client() -> MockGraphClient:
    """Provide an in-memory MockGraphClient for unit tests."""
    return MockGraphClient()


@pytest.fixture
def sample_actors() -> list[Actor]:
    return [make_actor(f"Actor {i}") for i in range(3)]


@pytest.fixture
def sample_conflict() -> Conflict:
    return make_conflict("Border Dispute")


@pytest.fixture
def sample_events() -> list[Event]:
    base = datetime(2024, 1, 1)
    return [
        make_event(f"Event {i}", occurred_at=base + timedelta(days=i * 30))
        for i in range(5)
    ]
