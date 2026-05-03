"""Neo4j source-of-truth client for graph reasoning objects."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from app.graph_reasoning.schema import GraphReasoningEdge, GraphReasoningObject, ObjectKind

_LABELS = {kind.value for kind in ObjectKind}


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if hasattr(value, "iso_format"):
        return value.iso_format()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


class Neo4jGraphReasoningClient:
    """Thin async Neo4j adapter using separate subsystem labels."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", os.getenv("NEO4J_USERNAME", "neo4j"))
        self.password = password or os.getenv("NEO4J_PASSWORD", "dialectica-dev")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
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

    async def initialize_schema(self) -> None:
        statements = [
            "CREATE CONSTRAINT graph_reasoning_id IF NOT EXISTS "
            "FOR (n:GraphReasoningObject) REQUIRE n.id IS UNIQUE",
            "CREATE INDEX graph_reasoning_workspace IF NOT EXISTS "
            "FOR (n:GraphReasoningObject) ON (n.workspace_id, n.tenant_id)",
            "CREATE INDEX graph_reasoning_source_hash IF NOT EXISTS "
            "FOR (n:Source) ON (n.source_hash)",
            "CREATE INDEX graph_reasoning_updated_at IF NOT EXISTS "
            "FOR (n:GraphReasoningObject) ON (n.updated_at)",
            "CREATE CONSTRAINT graph_reasoning_episode_id IF NOT EXISTS "
            "FOR (e:GraphReasoningEpisode) REQUIRE e.id IS UNIQUE",
        ]
        async with self._session() as session:
            for statement in statements:
                await session.run(statement)

    async def health(self) -> dict[str, str]:
        try:
            async with self._session() as session:
                result = await session.run("RETURN 1 AS ok")
                record = await result.single()
            return {
                "status": "up" if record and record["ok"] == 1 else "down",
                "details": "connected",
            }
        except Exception as exc:
            return {"status": "down", "details": str(exc)[:200]}

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def find_source_by_hash(
        self, workspace_id: str, source_hash: str
    ) -> dict[str, Any] | None:
        query = (
            "MATCH (s:GraphReasoningObject:Source {workspace_id: $workspace_id}) "
            "WHERE s.source_hash = $source_hash RETURN properties(s) AS props LIMIT 1"
        )
        async with self._session() as session:
            result = await session.run(
                query, {"workspace_id": workspace_id, "source_hash": source_hash}
            )
            record = await result.single()
        return dict(record["props"]) if record else None

    async def upsert_objects(self, objects: list[GraphReasoningObject]) -> list[str]:
        ids: list[str] = []
        async with self._session() as session:
            for obj in objects:
                label = str(obj.kind)
                if label not in _LABELS:
                    raise ValueError(f"Unsupported graph reasoning label: {label}")
                props = obj.to_neo4j_props()
                props.update(obj.properties)
                await session.run(
                    f"MERGE (n:GraphReasoningObject:{label} {{id: $id}}) "
                    "SET n += $props, n.updated_at = datetime($updated_at)",
                    {"id": obj.id, "props": props, "updated_at": obj.updated_at.isoformat()},
                )
                ids.append(obj.id)
        return ids

    async def upsert_edges(self, edges: list[GraphReasoningEdge]) -> list[str]:
        ids: list[str] = []
        async with self._session() as session:
            for edge in edges:
                rel_type = str(edge.kind)
                props = edge.to_neo4j_props()
                await session.run(
                    "MATCH (s:GraphReasoningObject {id: $source_id, workspace_id: $workspace_id}) "
                    "MATCH (t:GraphReasoningObject {id: $target_id, workspace_id: $workspace_id}) "
                    f"MERGE (s)-[r:{rel_type} {{id: $id}}]->(t) "
                    "SET r += $props, r.updated_at = datetime($updated_at)",
                    {
                        "id": edge.id,
                        "source_id": edge.source_id,
                        "target_id": edge.target_id,
                        "workspace_id": edge.workspace_id,
                        "props": props,
                        "updated_at": edge.updated_at.isoformat(),
                    },
                )
                ids.append(edge.id)
        return ids

    async def get_actor(
        self, actor_id: str, workspace_id: str | None = None
    ) -> dict[str, Any] | None:
        params: dict[str, Any] = {"actor_id": actor_id}
        query = "MATCH (a:GraphReasoningObject:Actor {id: $actor_id}) "
        if workspace_id:
            query += "WHERE a.workspace_id = $workspace_id "
            params["workspace_id"] = workspace_id
        query += (
            "OPTIONAL MATCH (a)-[r]->(out:GraphReasoningObject) "
            "RETURN properties(a) AS actor, "
            "collect({id: r.id, kind: type(r), target: properties(out)}) AS outgoing"
        )
        async with self._session() as session:
            result = await session.run(query, params)
            record = await result.single()
        if not record:
            return None
        return {
            "actor": _json_safe(dict(record["actor"])),
            "outgoing": _json_safe(record["outgoing"]),
        }

    async def search(
        self, q: str, workspace_id: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"q": q.lower(), "limit": limit}
        query = (
            "MATCH (n:GraphReasoningObject) "
            "WHERE toLower(coalesce(n.name, '') + ' ' + coalesce(n.text, '') + "
            "' ' + coalesce(n.description, '')) CONTAINS $q "
        )
        if workspace_id:
            query += "AND n.workspace_id = $workspace_id "
            params["workspace_id"] = workspace_id
        query += "RETURN properties(n) AS props ORDER BY n.updated_at DESC LIMIT $limit"
        async with self._session() as session:
            result = await session.run(query, params)
            records = await result.data()
        return [_json_safe(dict(record["props"])) for record in records]

    async def changed_since(
        self, timestamp: datetime, workspace_id: str | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        params: dict[str, Any] = {"timestamp": timestamp.isoformat()}
        node_query = "MATCH (n:GraphReasoningObject) WHERE n.updated_at >= datetime($timestamp) "
        edge_query = (
            "MATCH ()-[r]->() WHERE r.updated_at >= datetime($timestamp) AND r.id IS NOT NULL "
        )
        if workspace_id:
            node_query += "AND n.workspace_id = $workspace_id "
            edge_query += "AND r.workspace_id = $workspace_id "
            params["workspace_id"] = workspace_id
        node_query += "RETURN properties(n) AS props ORDER BY n.updated_at DESC LIMIT 500"
        edge_query += "RETURN properties(r) AS props ORDER BY r.updated_at DESC LIMIT 500"
        async with self._session() as session:
            node_result = await session.run(node_query, params)
            edge_result = await session.run(edge_query, params)
            nodes = [_json_safe(dict(record["props"])) for record in await node_result.data()]
            edges = [_json_safe(dict(record["props"])) for record in await edge_result.data()]
        return {"objects": nodes, "edges": edges}

    async def fetch_recent(
        self, workspace_id: str | None = None, limit: int = 500
    ) -> dict[str, list[dict[str, Any]]]:
        params: dict[str, Any] = {"limit": limit}
        node_query = "MATCH (n:GraphReasoningObject) "
        edge_query = (
            "MATCH (s:GraphReasoningObject)-[r]->(t:GraphReasoningObject) WHERE r.id IS NOT NULL "
        )
        if workspace_id:
            node_query += "WHERE n.workspace_id = $workspace_id "
            edge_query += "AND r.workspace_id = $workspace_id "
            params["workspace_id"] = workspace_id
        node_query += "RETURN properties(n) AS props ORDER BY n.updated_at DESC LIMIT $limit"
        edge_query += "RETURN properties(r) AS props ORDER BY r.updated_at DESC LIMIT $limit"
        async with self._session() as session:
            node_result = await session.run(node_query, params)
            edge_result = await session.run(edge_query, params)
            nodes = [_json_safe(dict(record["props"])) for record in await node_result.data()]
            edges = [_json_safe(dict(record["props"])) for record in await edge_result.data()]
        return {"objects": nodes, "edges": edges}
