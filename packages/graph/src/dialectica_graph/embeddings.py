"""
Graph Embedding Service — Vertex AI + FastEmbed backends for DIALECTICA.

Default: Vertex AI text-embedding-005 with task_type RETRIEVAL_DOCUMENT (768-dim).
Fallback: FastEmbed BAAI/bge-small-en-v1.5 for offline/dev (384-dim, padded to 768).

Configure via EMBEDDING_BACKEND env var: "vertex" or "fastembed".
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "vertex")
VERTEX_MODEL = "text-embedding-005"
FASTEMBED_MODEL = "BAAI/bge-small-en-v1.5"
TARGET_DIM = 768


class GraphEmbeddingService:
    """Embedding service for the graph layer.

    Supports Vertex AI (production) and FastEmbed (dev/offline).
    """

    def __init__(self, backend: str | None = None) -> None:
        self._backend = backend or EMBEDDING_BACKEND
        self._vertex_model: Any = None
        self._fastembed_model: Any = None

    def embed_text(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts, returning list of float vectors."""
        if not texts:
            return []

        if self._backend == "vertex":
            return self._vertex_embed(texts)
        elif self._backend == "fastembed":
            return self._fastembed_embed(texts)
        else:
            logger.warning("Unknown backend %s, trying vertex", self._backend)
            return self._vertex_embed(texts)

    def _vertex_embed(self, texts: list[str]) -> list[list[float]]:
        """Embed via Vertex AI text-embedding-005."""
        try:
            if self._vertex_model is None:
                from vertexai.language_models import TextEmbeddingModel
                self._vertex_model = TextEmbeddingModel.from_pretrained(VERTEX_MODEL)

            embeddings = self._vertex_model.get_embeddings(
                texts,
                task_type="RETRIEVAL_DOCUMENT",
            )
            return [e.values for e in embeddings]
        except Exception as e:
            logger.warning("Vertex AI embed failed: %s — falling back to fastembed", e)
            return self._fastembed_embed(texts)

    def _fastembed_embed(self, texts: list[str]) -> list[list[float]]:
        """Embed via FastEmbed (offline/dev)."""
        try:
            if self._fastembed_model is None:
                from fastembed import TextEmbedding
                self._fastembed_model = TextEmbedding(model_name=FASTEMBED_MODEL)

            raw = list(self._fastembed_model.embed(texts))
            # Pad to TARGET_DIM if needed
            result: list[list[float]] = []
            for emb in raw:
                vec = list(emb) if not isinstance(emb, list) else emb
                if len(vec) < TARGET_DIM:
                    vec.extend([0.0] * (TARGET_DIM - len(vec)))
                result.append(vec[:TARGET_DIM])
            return result
        except Exception as e:
            logger.error("FastEmbed failed: %s", e)
            return [[0.0] * TARGET_DIM for _ in texts]
