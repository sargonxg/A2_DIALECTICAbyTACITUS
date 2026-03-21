"""
Sample Data Seeder — Load conflict graph samples into Neo4j.

Reads all JSON files from data/seed/samples/ and populates the graph database
using the Neo4j graph client directly for speed.

Usage:
    uv run python infrastructure/scripts/seed_sample_data.py
    # Or with env vars:
    NEO4J_URI=bolt://localhost:7687 NEO4J_PASSWORD=dialectica-dev uv run python infrastructure/scripts/seed_sample_data.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add packages to path for direct execution
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "ontology" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "graph" / "src"))

from dialectica_ontology.primitives import NODE_TYPES, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_graph import create_graph_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SAMPLES_DIR = ROOT / "data" / "seed" / "samples"
DEFAULT_TENANT = "default"


def _parse_node(raw: dict[str, Any]) -> ConflictNode | None:
    """Parse a raw JSON node dict into a typed ConflictNode."""
    label = raw.get("label", "")
    model_cls = NODE_TYPES.get(label)
    if model_cls is None:
        logger.warning("Unknown node label %r — skipping", label)
        return None

    # Build kwargs from raw dict, keeping only fields the model accepts
    kwargs: dict[str, Any] = {}
    model_fields = set(model_cls.model_fields.keys())
    for key, value in raw.items():
        if key in model_fields:
            # Convert date strings to datetime for occurred_at etc.
            if key in ("occurred_at", "temporal_start", "temporal_end") and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    # Try date-only format
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                    except ValueError:
                        logger.warning("Cannot parse date %r for %s", value, key)
                        continue
            kwargs[key] = value

    try:
        return model_cls(**kwargs)
    except Exception as e:
        logger.warning("Failed to parse %s node %r: %s", label, raw.get("id", "?"), e)
        return None


def _parse_edge(raw: dict[str, Any]) -> ConflictRelationship | None:
    """Parse a raw JSON edge dict into a ConflictRelationship."""
    try:
        edge_type = raw.get("type", "")
        props = raw.get("properties", {})
        return ConflictRelationship(
            type=EdgeType(edge_type),
            source_id=raw["source"],
            target_id=raw["target"],
            properties=props,
            weight=props.get("weight", 1.0),
            confidence=props.get("confidence", 1.0),
        )
    except Exception as e:
        logger.warning("Failed to parse edge %s->%s: %s", raw.get("source"), raw.get("target"), e)
        return None


def _expand_simplified(data: dict[str, Any], workspace_id: str) -> tuple[list[dict], list[dict]]:
    """Expand simplified format (actors/conflict/events) into nodes/edges lists."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # Conflict node
    conflict_raw = data.get("conflict", {})
    conflict_id = f"{workspace_id}_conflict"
    conflict_raw["id"] = conflict_id
    conflict_raw["label"] = "Conflict"
    if "name" not in conflict_raw:
        conflict_raw["name"] = data.get("workspace", {}).get("name", workspace_id)
    nodes.append(conflict_raw)

    # Actors
    actor_ids: list[str] = []
    for i, actor_raw in enumerate(data.get("actors", [])):
        actor_id = f"{workspace_id}_actor_{i}"
        actor_raw["id"] = actor_id
        actor_raw["label"] = "Actor"
        nodes.append(actor_raw)
        actor_ids.append(actor_id)
        # Link actor to conflict
        edges.append({"source": actor_id, "target": conflict_id, "type": "PARTY_TO", "properties": {}})

    # Events
    prev_event_id: str | None = None
    for i, event_raw in enumerate(data.get("events", [])):
        event_id = f"{workspace_id}_event_{i}"
        event_raw["id"] = event_id
        event_raw["label"] = "Event"
        # Rename 'date' to 'occurred_at' if present
        if "date" in event_raw and "occurred_at" not in event_raw:
            event_raw["occurred_at"] = event_raw.pop("date")
        nodes.append(event_raw)
        # Chain events causally
        if prev_event_id:
            edges.append({
                "source": prev_event_id,
                "target": event_id,
                "type": "CAUSED",
                "properties": {"mechanism": "escalation"},
            })
        prev_event_id = event_id

    return nodes, edges


async def seed_file(filepath: Path, graph_client: Any) -> dict[str, int]:
    """Seed a single sample JSON file into the graph."""
    with open(filepath) as f:
        data = json.load(f)

    workspace_meta = data.get("workspace", {})
    workspace_name = workspace_meta.get("name", filepath.stem)
    workspace_id = f"ws_{filepath.stem}"
    tenant_id = DEFAULT_TENANT

    logger.info("Seeding %s (workspace: %s)", filepath.name, workspace_id)

    # Detect format: structured (nodes/edges) vs simplified (actors/conflict/events)
    raw_nodes: list[dict[str, Any]]
    raw_edges: list[dict[str, Any]]

    if "nodes" in data:
        # Structured format — nodes[] and edges[] with full ontology labels
        raw_nodes = data.get("nodes", [])
        raw_edges = data.get("edges", [])
    else:
        # Simplified format — actors[], conflict{}, events[]
        raw_nodes, raw_edges = _expand_simplified(data, workspace_id)

    # Parse nodes
    nodes: list[ConflictNode] = []
    id_remap: dict[str, str] = {}  # original_id -> pydantic model id
    for raw_node in raw_nodes:
        node = _parse_node(raw_node)
        if node is not None:
            original_id = raw_node.get("id", "")
            # Preserve original ID if provided
            if original_id:
                node.id = original_id
            id_remap[original_id] = node.id
            nodes.append(node)

    # Parse edges (remap IDs)
    edges: list[ConflictRelationship] = []
    for raw_edge in raw_edges:
        edge = _parse_edge(raw_edge)
        if edge is not None:
            # Remap source/target to actual node IDs
            edge.source_id = id_remap.get(edge.source_id, edge.source_id)
            edge.target_id = id_remap.get(edge.target_id, edge.target_id)
            edges.append(edge)

    # Create workspace node
    workspace_node_data = {
        "id": workspace_id,
        "label": "Conflict",
        "name": workspace_name,
        "scale": workspace_meta.get("scale", "micro"),
        "domain": workspace_meta.get("domain", "workplace"),
        "status": "active",
    }
    ws_node = _parse_node(workspace_node_data)

    # Upsert nodes
    node_count = 0
    if ws_node is not None:
        await graph_client.upsert_node(ws_node, workspace_id, tenant_id)
        node_count += 1

    node_ids = await graph_client.batch_upsert_nodes(nodes, workspace_id, tenant_id)
    node_count += len(node_ids)

    # Upsert edges
    edge_ids = await graph_client.batch_upsert_edges(edges, workspace_id, tenant_id)

    logger.info(
        "  %s: %d nodes, %d edges seeded",
        filepath.stem,
        node_count,
        len(edge_ids),
    )
    return {"nodes": node_count, "edges": len(edge_ids)}


async def main() -> None:
    """Load all sample data files into the graph database."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "dialectica-dev")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    backend = os.getenv("GRAPH_BACKEND", "neo4j")

    logger.info("Connecting to %s backend at %s", backend, uri)

    graph_client = create_graph_client(
        backend=backend,
        config={
            "uri": uri,
            "username": user,
            "password": password,
            "database": database,
        },
    )

    sample_files = sorted(SAMPLES_DIR.glob("*.json"))
    if not sample_files:
        logger.error("No sample files found in %s", SAMPLES_DIR)
        sys.exit(1)

    logger.info("Found %d sample files", len(sample_files))

    total_nodes = 0
    total_edges = 0

    for filepath in sample_files:
        try:
            counts = await seed_file(filepath, graph_client)
            total_nodes += counts["nodes"]
            total_edges += counts["edges"]
        except Exception as e:
            logger.error("Failed to seed %s: %s", filepath.name, e)

    await graph_client.close()

    logger.info("=" * 60)
    logger.info(
        "Seeding complete: %d files, %d nodes, %d edges",
        len(sample_files),
        total_nodes,
        total_edges,
    )


if __name__ == "__main__":
    asyncio.run(main())
