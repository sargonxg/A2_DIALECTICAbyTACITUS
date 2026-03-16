"""
DIALECTICA Graph Package — Database abstraction layer.

Provides a swappable GraphClient interface implemented by:
  SpannerGraphClient: Google Cloud Spanner Graph (primary, GCP-native)
  Neo4jGraphClient: Neo4j Aura (secondary, GDS algorithms)

Configure via GRAPH_BACKEND env var: "spanner" (default) or "neo4j".
"""
from __future__ import annotations

from typing import Any

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)

__all__ = [
    # Interface
    "GraphClient",
    # Factory
    "create_graph_client",
    # Models
    "SubgraphResult",
    "ScoredNode",
    "WorkspaceStats",
    "ActorNetworkResult",
    "EscalationResult",
    "EscalationTrajectoryPoint",
    # Clients (lazy imports)
    "SpannerGraphClient",
    "Neo4jGraphClient",
]


def create_graph_client(
    backend: str = "spanner",
    config: dict[str, Any] | None = None,
) -> GraphClient:
    """Factory function to create a GraphClient for the specified backend.

    Args:
        backend: "spanner" or "neo4j".
        config: Backend-specific configuration dict.
            Spanner: {"project_id", "instance_id", "database_id"}
            Neo4j: {"uri", "username", "password", "database"}

    Returns:
        A GraphClient instance.

    Raises:
        ValueError: If backend is not supported.
    """
    config = config or {}

    if backend == "spanner":
        from dialectica_graph.spanner_client import SpannerGraphClient

        return SpannerGraphClient(
            project_id=config.get("project_id", "local-project"),
            instance_id=config.get("instance_id", "dialectica-graph"),
            database_id=config.get("database_id", "dialectica"),
        )
    elif backend == "neo4j":
        from dialectica_graph.neo4j_client import Neo4jGraphClient

        return Neo4jGraphClient(
            uri=config.get("uri", "bolt://localhost:7687"),
            username=config.get("username", "neo4j"),
            password=config.get("password", "dialectica-dev"),
            database=config.get("database", "neo4j"),
        )
    else:
        raise ValueError(
            f"Unsupported graph backend: {backend!r}. Use 'spanner' or 'neo4j'."
        )


def __getattr__(name: str) -> Any:
    """Lazy import for client classes to avoid importing heavy SDKs at module level."""
    if name == "SpannerGraphClient":
        from dialectica_graph.spanner_client import SpannerGraphClient
        return SpannerGraphClient
    if name == "Neo4jGraphClient":
        from dialectica_graph.neo4j_client import Neo4jGraphClient
        return Neo4jGraphClient
    raise AttributeError(f"module 'dialectica_graph' has no attribute {name!r}")
