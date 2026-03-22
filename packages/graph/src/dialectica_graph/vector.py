"""
Qdrant Vector Store — Dual vector space with named vectors for DIALECTICA.

Named vectors:
  - semantic: 768-dim (Vertex AI text-embedding-005) for LLM semantic search
  - structural: 256-dim (RotatE via PyKEEN) for KGE structural similarity

Tenant isolation via payload filtering on tenant_id.
Supports hybrid search with Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from dialectica_ontology.primitives import ConflictNode

logger = logging.getLogger(__name__)

COLLECTION_NAME = "dialectica_entities"
SEMANTIC_DIM = 768
STRUCTURAL_DIM = 256


class QdrantVectorStore:
    """Qdrant-backed vector store with dual named vectors.

    Args:
        host: Qdrant server host.
        port: Qdrant gRPC port.
        api_key: Optional API key for Qdrant Cloud.
        collection_name: Override collection name.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6334,
        api_key: str | None = None,
        collection_name: str = COLLECTION_NAME,
    ) -> None:
        self._host = host
        self._port = port
        self._api_key = api_key
        self._collection_name = collection_name
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from qdrant_client import QdrantClient

                self._client = QdrantClient(
                    host=self._host,
                    port=self._port,
                    api_key=self._api_key,
                )
            except ImportError as err:
                raise ImportError(
                    "qdrant-client not installed. Install with: pip install qdrant-client>=1.12"
                ) from err
        return self._client

    async def initialize_collection(self) -> None:
        """Create the collection with named vectors if it doesn't exist."""
        from qdrant_client.models import (
            Distance,
            PayloadSchemaType,
            VectorParams,
        )

        client = self._get_client()

        collections = client.get_collections().collections
        exists = any(c.name == self._collection_name for c in collections)

        if not exists:
            client.create_collection(
                collection_name=self._collection_name,
                vectors_config={
                    "semantic": VectorParams(size=SEMANTIC_DIM, distance=Distance.COSINE),
                    "structural": VectorParams(size=STRUCTURAL_DIM, distance=Distance.COSINE),
                },
            )
            for field_name, schema_type in [
                ("tenant_id", PayloadSchemaType.KEYWORD),
                ("workspace_id", PayloadSchemaType.KEYWORD),
                ("node_type", PayloadSchemaType.KEYWORD),
                ("node_id", PayloadSchemaType.KEYWORD),
            ]:
                client.create_payload_index(
                    collection_name=self._collection_name,
                    field_name=field_name,
                    field_schema=schema_type,
                )
            logger.info("Created Qdrant collection: %s", self._collection_name)

    async def upsert_vectors(
        self,
        nodes: list[ConflictNode],
        semantic_embeddings: dict[str, list[float]],
        structural_embeddings: dict[str, list[float]] | None = None,
        tenant_id: str = "",
        workspace_id: str = "",
    ) -> int:
        """Upsert node vectors with both semantic and structural embeddings."""
        from qdrant_client.models import PointStruct

        client = self._get_client()
        points: list[PointStruct] = []

        for node in nodes:
            sem_emb = semantic_embeddings.get(node.id)
            if not sem_emb:
                continue

            vectors: dict[str, list[float]] = {"semantic": sem_emb}
            if structural_embeddings and node.id in structural_embeddings:
                vectors["structural"] = structural_embeddings[node.id]

            payload = {
                "node_id": node.id,
                "node_type": type(node).__name__,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "name": getattr(node, "name", ""),
                "description": getattr(node, "description", ""),
                "created_at": datetime.utcnow().isoformat(),
            }

            point_id = abs(hash(node.id)) % (2**63)
            points.append(PointStruct(id=point_id, vector=vectors, payload=payload))

        if points:
            client.upsert(collection_name=self._collection_name, points=points)
            logger.info("Upserted %d vectors to Qdrant", len(points))

        return len(points)

    async def search_semantic(
        self,
        query_embedding: list[float],
        tenant_id: str,
        top_k: int = 10,
        node_types: list[str] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        """Search by semantic similarity with tenant isolation."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

        client = self._get_client()
        must_conditions = [
            FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
        ]
        if node_types:
            for nt in node_types:
                must_conditions.append(FieldCondition(key="node_type", match=MatchValue(value=nt)))
        if date_from or date_to:
            range_params: dict[str, Any] = {}
            if date_from:
                range_params["gte"] = date_from.isoformat()
            if date_to:
                range_params["lte"] = date_to.isoformat()
            must_conditions.append(FieldCondition(key="created_at", range=Range(**range_params)))

        results = client.query_points(
            collection_name=self._collection_name,
            query=query_embedding,
            using="semantic",
            limit=top_k,
            query_filter=Filter(must=must_conditions),
            with_payload=True,
        )

        return [
            {"node_id": r.payload.get("node_id", ""), "score": r.score, "payload": r.payload}
            for r in results.points
        ]

    async def search_structural(
        self,
        kge_embedding: list[float],
        tenant_id: str,
        top_k: int = 10,
    ) -> list[dict]:
        """Search by structural (KGE) similarity."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        client = self._get_client()
        results = client.query_points(
            collection_name=self._collection_name,
            query=kge_embedding,
            using="structural",
            limit=top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
                ]
            ),
            with_payload=True,
        )

        return [
            {"node_id": r.payload.get("node_id", ""), "score": r.score, "payload": r.payload}
            for r in results.points
        ]

    async def hybrid_search(
        self,
        query_embedding: list[float],
        kge_embedding: list[float],
        tenant_id: str,
        top_k: int = 10,
    ) -> list[dict]:
        """Hybrid search combining semantic + structural via RRF fusion.

        score(d) = sum(1 / (60 + rank_i(d))) across both result sets.
        """
        semantic_results = await self.search_semantic(query_embedding, tenant_id, top_k=top_k * 2)
        structural_results = await self.search_structural(kge_embedding, tenant_id, top_k=top_k * 2)

        rrf_scores: dict[str, float] = {}
        payloads: dict[str, dict] = {}

        for rank, r in enumerate(semantic_results):
            nid = r["node_id"]
            rrf_scores[nid] = rrf_scores.get(nid, 0) + 1.0 / (60 + rank)
            payloads[nid] = r["payload"]

        for rank, r in enumerate(structural_results):
            nid = r["node_id"]
            rrf_scores[nid] = rrf_scores.get(nid, 0) + 1.0 / (60 + rank)
            if nid not in payloads:
                payloads[nid] = r["payload"]

        ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            {"node_id": nid, "score": score, "payload": payloads.get(nid, {})}
            for nid, score in ranked
        ]

    async def delete_tenant(self, tenant_id: str) -> None:
        """Delete all vectors for a tenant (GDPR erasure)."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        client = self._get_client()
        client.delete(
            collection_name=self._collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
                ]
            ),
        )
        logger.info("Deleted vectors for tenant %s", tenant_id)

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
