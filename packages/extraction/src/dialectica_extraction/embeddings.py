"""
Embeddings — Vertex AI text-embedding-005 with local fallback.

Primary: Vertex AI text-embedding-005 (768 dimensions, multilingual)
Fallback: sentence-transformers/all-MiniLM-L6-v2 (128 dimensions, local)

Used for: Node embeddings in Spanner vector index, semantic search.
"""
from __future__ import annotations

import logging
from typing import Any

from dialectica_ontology.primitives import ConflictNode

logger = logging.getLogger(__name__)

VERTEX_MODEL = "text-embedding-005"
VERTEX_DIMENSIONS = 768
LOCAL_MODEL = "all-MiniLM-L6-v2"
LOCAL_DIMENSIONS = 128


class EmbeddingService:
    """Compute embeddings for text and ConflictNode instances.

    Tries Vertex AI first; falls back to local sentence-transformers.
    """

    def __init__(self, use_vertex: bool = True, project_id: str | None = None) -> None:
        self._use_vertex = use_vertex
        self._project_id = project_id
        self._vertex_model: Any = None
        self._local_model: Any = None

    def _init_vertex(self) -> bool:
        """Lazy-init Vertex AI embedding model."""
        if self._vertex_model is not None:
            return True
        try:
            from vertexai.language_models import TextEmbeddingModel
            import vertexai

            if self._project_id:
                vertexai.init(project=self._project_id)
            self._vertex_model = TextEmbeddingModel.from_pretrained(VERTEX_MODEL)
            logger.info("Initialized Vertex AI embedding model: %s", VERTEX_MODEL)
            return True
        except Exception as e:
            logger.warning("Vertex AI embedding init failed: %s", e)
            return False

    def _init_local(self) -> bool:
        """Lazy-init local sentence-transformers model."""
        if self._local_model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer

            self._local_model = SentenceTransformer(LOCAL_MODEL)
            logger.info("Initialized local embedding model: %s", LOCAL_MODEL)
            return True
        except Exception as e:
            logger.warning("Local embedding model init failed: %s", e)
            return False

    def embed_text(self, text: str) -> list[float]:
        """Compute embedding for a single text string."""
        if self._use_vertex and self._init_vertex():
            return self._vertex_embed([text])[0]

        if self._init_local():
            return self._local_embed([text])[0]

        logger.error("No embedding backend available")
        return []

    def embed_texts(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """Compute embeddings for a batch of texts."""
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            if self._use_vertex and self._init_vertex():
                all_embeddings.extend(self._vertex_embed(batch))
            elif self._init_local():
                all_embeddings.extend(self._local_embed(batch))
            else:
                all_embeddings.extend([] for _ in batch)

        return all_embeddings

    def _vertex_embed(self, texts: list[str]) -> list[list[float]]:
        """Embed using Vertex AI."""
        try:
            embeddings = self._vertex_model.get_embeddings(texts)
            return [e.values for e in embeddings]
        except Exception as e:
            logger.error("Vertex AI embedding failed: %s", e)
            # Fallback to local
            if self._init_local():
                return self._local_embed(texts)
            return [[] for _ in texts]

    def _local_embed(self, texts: list[str]) -> list[list[float]]:
        """Embed using local sentence-transformers."""
        try:
            embeddings = self._local_model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error("Local embedding failed: %s", e)
            return [[] for _ in texts]

    def embed_node(self, node: ConflictNode) -> list[float]:
        """Compute embedding for a ConflictNode.

        Embeds concatenation of label + key text properties.
        """
        text = _node_to_embedding_text(node)
        return self.embed_text(text)

    def embed_nodes(self, nodes: list[ConflictNode]) -> dict[str, list[float]]:
        """Batch compute embeddings for a list of nodes.

        Returns dict mapping node ID to embedding vector.
        """
        texts = [_node_to_embedding_text(n) for n in nodes]
        embeddings = self.embed_texts(texts)
        return {node.id: emb for node, emb in zip(nodes, embeddings) if emb}


def _node_to_embedding_text(node: ConflictNode) -> str:
    """Convert a ConflictNode to text for embedding.

    Concatenates label + key text fields.
    """
    parts = [node.label]

    # Add name/description fields
    for attr in ("name", "description", "content", "text", "summary"):
        val = getattr(node, attr, None)
        if val:
            parts.append(str(val))

    # Add source text
    if node.source_text:
        parts.append(node.source_text)

    return " | ".join(parts)
