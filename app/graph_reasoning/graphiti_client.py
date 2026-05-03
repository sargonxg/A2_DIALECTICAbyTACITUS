"""Graphiti temporal/provenance adapter."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

from app.graph_reasoning.schema import GraphReasoningEdge, GraphReasoningObject

logger = logging.getLogger(__name__)


class GraphitiTemporalClient:
    """Temporal layer on Neo4j with optional native Graphiti integration."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
        use_native: bool | None = None,
    ) -> None:
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME", "neo4j"))
        self.password = password or os.getenv("NEO4J_PASSWORD", "dialectica-dev")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        self.use_native = (
            os.getenv("GRAPHITI_USE_NATIVE", "false").lower() == "true"
            if use_native is None
            else use_native
        )
        self.mode = "neo4j_compat"
        self._native: Any | None = None
        self._driver: Any | None = None

    def _get_driver(self) -> Any:
        if self._driver is None:
            from neo4j import AsyncGraphDatabase

            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                connection_timeout=float(os.getenv("NEO4J_CONNECTION_TIMEOUT", "5")),
            )
        return self._driver

    def _session(self) -> Any:
        return self._get_driver().session(database=self.database)

    async def initialize(self) -> None:
        if self.use_native:
            try:
                from graphiti_core import Graphiti  # type: ignore

                self._native = Graphiti(self.uri, self.username, self.password)
                build = getattr(self._native, "build_indices_and_constraints", None)
                if build is not None:
                    result = build()
                    if hasattr(result, "__await__"):
                        await result
                self.mode = "native"
            except Exception as exc:
                logger.warning("Graphiti native mode unavailable, using Neo4j compat: %s", exc)
                self.mode = "neo4j_compat"
        async with self._session() as session:
            await session.run(
                "CREATE CONSTRAINT graph_reasoning_episode IF NOT EXISTS "
                "FOR (e:GraphReasoningEpisode) REQUIRE e.id IS UNIQUE"
            )
            await session.run(
                "CREATE INDEX graph_reasoning_episode_hash IF NOT EXISTS "
                "FOR (e:GraphReasoningEpisode) ON (e.source_hash)"
            )

    async def health(self) -> dict[str, str]:
        try:
            async with self._session() as session:
                result = await session.run("RETURN 1 AS ok")
                record = await result.single()
            status = "up" if record and record["ok"] == 1 else "down"
            return {"status": status, "mode": self.mode, "details": "connected"}
        except Exception as exc:
            return {"status": "down", "mode": self.mode, "details": str(exc)[:200]}

    async def record_episode(
        self,
        *,
        episode_id: str,
        source_hash: str,
        text: str,
        source_id: str,
        workspace_id: str,
        tenant_id: str,
        objects: list[GraphReasoningObject],
        edges: list[GraphReasoningEdge],
    ) -> str:
        now = datetime.utcnow().isoformat()
        if self.mode == "native" and self._native is not None:
            try:
                add_episode = getattr(self._native, "add_episode", None)
                if add_episode is not None:
                    result = add_episode(
                        name=episode_id,
                        episode_body=text,
                        source_description=source_id,
                        reference_time=datetime.utcnow(),
                    )
                    if hasattr(result, "__await__"):
                        await result
            except Exception as exc:
                logger.warning(
                    "Graphiti native episode write failed, preserving compat node: %s", exc
                )
        async with self._session() as session:
            await session.run(
                "MERGE (e:GraphReasoningEpisode {id: $id}) "
                "SET e += $props, e.updated_at = datetime($updated_at)",
                {
                    "id": episode_id,
                    "updated_at": now,
                    "props": {
                        "id": episode_id,
                        "workspace_id": workspace_id,
                        "tenant_id": tenant_id,
                        "source_hash": source_hash,
                        "source_id": source_id,
                        "created_at": now,
                        "updated_at": now,
                        "object_ids": [obj.id for obj in objects],
                        "edge_ids": [edge.id for edge in edges],
                    },
                },
            )
            await session.run(
                "MATCH (e:GraphReasoningEpisode {id: $episode_id}) "
                "MATCH (s:GraphReasoningObject {id: $source_id}) "
                "MERGE (e)-[:GRAPHITI_SOURCE]->(s)",
                {"episode_id": episode_id, "source_id": source_id},
            )
        return episode_id

    async def close(self) -> None:
        close = getattr(self._native, "close", None)
        if close is not None:
            result = close()
            if hasattr(result, "__await__"):
                await result
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
