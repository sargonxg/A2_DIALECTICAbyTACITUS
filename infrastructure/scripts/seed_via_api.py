"""
API-based Sample Data Seeder — Load conflict data via REST API.

Proves the full API stack works end-to-end by creating workspaces
and entities through the HTTP endpoints.

Usage:
    uv run python infrastructure/scripts/seed_via_api.py
    # Or:
    API_URL=http://localhost:8080 API_KEY=dev-admin-key-local uv run python infrastructure/scripts/seed_via_api.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT / "data" / "seed" / "samples"


def seed_file(client: httpx.Client, filepath: Path) -> dict[str, int]:
    """Seed a single sample file via the REST API."""
    with open(filepath) as f:
        data = json.load(f)

    workspace_meta = data.get("workspace", {})
    workspace_id = f"ws_{filepath.stem}"
    workspace_name = workspace_meta.get("name", filepath.stem)

    logger.info("Seeding %s via API (workspace: %s)", filepath.name, workspace_id)

    # Create workspace
    resp = client.post(
        "/v1/workspaces",
        json={
            "workspace_id": workspace_id,
            "name": workspace_name,
            "domain": workspace_meta.get("domain", "workplace"),
            "scale": workspace_meta.get("scale", "micro"),
            "tier": workspace_meta.get("tier", "essential"),
        },
    )
    if resp.status_code not in (200, 201, 409):
        logger.warning("  Workspace create: %d %s", resp.status_code, resp.text[:200])

    # Create entities (nodes)
    node_count = 0
    for raw_node in data.get("nodes", []):
        resp = client.post(
            f"/v1/workspaces/{workspace_id}/entities",
            json=raw_node,
        )
        if resp.status_code in (200, 201):
            node_count += 1
        else:
            logger.debug(
                "  Node %s: %d %s",
                raw_node.get("id", "?"),
                resp.status_code,
                resp.text[:100],
            )

    # Create relationships (edges)
    edge_count = 0
    for raw_edge in data.get("edges", []):
        resp = client.post(
            f"/v1/workspaces/{workspace_id}/relationships",
            json=raw_edge,
        )
        if resp.status_code in (200, 201):
            edge_count += 1
        else:
            logger.debug(
                "  Edge %s->%s: %d %s",
                raw_edge.get("source", "?"),
                raw_edge.get("target", "?"),
                resp.status_code,
                resp.text[:100],
            )

    logger.info("  %s: %d nodes, %d edges via API", filepath.stem, node_count, edge_count)
    return {"nodes": node_count, "edges": edge_count}


def main() -> None:
    """Seed all sample data via the REST API."""
    api_url = os.getenv("API_URL", "http://localhost:8080")
    api_key = os.getenv("API_KEY", os.getenv("ADMIN_API_KEY", "dev-admin-key-local"))

    logger.info("Connecting to API at %s", api_url)

    client = httpx.Client(
        base_url=api_url,
        headers={"X-API-Key": api_key},
        timeout=30.0,
    )

    # Health check
    try:
        resp = client.get("/health")
        resp.raise_for_status()
        logger.info("API health: %s", resp.json().get("status"))
    except Exception as e:
        logger.error("API not reachable at %s: %s", api_url, e)
        sys.exit(1)

    sample_files = sorted(SAMPLES_DIR.glob("*.json"))
    if not sample_files:
        logger.error("No sample files found in %s", SAMPLES_DIR)
        sys.exit(1)

    logger.info("Found %d sample files", len(sample_files))

    total_nodes = 0
    total_edges = 0

    for filepath in sample_files:
        try:
            counts = seed_file(client, filepath)
            total_nodes += counts["nodes"]
            total_edges += counts["edges"]
        except Exception as e:
            logger.error("Failed to seed %s: %s", filepath.name, e)

    client.close()

    logger.info("=" * 60)
    logger.info(
        "API seeding complete: %d files, %d nodes, %d edges",
        len(sample_files),
        total_nodes,
        total_edges,
    )


if __name__ == "__main__":
    main()
