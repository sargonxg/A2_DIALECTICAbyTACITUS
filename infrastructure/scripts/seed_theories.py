"""
Theory Frameworks Seeder — Upsert 15 TheoryFrameworkNode nodes into Neo4j.

Reads data/seed/theories/theory_frameworks.json and populates the graph
database with durable TheoryFrameworkNode nodes. These nodes are shared
across all tenants as the universal theory scaffold.

LLM agents traverse: Conflict -[ASSESSED_VIA]-> TheoryFrameworkNode

Usage:
    uv run python infrastructure/scripts/seed_theories.py
    # Or with env vars:
    NEO4J_URI=bolt://localhost:7687 NEO4J_PASSWORD=dialectica-dev \
        uv run python infrastructure/scripts/seed_theories.py
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add packages to path for direct execution
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "ontology" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "graph" / "src"))

from dialectica_graph import create_graph_client  # noqa: E402
from dialectica_ontology.primitives import TheoryFrameworkNode  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

THEORIES_FILE = ROOT / "data" / "seed" / "theories" / "theory_frameworks.json"

# Shared theory nodes are in a dedicated workspace/tenant
THEORY_WORKSPACE_ID = "ws_theory_scaffold"
THEORY_TENANT_ID = "shared"


async def seed_theories(graph_client: object) -> int:
    """Upsert all 15 TheoryFrameworkNode nodes and return count."""
    if not THEORIES_FILE.exists():
        logger.error("Theory frameworks file not found: %s", THEORIES_FILE)
        sys.exit(1)

    with open(THEORIES_FILE) as f:
        data = json.load(f)

    frameworks = data.get("theory_frameworks", [])
    if not frameworks:
        logger.error("No theory_frameworks found in %s", THEORIES_FILE)
        sys.exit(1)

    logger.info("Loading %d theory frameworks...", len(frameworks))

    count = 0
    for raw in frameworks:
        try:
            node = TheoryFrameworkNode(
                id=f"theory_{raw['framework_id']}",
                label="TheoryFrameworkNode",
                workspace_id=THEORY_WORKSPACE_ID,
                tenant_id=THEORY_TENANT_ID,
                framework_id=raw["framework_id"],
                display_name=raw["display_name"],
                domain=raw["domain"],
                core_concepts=raw.get("core_concepts", []),
                key_propositions=raw.get("key_propositions", []),
                escalation_indicators=raw.get("escalation_indicators", []),
                de_escalation_levers=raw.get("de_escalation_levers", []),
                primary_questions=raw.get("primary_questions", []),
                citations=raw.get("citations", []),
            )
            await graph_client.upsert_node(  # type: ignore[union-attr]
                node, THEORY_WORKSPACE_ID, THEORY_TENANT_ID
            )
            count += 1
            logger.info("  [%d/15] %s (%s)", count, node.display_name, node.domain)
        except Exception as e:
            logger.error("Failed to seed framework %r: %s", raw.get("framework_id"), e)

    return count


async def create_theory_index(graph_client: object) -> None:
    """Create index on TheoryFrameworkNode.framework_id for fast lookups."""
    cypher = (
        "CREATE INDEX theory_framework_id IF NOT EXISTS "
        "FOR (t:TheoryFrameworkNode) ON (t.framework_id)"
    )
    try:
        await graph_client.execute_query(cypher, {})  # type: ignore[union-attr]
        logger.info("Index :THEORY on framework_id created (or already exists)")
    except AttributeError:
        # graph_client may not expose execute_query directly — skip index creation
        logger.info("Skipping index creation (execute_query not available on this client)")
    except Exception as e:
        logger.warning("Could not create index: %s", e)


async def main() -> None:
    """Seed all 15 TheoryFrameworkNode entries into Neo4j."""
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

    count = await seed_theories(graph_client)
    await create_theory_index(graph_client)
    await graph_client.close()

    logger.info("=" * 60)
    logger.info("Theory seeding complete: %d TheoryFrameworkNode nodes upserted", count)


if __name__ == "__main__":
    asyncio.run(main())
