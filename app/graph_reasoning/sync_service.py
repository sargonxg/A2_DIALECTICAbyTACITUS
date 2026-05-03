"""Synchronization service for graph reasoning ingestion and queries."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.graph_reasoning.cozo_client import CozoReasoningClient
from app.graph_reasoning.graphiti_client import GraphitiTemporalClient
from app.graph_reasoning.ingestion_adapter import DialecticaIngestionAdapter
from app.graph_reasoning.neo4j_client import Neo4jGraphReasoningClient
from app.graph_reasoning.pipeline import build_pipeline_plan
from app.graph_reasoning.reasoning_queries import ReasoningQueries
from app.graph_reasoning.schema import GraphReasoningHealth, HealthCheck, IngestResult
from app.graph_reasoning.sql_store import GraphReasoningSqlStore

logger = logging.getLogger(__name__)


class GraphReasoningService:
    """Orchestrates Graphiti, Neo4j, and the Cozo reasoning mirror."""

    def __init__(
        self,
        neo4j: Neo4jGraphReasoningClient | None = None,
        graphiti: GraphitiTemporalClient | None = None,
        cozo: CozoReasoningClient | None = None,
        adapter: DialecticaIngestionAdapter | None = None,
    ) -> None:
        self.neo4j = neo4j or Neo4jGraphReasoningClient()
        self.graphiti = graphiti or GraphitiTemporalClient()
        self.cozo = cozo or CozoReasoningClient()
        self.adapter = adapter or DialecticaIngestionAdapter()
        self.reasoning = ReasoningQueries(self.cozo)
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.neo4j.initialize_schema()
        await self.graphiti.initialize()
        await self.cozo.initialize()
        self._initialized = True

    async def health(self) -> GraphReasoningHealth:
        checks = {
            "neo4j": _check("neo4j", await self.neo4j.health()),
            "graphiti": _check("graphiti", await self.graphiti.health()),
            "cozo": _check("cozo", await self.cozo.health()),
        }
        status = "healthy" if all(check.status == "up" for check in checks.values()) else "degraded"
        if checks["neo4j"].status == "down":
            status = "unhealthy"
        return GraphReasoningHealth(status=status, checks=checks)

    async def ingest_text(
        self,
        *,
        text: str,
        workspace_id: str,
        tenant_id: str,
        source_title: str,
        source_uri: str | None,
        source_type: str,
        objective: str = "Understand the conflict",
        ontology_profile: str = "human-friction",
        occurred_at: datetime | None = None,
        force: bool = False,
        db_session: AsyncSession | None = None,
    ) -> IngestResult:
        await self.initialize()
        pipeline = build_pipeline_plan(
            text=text,
            workspace_id=workspace_id,
            objective=objective,
            ontology_profile=ontology_profile,
            chunk_chars=int(os.getenv("GRAPH_REASONING_CHUNK_CHARS", "6000")),
        )
        adapted = self.adapter.adapt_text(
            text=pipeline.cleaned_text,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            source_title=source_title,
            source_uri=source_uri,
            source_type=source_type,
            occurred_at=occurred_at,
        )
        sql_store = GraphReasoningSqlStore(db_session) if db_session is not None else None
        if sql_store is not None:
            await sql_store.record_started(
                adapted=adapted,
                pipeline=pipeline,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_title=source_title,
                source_type=source_type,
                source_uri=source_uri,
            )
        errors: list[str] = []
        if not force:
            try:
                existing = await self.neo4j.find_source_by_hash(workspace_id, adapted.source_hash)
                if existing:
                    await self.refresh_mirror(workspace_id=workspace_id)
                    result = IngestResult(
                        status="duplicate",
                        duplicate=True,
                        source_id=str(existing.get("id", adapted.source_id)),
                        episode_id=adapted.episode_id,
                        pipeline=pipeline.summary(),
                    )
                    if sql_store is not None:
                        await sql_store.record_completed(
                            run_id=adapted.episode_id, adapted=adapted, result=result
                        )
                    return result
            except Exception as exc:
                logger.warning("Deduplication check failed: %s", exc)
                errors.append(f"deduplication_check_failed: {exc}")

        try:
            await self.graphiti.record_episode(
                episode_id=adapted.episode_id,
                source_hash=adapted.source_hash,
                text=pipeline.cleaned_text,
                source_id=adapted.source_id,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                objects=adapted.objects,
                edges=adapted.edges,
            )
        except Exception as exc:
            logger.warning("Graphiti episode write failed: %s", exc)
            errors.append(f"graphiti_write_failed: {exc}")

        object_ids = await self.neo4j.upsert_objects(adapted.objects)
        edge_ids: list[str] = []
        try:
            edge_ids = await self.neo4j.upsert_edges(adapted.edges)
        except Exception as exc:
            logger.warning("Neo4j edge write partial failure: %s", exc)
            errors.append(f"neo4j_edge_write_failed: {exc}")

        try:
            await self.graphiti.record_episode(
                episode_id=adapted.episode_id,
                source_hash=adapted.source_hash,
                text=pipeline.cleaned_text,
                source_id=adapted.source_id,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                objects=adapted.objects,
                edges=adapted.edges,
            )
        except Exception as exc:
            logger.warning("Graphiti provenance link refresh failed: %s", exc)
            errors.append(f"graphiti_link_failed: {exc}")

        try:
            await self.cozo.upsert_objects(adapted.objects)
            await self.cozo.upsert_edges(adapted.edges)
        except Exception as exc:
            logger.warning("Cozo mirror write failed: %s", exc)
            errors.append(f"cozo_write_failed: {exc}")

        result = IngestResult(
            status="ok" if not errors else "partial",
            duplicate=False,
            source_id=adapted.source_id,
            episode_id=adapted.episode_id,
            object_count=len(object_ids),
            edge_count=len(edge_ids),
            object_ids=object_ids,
            edge_ids=edge_ids,
            errors=errors,
            pipeline=pipeline.summary(),
        )
        if sql_store is not None:
            await sql_store.record_completed(
                run_id=adapted.episode_id,
                adapted=adapted,
                result=result,
            )
        return result

    async def refresh_mirror(self, workspace_id: str | None = None) -> None:
        payload = await self.neo4j.fetch_recent(workspace_id=workspace_id)
        await self.cozo.mirror_payload(payload)

    async def actor(self, actor_id: str, workspace_id: str | None = None) -> dict[str, Any] | None:
        return await self.neo4j.get_actor(actor_id, workspace_id=workspace_id)

    async def search(
        self, q: str, workspace_id: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        return await self.neo4j.search(q, workspace_id=workspace_id, limit=limit)

    async def reasoning_actor(
        self, actor_id: str, workspace_id: str | None = None
    ) -> dict[str, Any]:
        profile = self.reasoning.actor_profile(actor_id, workspace_id=workspace_id)
        if profile["actor"] is None:
            await self.refresh_mirror(workspace_id=workspace_id)
            profile = self.reasoning.actor_profile(actor_id, workspace_id=workspace_id)
        return profile

    async def changed_since(
        self, timestamp: datetime, workspace_id: str | None = None
    ) -> dict[str, Any]:
        changed = self.reasoning.changed_since(timestamp.isoformat(), workspace_id=workspace_id)
        if not changed["objects"] and not changed["edges"]:
            changed = await self.neo4j.changed_since(timestamp, workspace_id=workspace_id)
            await self.cozo.mirror_payload(changed)
        return changed

    async def close(self) -> None:
        await self.neo4j.close()
        await self.graphiti.close()


def _check(service: str, payload: dict[str, str]) -> HealthCheck:
    return HealthCheck(
        service=service,
        status=payload.get("status", "down"),
        mode=payload.get("mode", ""),
        details=payload.get("details", ""),
    )
