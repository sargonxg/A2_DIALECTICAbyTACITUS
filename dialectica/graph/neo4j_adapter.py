"""Neo4j adapter for TACITUS core v1 graph primitives."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from neo4j import GraphDatabase

from dialectica.ontology.models import GraphPrimitive

CORE_LABEL = "TacitusCoreV1"


def _env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name, fallback)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _props(primitive: GraphPrimitive) -> dict[str, Any]:
    data = primitive.model_dump(mode="python")
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, (dict, list)):
            data[key] = json.dumps(value)
        elif value is None:
            data.pop(key)
    data["primitive_type"] = primitive.__class__.__name__
    return data


class Neo4jAdapter:
    """Scoped Neo4j writer/query adapter."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self.uri = uri or _env("NEO4J_URI")
        self.username = (
            username or os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER") or "neo4j"
        )
        self.password = password or _env("NEO4J_PASSWORD")
        self.database = database or os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    def initialize_schema(self) -> None:
        statements = [
            f"CREATE CONSTRAINT tacitus_core_v1_id IF NOT EXISTS FOR (n:{CORE_LABEL}) "
            "REQUIRE n.id IS UNIQUE",
            f"CREATE INDEX tacitus_core_v1_workspace_case IF NOT EXISTS FOR (n:{CORE_LABEL}) "
            "ON (n.workspace_id, n.case_id)",
            f"CREATE INDEX tacitus_core_v1_episode IF NOT EXISTS FOR (n:{CORE_LABEL}) "
            "ON (n.episode_id)",
            f"CREATE INDEX tacitus_core_v1_source IF NOT EXISTS FOR (n:{CORE_LABEL}) "
            "ON (n.source_id)",
            f"CREATE INDEX tacitus_core_v1_extraction_run IF NOT EXISTS FOR (n:{CORE_LABEL}) "
            "ON (n.extraction_run_id)",
        ]
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                session.run(statement)

    def write_primitive(self, primitive: GraphPrimitive) -> str:
        data = _props(primitive)
        if not data.get("workspace_id") or not data.get("case_id"):
            raise ValueError("All graph writes require workspace_id and case_id")
        if "episode_id" in data and not data["episode_id"]:
            raise ValueError("Episode-scoped graph writes require episode_id")

        label = primitive.__class__.__name__
        cypher = (
            f"MERGE (n:{CORE_LABEL}:{label} {{id: $id}}) "
            "SET n += $props, n.updated_at = datetime() "
            "RETURN n.id AS id"
        )
        with self.driver.session(database=self.database) as session:
            record = session.run(cypher, id=primitive.id, props=data).single()
        return str(record["id"] if record else primitive.id)

    def write_primitives(self, primitives: list[GraphPrimitive]) -> list[str]:
        return [self.write_primitive(primitive) for primitive in primitives]

    def query(self, question: str, workspace_id: str, case_id: str) -> list[dict]:
        lowered = question.lower()
        if "commitment" in lowered and "constrain" in lowered:
            cypher = (
                f"MATCH (n:{CORE_LABEL}) "
                "WHERE n.workspace_id = $workspace_id AND n.case_id = $case_id "
                "AND n.primitive_type IN ['Commitment', 'Constraint'] "
                "RETURN properties(n) AS item ORDER BY n.observed_at DESC LIMIT 50"
            )
        elif "episode" in lowered or "changed" in lowered:
            cypher = (
                f"MATCH (n:{CORE_LABEL}) "
                "WHERE n.workspace_id = $workspace_id AND n.case_id = $case_id "
                "AND n.primitive_type IN ['Episode', 'ActorState', 'Event'] "
                "RETURN properties(n) AS item ORDER BY n.observed_at DESC LIMIT 50"
            )
        else:
            cypher = (
                f"MATCH (n:{CORE_LABEL}) "
                "WHERE n.workspace_id = $workspace_id AND n.case_id = $case_id "
                "RETURN properties(n) AS item LIMIT 50"
            )
        with self.driver.session(database=self.database) as session:
            return [
                dict(record["item"])
                for record in session.run(cypher, workspace_id=workspace_id, case_id=case_id)
            ]

    def episodes(self, workspace_id: str, case_id: str) -> list[dict]:
        cypher = (
            f"MATCH (n:{CORE_LABEL}:Episode) "
            "WHERE n.workspace_id = $workspace_id AND n.case_id = $case_id "
            "RETURN properties(n) AS item ORDER BY n.valid_from, n.name"
        )
        with self.driver.session(database=self.database) as session:
            return [
                dict(record["item"])
                for record in session.run(cypher, workspace_id=workspace_id, case_id=case_id)
            ]

    def close(self) -> None:
        self.driver.close()
