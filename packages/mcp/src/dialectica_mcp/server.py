"""
DIALECTICA MCP Server — FastMCP server exposing conflict intelligence tools.

Tools:
  - query_conflict_graph: GraphRAG retrieval + synthesis
  - get_actor_analysis: Actor network + power dynamics
  - get_escalation_status: Glasl stage + trajectory
  - compare_conflicts: Cross-case structural similarity
  - ingest_document: Extract and store conflict data
  - check_health: Verify graph connectivity
  - get_knowledge_clusters: Retrieve knowledge clusters for a workspace
"""

from __future__ import annotations

import json
import logging
import os
import re
import traceback
from typing import Any

logger = logging.getLogger(__name__)

# ── Validation constants ─────────────────────────────────────────────────────

_WORKSPACE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")
_MAX_TEXT_LENGTH = 500_000  # 500K characters
_MAX_QUERY_LENGTH = 10_000


def _validate_workspace_id(workspace_id: str) -> None:
    """Validate workspace_id format."""
    if not workspace_id or not _WORKSPACE_ID_PATTERN.match(workspace_id):
        raise ValueError(
            f"Invalid workspace_id: {workspace_id!r}. "
            "Must be 1-128 alphanumeric, dash, or underscore characters."
        )


def _validate_text_length(
    text: str, max_length: int = _MAX_TEXT_LENGTH, field: str = "text"
) -> None:
    """Validate text length is within bounds."""
    if len(text) > max_length:
        raise ValueError(
            f"{field} exceeds maximum length of {max_length} characters "
            f"(got {len(text)})."
        )


def _error_response(tool_name: str, error: Exception) -> str:
    """Format a structured error response for MCP tool failures."""
    logger.error(
        '{"event":"mcp_tool_error","tool":"%s","error":"%s","traceback":"%s"}',
        tool_name,
        str(error),
        traceback.format_exc(),
    )
    return json.dumps(
        {
            "error": True,
            "tool": tool_name,
            "message": str(error),
            "type": type(error).__name__,
        },
        indent=2,
    )


def create_mcp_server() -> Any:
    """Create and configure the FastMCP server with all DIALECTICA tools."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "DIALECTICA Conflict Intelligence",
        description=(
            "Neurosymbolic conflict intelligence engine by TACITUS. "
            "Query conflict knowledge graphs, analyze actors, track escalation, "
            "and ingest documents into structured conflict graphs."
        ),
    )

    # ── Tool: Check Health ───────────────────────────────────────────────

    @mcp.tool()
    async def check_health() -> str:
        """Check health of the DIALECTICA graph backend.

        Verifies that the graph database is reachable and responsive.

        Returns:
            Health status with connectivity details.
        """
        try:
            gc = _get_graph_client()
            # Attempt a lightweight query to verify connectivity
            try:
                await gc.initialize_schema()
                status = "healthy"
                detail = "Graph backend is reachable and schema initialized."
            except Exception as exc:
                status = "degraded"
                detail = f"Graph backend reachable but schema init failed: {exc}"

            backend = os.getenv("GRAPH_BACKEND", "neo4j")
            return json.dumps(
                {
                    "status": status,
                    "backend": backend,
                    "detail": detail,
                },
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "status": "unhealthy",
                    "backend": os.getenv("GRAPH_BACKEND", "neo4j"),
                    "detail": f"Cannot connect to graph backend: {e}",
                },
                indent=2,
            )

    # ── Tool: Query Conflict Graph ────────────────────────────────────────

    @mcp.tool()
    async def query_conflict_graph(
        query: str,
        workspace_id: str,
        tenant_id: str = "default",
        top_k: int = 20,
    ) -> str:
        """Query the conflict knowledge graph using GraphRAG retrieval + synthesis.

        Args:
            query: Natural language query about the conflict.
            workspace_id: Workspace ID to search.
            tenant_id: Tenant ID for isolation.
            top_k: Maximum results to return.

        Returns:
            Structured conflict context with cited sources.
        """
        try:
            _validate_workspace_id(workspace_id)
            _validate_text_length(query, _MAX_QUERY_LENGTH, "query")
            if top_k < 1 or top_k > 1000:
                raise ValueError("top_k must be between 1 and 1000.")

            gc = _get_graph_client()
            from dialectica_reasoning.graphrag import (
                ConflictContextBuilder,
                ConflictGraphRAGRetriever,
            )

            retriever = ConflictGraphRAGRetriever(graph_client=gc)
            result = await retriever.retrieve(
                query=query,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                top_k=top_k,
            )

            builder = ConflictContextBuilder()
            context = builder.build_context(result)
            return context
        except Exception as e:
            return _error_response("query_conflict_graph", e)

    # ── Tool: Get Actor Analysis ──────────────────────────────────────────

    @mcp.tool()
    async def get_actor_analysis(
        actor_name: str,
        workspace_id: str,
        tenant_id: str = "default",
    ) -> str:
        """Analyze an actor's network, alliances, oppositions, and power dynamics.

        Args:
            actor_name: Name of the actor to analyze.
            workspace_id: Workspace ID.
            tenant_id: Tenant ID.

        Returns:
            Actor analysis with network, power, and trust information.
        """
        try:
            _validate_workspace_id(workspace_id)
            if not actor_name or not actor_name.strip():
                raise ValueError("actor_name must be a non-empty string.")
            _validate_text_length(actor_name, 500, "actor_name")

            gc = _get_graph_client()

            # Find actor by name
            nodes = await gc.get_nodes(workspace_id, label="Actor", limit=200)
            actor = None
            for n in nodes:
                if getattr(n, "name", "").lower() == actor_name.lower():
                    actor = n
                    break

            if not actor:
                return f"Actor '{actor_name}' not found in workspace {workspace_id}."

            network = await gc.get_actor_network(actor.id, workspace_id)
            allies = [getattr(a, "name", a.id) for a in getattr(network, "allies", [])]
            opponents = [getattr(o, "name", o.id) for o in getattr(network, "opponents", [])]

            result = {
                "actor": actor_name,
                "actor_type": getattr(actor, "actor_type", "unknown"),
                "allies": allies,
                "opponents": opponents,
                "connections": len(getattr(network, "connections", [])),
                "centrality": getattr(network, "centrality_scores", {}),
            }
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return _error_response("get_actor_analysis", e)

    # ── Tool: Get Escalation Status ───────────────────────────────────────

    @mcp.tool()
    async def get_escalation_status(
        workspace_id: str,
        tenant_id: str = "default",
    ) -> str:
        """Get the Glasl escalation stage and trajectory for a conflict workspace.

        Args:
            workspace_id: Workspace ID.
            tenant_id: Tenant ID.

        Returns:
            Escalation status with current stage, velocity, and direction.
        """
        try:
            _validate_workspace_id(workspace_id)

            gc = _get_graph_client()
            esc = await gc.get_escalation_trajectory(workspace_id)

            result = {
                "current_stage": esc.current_stage,
                "velocity": round(esc.velocity, 2),
                "direction": esc.direction,
                "trajectory_points": len(esc.trajectory),
            }

            if esc.trajectory:
                result["latest_point"] = {
                    "timestamp": str(esc.trajectory[-1].timestamp),
                    "glasl_stage": esc.trajectory[-1].glasl_stage,
                    "evidence": esc.trajectory[-1].evidence,
                }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return _error_response("get_escalation_status", e)

    # ── Tool: Compare Conflicts ───────────────────────────────────────────

    @mcp.tool()
    async def compare_conflicts(
        workspace_a: str,
        workspace_b: str,
        tenant_id: str = "default",
    ) -> str:
        """Compare two conflict workspaces for structural similarity.

        Args:
            workspace_a: First workspace ID.
            workspace_b: Second workspace ID.
            tenant_id: Tenant ID.

        Returns:
            Comparison with shared patterns, actor counts, and escalation stages.
        """
        try:
            _validate_workspace_id(workspace_a)
            _validate_workspace_id(workspace_b)

            gc = _get_graph_client()

            stats_a = await gc.get_workspace_stats(workspace_a)
            stats_b = await gc.get_workspace_stats(workspace_b)

            esc_a = await gc.get_escalation_trajectory(workspace_a)
            esc_b = await gc.get_escalation_trajectory(workspace_b)

            # Simple structural comparison
            shared_node_types = set(stats_a.node_counts_by_label.keys()) & set(
                stats_b.node_counts_by_label.keys()
            )
            shared_edge_types = set(stats_a.edge_counts_by_type.keys()) & set(
                stats_b.edge_counts_by_type.keys()
            )

            result = {
                "workspace_a": {
                    "total_nodes": stats_a.total_nodes,
                    "total_edges": stats_a.total_edges,
                    "density": round(stats_a.density, 4),
                    "escalation_stage": esc_a.current_stage,
                    "escalation_direction": esc_a.direction,
                },
                "workspace_b": {
                    "total_nodes": stats_b.total_nodes,
                    "total_edges": stats_b.total_edges,
                    "density": round(stats_b.density, 4),
                    "escalation_stage": esc_b.current_stage,
                    "escalation_direction": esc_b.direction,
                },
                "shared_node_types": list(shared_node_types),
                "shared_edge_types": list(shared_edge_types),
                "structural_similarity": len(shared_node_types)
                / max(
                    len(
                        set(stats_a.node_counts_by_label.keys())
                        | set(stats_b.node_counts_by_label.keys())
                    ),
                    1,
                ),
            }
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            return _error_response("compare_conflicts", e)

    # ── Tool: Ingest Document ─────────────────────────────────────────────

    @mcp.tool()
    async def ingest_document(
        text: str,
        workspace_id: str,
        tier: str = "standard",
        tenant_id: str = "default",
    ) -> str:
        """Extract conflict entities from text and store in the knowledge graph.

        Args:
            text: Document text to extract from.
            workspace_id: Target workspace.
            tier: Ontology tier (essential, standard, full).
            tenant_id: Tenant ID.

        Returns:
            Extraction results with node and edge counts.
        """
        try:
            _validate_workspace_id(workspace_id)
            _validate_text_length(text, _MAX_TEXT_LENGTH, "text")
            if not text.strip():
                raise ValueError("text must be a non-empty string.")
            if tier not in ("essential", "standard", "full"):
                raise ValueError(f"tier must be one of: essential, standard, full (got {tier!r}).")

            from dialectica_extraction.pipeline import ExtractionPipeline
            from dialectica_ontology.tiers import OntologyTier

            pipeline = ExtractionPipeline()
            result = pipeline.run(
                text=text,
                tier=OntologyTier(tier),
                workspace_id=workspace_id,
                tenant_id=tenant_id,
            )

            stats = result.get("ingestion_stats", {})
            errors = result.get("errors", [])

            return json.dumps(
                {
                    "status": "complete",
                    "nodes_extracted": stats.get("nodes_written", 0),
                    "edges_extracted": stats.get("edges_written", 0),
                    "errors": len(errors),
                    "review_needed": result.get("requires_review", False),
                    "review_reasons": result.get("review_reasons", []),
                },
                indent=2,
            )
        except Exception as e:
            return _error_response("ingest_document", e)

    # ── Tool: Get Knowledge Clusters ──────────────────────────────────────

    @mcp.tool()
    async def get_knowledge_clusters(
        workspace_id: str,
        tenant_id: str = "default",
    ) -> str:
        """Retrieve knowledge clusters (topic groups) for a workspace.

        Args:
            workspace_id: Workspace ID.
            tenant_id: Tenant ID.

        Returns:
            Knowledge clusters with topics, sizes, and key entities.
        """
        try:
            _validate_workspace_id(workspace_id)

            gc = _get_graph_client()

            # Try importing the knowledge clusters module
            try:
                from dialectica_reasoning.knowledge_clusters import KnowledgeClusterAnalyzer

                analyzer = KnowledgeClusterAnalyzer(graph_client=gc)
                clusters = await analyzer.compute_clusters(workspace_id)
                return json.dumps(
                    {
                        "workspace_id": workspace_id,
                        "clusters": [
                            {
                                "id": c.cluster_id,
                                "topic": c.topic,
                                "size": c.size,
                                "key_entities": c.key_entities[:10],
                            }
                            for c in clusters
                        ],
                        "total_clusters": len(clusters),
                    },
                    indent=2,
                    default=str,
                )
            except ImportError:
                # Knowledge clusters module not available — fall back to
                # community detection via network analyzer if available
                try:
                    from dialectica_reasoning.symbolic.network_metrics import NetworkAnalyzer

                    analyzer = NetworkAnalyzer(graph_client=gc)
                    communities = await analyzer.detect_communities(workspace_id)
                    return json.dumps(
                        {
                            "workspace_id": workspace_id,
                            "clusters": [
                                {
                                    "id": c.community_id,
                                    "topic": f"Community {c.community_id}",
                                    "size": len(c.actor_ids),
                                    "key_entities": c.actor_ids[:10],
                                }
                                for c in communities
                            ],
                            "total_clusters": len(communities),
                            "source": "community_detection_fallback",
                        },
                        indent=2,
                        default=str,
                    )
                except Exception:
                    return json.dumps(
                        {
                            "workspace_id": workspace_id,
                            "clusters": [],
                            "total_clusters": 0,
                            "message": "Knowledge clusters module not available.",
                        },
                        indent=2,
                    )
        except Exception as e:
            return _error_response("get_knowledge_clusters", e)

    return mcp


def _get_graph_client() -> Any:
    """Get or create the graph client based on environment config."""
    from dialectica_graph import create_graph_client

    backend = os.getenv("GRAPH_BACKEND", "neo4j")
    config: dict[str, Any] = {}

    if backend == "falkordb":
        config = {
            "host": os.getenv("FALKORDB_HOST", "localhost"),
            "port": int(os.getenv("FALKORDB_PORT", "6379")),
        }
    elif backend == "neo4j":
        config = {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "username": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "dialectica-dev"),
        }
    elif backend == "spanner":
        config = {
            "project_id": os.getenv("GCP_PROJECT_ID", "local-project"),
            "instance_id": os.getenv("SPANNER_INSTANCE_ID", "dialectica-graph"),
            "database_id": os.getenv("SPANNER_DATABASE_ID", "dialectica"),
        }

    return create_graph_client(backend=backend, config=config)


def main() -> None:
    """Run the MCP server."""
    mcp = create_mcp_server()
    mcp.run()


if __name__ == "__main__":
    main()
