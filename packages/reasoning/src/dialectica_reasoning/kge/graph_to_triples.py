"""Convert graph database content to PyKEEN triples factory format."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from dialectica_graph import GraphClient

logger = logging.getLogger(__name__)


async def graph_to_triples(
    graph_client: GraphClient,
    workspace_id: str,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[tuple[str, str, str]]:
    """Extract (head, relation, tail) triples from the graph.

    Args:
        graph_client: Graph database client.
        workspace_id: Workspace to extract from.
        date_from: Optional start date filter for Event nodes.
        date_to: Optional end date filter for Event nodes.

    Returns:
        List of (head_id, relation_type, tail_id) string triples.
    """
    edges = await graph_client.get_edges(workspace_id)
    triples: list[tuple[str, str, str]] = []

    for edge in edges:
        rel_type = edge.type.value if hasattr(edge.type, "value") else str(edge.type)
        triples.append((edge.source_id, rel_type, edge.target_id))

    logger.info("Extracted %d triples from workspace %s", len(triples), workspace_id)
    return triples


def triples_to_pykeen_factory(
    triples: list[tuple[str, str, str]],
) -> Any:
    """Convert triples to PyKEEN TriplesFactory.

    Returns:
        A pykeen.triples.TriplesFactory instance.
    """
    try:
        from pykeen.triples import TriplesFactory
        import numpy as np

        if not triples:
            raise ValueError("No triples to create factory from")

        mapped = np.array(triples, dtype=str)
        return TriplesFactory.from_labeled_triples(mapped)
    except ImportError:
        raise ImportError("PyKEEN not installed. Install with: pip install pykeen>=1.11")
