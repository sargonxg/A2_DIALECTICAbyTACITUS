"""Cloud SQL audit store for graph reasoning pipeline runs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph_reasoning.ingestion_adapter import AdaptedGraph
from app.graph_reasoning.pipeline import PipelinePlan
from app.graph_reasoning.schema import IngestResult
from dialectica_api.database.models import (
    GraphEdgeRecord,
    GraphObjectRecord,
    OntologyProfileRecord,
    PipelineRun,
    SourceChunkRecord,
)


class GraphReasoningSqlStore:
    """Persists pipeline metadata to SQLite locally or Cloud SQL in production."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_started(
        self,
        *,
        adapted: AdaptedGraph,
        pipeline: PipelinePlan,
        workspace_id: str,
        tenant_id: str,
        source_title: str,
        source_type: str,
        source_uri: str | None,
    ) -> str:
        run_id = adapted.episode_id
        await self.session.merge(
            PipelineRun(
                id=run_id,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                source_id=adapted.source_id,
                source_hash=adapted.source_hash,
                source_title=source_title,
                source_type=source_type,
                source_uri=source_uri,
                objective=pipeline.objective,
                ontology_profile=pipeline.ontology_profile,
                status="running",
                chunk_count=len(pipeline.chunks),
                cleaned_chars=len(pipeline.cleaned_text),
                original_chars=len(pipeline.original_text),
                pipeline=pipeline.summary(),
            )
        )
        await self.session.merge(
            OntologyProfileRecord(
                id=f"{run_id}:ontology",
                run_id=run_id,
                workspace_id=workspace_id,
                profile_id=pipeline.ontology_profile,
                objective=pipeline.objective,
                plan=pipeline.dynamic_ontology,
            )
        )
        for chunk in pipeline.chunks:
            await self.session.merge(
                SourceChunkRecord(
                    id=chunk.id,
                    run_id=run_id,
                    workspace_id=workspace_id,
                    source_id=adapted.source_id,
                    ordinal=chunk.ordinal,
                    label=chunk.label,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    char_count=len(chunk.text),
                    reason=chunk.reason,
                    text=chunk.text,
                )
            )
        await self.session.flush()
        return run_id

    async def record_completed(
        self,
        *,
        run_id: str,
        adapted: AdaptedGraph,
        result: IngestResult,
    ) -> None:
        run = await self.session.get(PipelineRun, run_id)
        if run is not None:
            run.status = result.status
            run.duplicate = result.duplicate
            run.object_count = result.object_count
            run.edge_count = result.edge_count
            run.errors = result.errors
            run.completed_at = datetime.utcnow()
            self.session.add(run)

        for obj in adapted.objects:
            payload = obj.model_dump(mode="json")
            await self.session.merge(
                GraphObjectRecord(
                    id=obj.id,
                    run_id=run_id,
                    workspace_id=obj.workspace_id,
                    tenant_id=obj.tenant_id,
                    kind=str(obj.kind),
                    source_ids=list(obj.source_ids),
                    confidence=obj.confidence,
                    payload=payload,
                )
            )
        for edge in adapted.edges:
            payload = edge.model_dump(mode="json")
            await self.session.merge(
                GraphEdgeRecord(
                    id=edge.id,
                    run_id=run_id,
                    workspace_id=edge.workspace_id,
                    tenant_id=edge.tenant_id,
                    kind=str(edge.kind),
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    source_ids=list(edge.source_ids),
                    confidence=edge.confidence,
                    payload=payload,
                )
            )
        await self.session.flush()

    async def record_failed(self, *, run_id: str, errors: list[str]) -> None:
        run = await self.session.get(PipelineRun, run_id)
        if run is None:
            return
        run.status = "failed"
        run.errors = errors
        run.completed_at = datetime.utcnow()
        self.session.add(run)
        await self.session.flush()

    async def list_runs(
        self, *, workspace_id: str | None = None, limit: int = 25
    ) -> list[dict[str, Any]]:
        stmt = select(PipelineRun).order_by(desc(PipelineRun.created_at)).limit(limit)
        if workspace_id:
            stmt = stmt.where(PipelineRun.workspace_id == workspace_id)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [_run_to_dict(row) for row in rows]

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        run = await self.session.get(PipelineRun, run_id)
        if run is None:
            return None
        chunks = (
            (
                await self.session.execute(
                    select(SourceChunkRecord)
                    .where(SourceChunkRecord.run_id == run_id)
                    .order_by(SourceChunkRecord.ordinal)
                )
            )
            .scalars()
            .all()
        )
        objects = (
            (
                await self.session.execute(
                    select(GraphObjectRecord).where(GraphObjectRecord.run_id == run_id)
                )
            )
            .scalars()
            .all()
        )
        edges = (
            (
                await self.session.execute(
                    select(GraphEdgeRecord).where(GraphEdgeRecord.run_id == run_id)
                )
            )
            .scalars()
            .all()
        )
        payload = _run_to_dict(run)
        payload["chunks"] = [_model_dict(chunk) for chunk in chunks]
        payload["objects"] = [_model_dict(obj) for obj in objects]
        payload["edges"] = [_model_dict(edge) for edge in edges]
        return payload


def _run_to_dict(run: PipelineRun) -> dict[str, Any]:
    return _model_dict(run)


def _model_dict(model: Any) -> dict[str, Any]:
    return model.model_dump(mode="json")
