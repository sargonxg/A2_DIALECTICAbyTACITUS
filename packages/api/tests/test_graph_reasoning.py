"""Tests for the optional graph reasoning subsystem."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.graph_reasoning.cozo_client import CozoReasoningClient
from app.graph_reasoning.ingestion_adapter import DialecticaIngestionAdapter
from app.graph_reasoning.reasoning_queries import ReasoningQueries
from app.graph_reasoning.schema import GraphReasoningObject, ObjectKind
from app.graph_reasoning.sync_service import GraphReasoningService

pytestmark = pytest.mark.asyncio


class FakeNeo4j:
    def __init__(self, fail_writes: bool = False) -> None:
        self.fail_writes = fail_writes
        self.objects: dict[str, Any] = {}
        self.edges: dict[str, Any] = {}
        self.sources_by_hash: dict[str, dict[str, Any]] = {}
        self.initialized = False

    async def initialize_schema(self) -> None:
        self.initialized = True

    async def health(self) -> dict[str, str]:
        return {"status": "down" if self.fail_writes else "up", "details": "fake"}

    async def find_source_by_hash(
        self, workspace_id: str, source_hash: str
    ) -> dict[str, Any] | None:
        return self.sources_by_hash.get(f"{workspace_id}:{source_hash}")

    async def upsert_objects(self, objects: list[Any]) -> list[str]:
        if self.fail_writes:
            raise RuntimeError("neo4j unavailable")
        for obj in objects:
            self.objects[obj.id] = obj.model_dump(mode="json")
            if obj.kind == "Source":
                self.sources_by_hash[f"{obj.workspace_id}:{obj.properties['source_hash']}"] = (
                    self.objects[obj.id]
                )
        return [obj.id for obj in objects]

    async def upsert_edges(self, edges: list[Any]) -> list[str]:
        if self.fail_writes:
            raise RuntimeError("neo4j unavailable")
        for edge in edges:
            self.edges[edge.id] = edge.model_dump(mode="json")
        return [edge.id for edge in edges]

    async def fetch_recent(
        self, workspace_id: str | None = None, limit: int = 500
    ) -> dict[str, list[dict[str, Any]]]:
        objects = list(self.objects.values())
        edges = list(self.edges.values())
        if workspace_id:
            objects = [obj for obj in objects if obj["workspace_id"] == workspace_id]
            edges = [edge for edge in edges if edge["workspace_id"] == workspace_id]
        return {"objects": objects[:limit], "edges": edges[:limit]}

    async def get_actor(
        self, actor_id: str, workspace_id: str | None = None
    ) -> dict[str, Any] | None:
        actor = self.objects.get(actor_id)
        if actor is None:
            return None
        return {"actor": actor, "outgoing": []}

    async def search(
        self, q: str, workspace_id: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        q_lower = q.lower()
        return [
            obj
            for obj in self.objects.values()
            if q_lower
            in str(obj.get("name") or obj.get("text") or obj.get("description") or "").lower()
        ][:limit]

    async def changed_since(
        self, timestamp: datetime, workspace_id: str | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        return await self.fetch_recent(workspace_id=workspace_id)

    async def close(self) -> None:
        return None


class FakeGraphiti:
    def __init__(self) -> None:
        self.episodes: list[str] = []

    async def initialize(self) -> None:
        return None

    async def health(self) -> dict[str, str]:
        return {"status": "up", "mode": "fake", "details": "fake"}

    async def record_episode(self, **kwargs: Any) -> str:
        self.episodes.append(kwargs["episode_id"])
        return str(kwargs["episode_id"])

    async def close(self) -> None:
        return None


async def test_ontology_requires_provenance() -> None:
    with pytest.raises(ValidationError):
        GraphReasoningObject(
            id="actor_missing_sources",
            kind=ObjectKind.ACTOR,
            workspace_id="ws",
            tenant_id="t",
            name="Alice",
            source_ids=[],
        )


async def test_ingestion_writes_graphiti_neo4j_and_cozo() -> None:
    service = GraphReasoningService(
        neo4j=FakeNeo4j(), graphiti=FakeGraphiti(), cozo=CozoReasoningClient()
    )
    result = await service.ingest_text(
        text="Alice will meet Bob. Bob must accept a deadline.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    assert result.status == "ok"
    assert result.object_count > 0
    assert result.edge_count > 0
    assert service.graphiti.episodes
    assert service.cozo.relation_counts()["actor"] >= 2


async def test_ingestion_deduplicates_by_source_hash() -> None:
    service = GraphReasoningService(
        neo4j=FakeNeo4j(), graphiti=FakeGraphiti(), cozo=CozoReasoningClient()
    )
    first = await service.ingest_text(
        text="Alice committed to a deadline.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    second = await service.ingest_text(
        text="Alice committed to a deadline.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    assert first.duplicate is False
    assert second.duplicate is True
    assert second.source_id == first.source_id


async def test_reasoning_queries_return_actor_profile_and_constraints() -> None:
    adapter = DialecticaIngestionAdapter()
    graph = adapter.adapt_text(
        text="Alice wants access. Alice must satisfy the deadline.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    cozo = CozoReasoningClient()
    await cozo.upsert_objects(graph.objects)
    await cozo.upsert_edges(graph.edges)
    actor_id = next(
        obj.id for obj in graph.objects if obj.kind == ObjectKind.ACTOR and obj.name == "Alice"
    )
    queries = ReasoningQueries(cozo)
    profile = queries.actor_profile(actor_id, workspace_id="ws")
    constraints = queries.indirect_constraints(actor_id, workspace_id="ws")
    assert profile["actor"]["name"] == "Alice"
    assert profile["interests"]
    assert constraints["direct"]


async def test_cozo_embedded_relation_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("cozo_embedded")
    monkeypatch.setenv("COZO_USE_EMBEDDED", "true")
    monkeypatch.setenv("COZO_ENGINE", "mem")
    monkeypatch.setenv("COZO_PATH", "")
    cozo = CozoReasoningClient()
    await cozo.initialize()

    graph = DialecticaIngestionAdapter().adapt_text(
        text="Alice must meet Bob. Bob has leverage.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    await cozo.upsert_objects(graph.objects)
    await cozo.upsert_edges(graph.edges)

    assert cozo.mode == "embedded"
    assert cozo.relation_counts()["actor"] >= 2
    assert cozo.native_relation("actor")
    assert cozo.native_relation("edge")


async def test_graph_reasoning_api_endpoints(admin_headers: dict[str, str]) -> None:
    from dialectica_api.database.deps import get_db
    from dialectica_api.main import create_app
    from dialectica_api.routers.graph_reasoning import get_graph_reasoning_service

    service = GraphReasoningService(
        neo4j=FakeNeo4j(), graphiti=FakeGraphiti(), cozo=CozoReasoningClient()
    )
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_db():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app = create_app()
    test_app.dependency_overrides[get_graph_reasoning_service] = lambda: service
    test_app.dependency_overrides[get_db] = override_db
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://testserver"
    ) as client:
        ingest = await client.post(
            "/ingest/text",
            json={
                "text": "Alice will meet Bob. Bob has leverage.",
                "workspace_id": "ws",
                "source_title": "api fixture",
            },
            headers=admin_headers,
        )
        assert ingest.status_code == 200
        actor_id = next(
            obj_id for obj_id, obj in service.neo4j.objects.items() if obj["kind"] == "Actor"
        )
        profile = await client.get(
            f"/reasoning/actor/{actor_id}", params={"workspace_id": "ws"}, headers=admin_headers
        )
        assert profile.status_code == 200
        search = await client.get(
            "/graph/search", params={"q": "Alice", "workspace_id": "ws"}, headers=admin_headers
        )
        assert search.status_code == 200
        assert search.json()["results"]
        runs = await client.get(
            "/pipeline/runs", params={"workspace_id": "ws"}, headers=admin_headers
        )
        assert runs.status_code == 200
        assert runs.json()["runs"]
    await engine.dispose()


async def test_failure_mode_db_unavailable() -> None:
    service = GraphReasoningService(
        neo4j=FakeNeo4j(fail_writes=True), graphiti=FakeGraphiti(), cozo=CozoReasoningClient()
    )
    health = await service.health()
    assert health.status == "unhealthy"
    with pytest.raises(RuntimeError, match="neo4j unavailable"):
        await service.ingest_text(
            text="Alice will meet Bob.",
            workspace_id="ws",
            tenant_id="tenant",
            source_title="fixture",
            source_uri=None,
            source_type="text",
        )


async def test_changed_since_uses_cozo_mirror() -> None:
    service = GraphReasoningService(
        neo4j=FakeNeo4j(), graphiti=FakeGraphiti(), cozo=CozoReasoningClient()
    )
    await service.ingest_text(
        text="Alice announced a commitment.",
        workspace_id="ws",
        tenant_id="tenant",
        source_title="fixture",
        source_uri=None,
        source_type="text",
    )
    changed = await service.changed_since(
        datetime.now(UTC) - timedelta(minutes=1), workspace_id="ws"
    )
    assert changed["objects"]
    assert changed["edges"]
