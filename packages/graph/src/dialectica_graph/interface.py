"""
GraphClient Interface — Abstract base class for all graph database backends.

Defines the contract that SpannerGraphClient and Neo4jGraphClient must implement.
All methods are async. All operations are scoped by workspace_id + tenant_id.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship

from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)


class GraphClient(ABC):
    """Abstract interface for graph database operations.

    Implemented by SpannerGraphClient (primary) and Neo4jGraphClient (secondary).
    All data access is scoped by workspace_id and tenant_id for multi-tenancy.
    """

    # ── Schema Management ──────────────────────────────────────────────────

    @abstractmethod
    async def initialize_schema(self) -> None:
        """Create tables, indexes, and property graph definition."""
        ...

    # ── Node CRUD ──────────────────────────────────────────────────────────

    @abstractmethod
    async def upsert_node(
        self, node: ConflictNode, workspace_id: str, tenant_id: str
    ) -> str:
        """Insert or update a node. Returns the node ID."""
        ...

    @abstractmethod
    async def delete_node(
        self, node_id: str, workspace_id: str, hard: bool = False
    ) -> bool:
        """Soft-delete (set deleted_at) or hard-delete a node. Returns success."""
        ...

    @abstractmethod
    async def get_node(
        self, node_id: str, workspace_id: str
    ) -> ConflictNode | None:
        """Retrieve a single node by ID within a workspace."""
        ...

    @abstractmethod
    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        """List nodes in a workspace, optionally filtered by label."""
        ...

    # ── Edge CRUD ──────────────────────────────────────────────────────────

    @abstractmethod
    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        """Insert or update an edge. Returns the edge ID."""
        ...

    @abstractmethod
    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        """List edges in a workspace, optionally filtered by type."""
        ...

    # ── Traversal ──────────────────────────────────────────────────────────

    @abstractmethod
    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        """N-hop subgraph traversal from a starting node."""
        ...

    # ── Vector Search ──────────────────────────────────────────────────────

    @abstractmethod
    async def vector_search(
        self,
        embedding: list[float],
        workspace_id: str,
        label: str | None = None,
        top_k: int = 10,
    ) -> list[ScoredNode]:
        """Semantic similarity search using cosine distance on embeddings."""
        ...

    # ── Raw Query ──────────────────────────────────────────────────────────

    @abstractmethod
    async def execute_query(
        self, query: str, params: dict | None = None
    ) -> list[dict]:
        """Execute a raw GQL (Spanner) or Cypher (Neo4j) query."""
        ...

    # ── Analytics ──────────────────────────────────────────────────────────

    @abstractmethod
    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        """Node/edge counts, density metrics for a workspace."""
        ...

    @abstractmethod
    async def get_actor_network(
        self, actor_id: str, workspace_id: str
    ) -> ActorNetworkResult:
        """Get an actor's alliance/opposition network with centrality scores."""
        ...

    @abstractmethod
    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        """Get time-ordered events in a workspace, optionally within a date range."""
        ...

    @abstractmethod
    async def get_escalation_trajectory(
        self, workspace_id: str
    ) -> EscalationResult:
        """Compute Glasl escalation trajectory for a workspace's conflicts."""
        ...

    # ── Batch Operations ───────────────────────────────────────────────────

    @abstractmethod
    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        """Bulk insert/update nodes. Returns list of node IDs."""
        ...

    @abstractmethod
    async def batch_upsert_edges(
        self,
        edges: list[ConflictRelationship],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        """Bulk insert/update edges. Returns list of edge IDs."""
        ...

    # ── Lifecycle ──────────────────────────────────────────────────────────

    @abstractmethod
    async def close(self) -> None:
        """Release connections and clean up resources."""
        ...
