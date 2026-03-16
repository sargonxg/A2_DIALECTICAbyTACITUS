"""
Vector Utilities — Embedding storage and similarity search for DIALECTICA.

Provides cosine similarity computation, embedding normalization, and
batch vector search helpers.
"""
from __future__ import annotations

import math

from dialectica_ontology.primitives import ConflictNode

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import ScoredNode

EMBEDDING_DIM = 768


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        raise ValueError(f"Dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cosine_distance(a: list[float], b: list[float]) -> float:
    """Compute cosine distance (1 - similarity) between two vectors."""
    return 1.0 - cosine_similarity(a, b)


def normalize_embedding(embedding: list[float]) -> list[float]:
    """L2-normalize an embedding vector."""
    norm = math.sqrt(sum(x * x for x in embedding))
    if norm == 0:
        return embedding
    return [x / norm for x in embedding]


def validate_embedding(embedding: list[float] | None) -> bool:
    """Check that an embedding has valid dimensions."""
    if embedding is None:
        return True
    return len(embedding) in (128, EMBEDDING_DIM)


async def find_similar_nodes(
    client: GraphClient,
    reference_node: ConflictNode,
    workspace_id: str,
    top_k: int = 10,
    same_label_only: bool = False,
) -> list[ScoredNode]:
    """Find nodes semantically similar to a reference node.

    Args:
        client: GraphClient implementation.
        reference_node: Node whose embedding to use for search.
        workspace_id: Workspace scope.
        top_k: Number of results.
        same_label_only: Only return nodes with the same label.

    Returns:
        List of ScoredNode sorted by descending similarity.
    """
    if not reference_node.embedding:
        return []

    label = reference_node.label if same_label_only else None
    results = await client.vector_search(
        embedding=reference_node.embedding,
        workspace_id=workspace_id,
        label=label,
        top_k=top_k + 1,  # +1 to exclude self
    )

    # Exclude the reference node itself
    return [r for r in results if r.node.id != reference_node.id][:top_k]


async def find_duplicate_candidates(
    client: GraphClient,
    node: ConflictNode,
    workspace_id: str,
    threshold: float = 0.92,
) -> list[ScoredNode]:
    """Find potential duplicate nodes based on embedding similarity.

    Args:
        client: GraphClient implementation.
        node: Node to check for duplicates.
        workspace_id: Workspace scope.
        threshold: Minimum similarity score to consider a duplicate.

    Returns:
        Nodes with similarity >= threshold, same label, excluding self.
    """
    candidates = await find_similar_nodes(
        client, node, workspace_id, top_k=20, same_label_only=True
    )
    return [c for c in candidates if c.score >= threshold]
