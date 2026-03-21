"""KGE Exporter — Export trained embeddings to Qdrant structural named vector."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class KGEExporter:
    """Export KGE embeddings to Qdrant's structural named vector."""

    def __init__(self, vector_store: Any) -> None:
        self._vs = vector_store

    async def export_to_qdrant(
        self,
        embeddings: dict[str, list[float]],
        nodes: list[Any],
        tenant_id: str,
        workspace_id: str,
    ) -> int:
        """Upload structural embeddings to Qdrant.

        Args:
            embeddings: Dict mapping node_id to KGE embedding vector.
            nodes: ConflictNode objects to associate.
            tenant_id: Tenant for isolation.
            workspace_id: Workspace context.

        Returns:
            Number of vectors exported.
        """
        count = await self._vs.upsert_vectors(
            nodes=nodes,
            semantic_embeddings={},
            structural_embeddings=embeddings,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
        logger.info("Exported %d KGE embeddings to Qdrant", count)
        return count
