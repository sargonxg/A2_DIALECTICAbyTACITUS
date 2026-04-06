"""
Qdrant Vector Store — Simplified node-level vector store for DIALECTICA.

Single-vector collection (768-dim cosine) for semantic search over conflict graph nodes.
Supports tenant-isolated queries with node type and date filtering.

For the full dual-vector store (semantic + structural KGE), see vector.py.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

COLLECTION_NAME = "dialectica_nodes"
VECTOR_DIM = 768


class QdrantVectorStore:
    """Qdrant-backed vector store for semantic node search.

    Provides a simplified interface for upserting and searching node embeddings
    with tenant isolation. Uses a single 768-dim cosine vector per node.

    Args:
        url: Qdrant server URL (e.g. "http://localhost:6333").
        api_key: Optional API key for Qdrant Cloud.
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
    ) -> None:
        self._url = url
        self._api_key = api_key
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazy-init the Qdrant client."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient

                self._client = QdrantClient(url=self._url, api_key=self._api_key)
            except ImportError as err:
                raise ImportError(
                    "qdrant-client not installed. Install with: pip install qdrant-client>=1.12"
                ) from err
        return self._client

    async def _ensure_collection(self) -> None:
        """Create the 'dialectica_nodes' collection with 768-dim cosine vectors if absent."""
        from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

        client = self._get_client()

        collections = client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)

        if not exists:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
            )
            for field_name, schema_type in [
                ("tenant_id", PayloadSchemaType.KEYWORD),
                ("workspace_id", PayloadSchemaType.KEYWORD),
                ("node_type", PayloadSchemaType.KEYWORD),
                ("node_id", PayloadSchemaType.KEYWORD),
            ]:
                client.create_payload_index(
                    collection_name=COLLECTION_NAME,
                    field_name=field_name,
                    field_schema=schema_type,
                )
            logger.info("Created Qdrant collection: %s", COLLECTION_NAME)

    async def search_semantic(
        self,
        query_embedding: list[float],
        tenant_id: str,
        top_k: int = 10,
        node_types: list[str] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Search by semantic similarity with tenant isolation.

        Args:
            query_embedding: 768-dim query vector.
            tenant_id: Tenant scope for multi-tenancy.
            top_k: Maximum results to return.
            node_types: Optional filter to specific node types (e.g. ["Actor", "Event"]).
            date_from: Optional lower bound on created_at.
            date_to: Optional upper bound on created_at.

        Returns:
            List of dicts with node_id, score, and label.
        """
        from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

        client = self._get_client()
        must_conditions = [
            FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
        ]
        if node_types:
            for nt in node_types:
                must_conditions.append(
                    FieldCondition(key="node_type", match=MatchValue(value=nt))
                )
        if date_from or date_to:
            range_params: dict[str, Any] = {}
            if date_from:
                range_params["gte"] = date_from.isoformat()
            if date_to:
                range_params["lte"] = date_to.isoformat()
            must_conditions.append(
                FieldCondition(key="created_at", range=Range(**range_params))
            )

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=Filter(must=must_conditions),
            with_payload=True,
        )

        return [
            {
                "node_id": r.payload.get("node_id", ""),
                "score": r.score,
                "label": r.payload.get("node_type", ""),
            }
            for r in results.points
        ]

    async def upsert_vectors(
        self,
        node_id: str,
        embedding: list[float],
        workspace_id: str,
        tenant_id: str,
        label: str = "",
        name: str = "",
    ) -> None:
        """Upsert a single node embedding.

        Args:
            node_id: Unique node identifier.
            embedding: 768-dim vector.
            workspace_id: Workspace scope.
            tenant_id: Tenant scope.
            label: Node type label (e.g. "Actor").
            name: Human-readable node name.
        """
        from qdrant_client.models import PointStruct

        client = self._get_client()
        point_id = abs(hash(node_id)) % (2**63)
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "node_id": node_id,
                        "node_type": label,
                        "workspace_id": workspace_id,
                        "tenant_id": tenant_id,
                        "name": name,
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
            ],
        )

    async def batch_upsert(self, items: list[dict[str, Any]]) -> int:
        """Bulk upsert multiple node embeddings.

        Args:
            items: List of dicts, each with keys:
                node_id, embedding, workspace_id, tenant_id, label, name.

        Returns:
            Number of points upserted.
        """
        from qdrant_client.models import PointStruct

        client = self._get_client()
        points: list[PointStruct] = []

        for item in items:
            embedding = item.get("embedding")
            node_id = item.get("node_id", "")
            if not embedding or not node_id:
                continue
            point_id = abs(hash(node_id)) % (2**63)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "node_id": node_id,
                        "node_type": item.get("label", ""),
                        "workspace_id": item.get("workspace_id", ""),
                        "tenant_id": item.get("tenant_id", ""),
                        "name": item.get("name", ""),
                        "created_at": datetime.utcnow().isoformat(),
                    },
                )
            )

        if points:
            client.upsert(collection_name=COLLECTION_NAME, points=points)
            logger.info("Batch upserted %d vectors to Qdrant", len(points))

        return len(points)

    async def close(self) -> None:
        """Close the Qdrant client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
