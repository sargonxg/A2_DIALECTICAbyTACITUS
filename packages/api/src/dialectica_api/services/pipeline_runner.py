"""
Inline pipeline runner with live progress reporting.

Used when Pub/Sub is unavailable (local dev, CI, demo machines). Runs the
canonical extraction pipeline in a background task, emitting one
``JobProgressEvent`` per LangGraph step plus terminal events. Also persists
a ``SourceDocument`` summary onto the job and triggers the canned
auto-reasoning queries on completion.

Production path runs through ``dialectica_extraction.pubsub_worker`` instead;
that worker will be wired to publish equivalent events to a Redis pub/sub
channel keyed on ``job_id`` (see ``docs/ARCHITECTURE.md``).
"""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime
from typing import Any

from dialectica_api.services.job_store import JobProgressEvent, JobStore

logger = logging.getLogger(__name__)


PIPELINE_STEPS = (
    "chunk_document",
    "gliner_prefilter",
    "extract_entities",
    "validate_schema",
    "extract_relationships",
    "resolve_coreference",
    "validate_structural",
    "compute_embeddings",
    "write_to_graph",
)


def _emit(store: JobStore, event: JobProgressEvent) -> None:
    store.append_event(event)


async def run_pipeline_with_progress(  # noqa: PLR0913
    *,
    job_id: str,
    text: str,
    tier: str,
    workspace_id: str,
    tenant_id: str,
    source_title: str,
    source_kind: str,
    graph_client: Any,
    store: JobStore,
) -> dict[str, Any]:
    """Run the extraction pipeline inline and stream progress to ``store``.

    Returns the final job dict. Any unhandled exception is captured into
    the job's ``error`` field rather than propagating, so background-task
    callers don't drop tracebacks.
    """
    job = store.get_job(job_id) or {}
    job["status"] = "running"
    store.upsert_job(job)
    _emit(
        store,
        JobProgressEvent(
            job_id=job_id,
            step="job",
            status="started",
            message=f"Ingesting {source_title or 'input text'}",
        ),
    )

    try:
        from dialectica_extraction.pipeline import (
            ExtractionState,
            check_review_needed,
            chunk_document,
            compute_embeddings,
            extract_entities,
            extract_relationships,
            gliner_prefilter,
            repair_extraction,
            resolve_coreference,
            validate_schema,
            validate_structural_step,
        )
        from dialectica_ontology.tiers import OntologyTier

        state: ExtractionState = {
            "text": text,
            "tier": OntologyTier(tier).value,
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
            "chunks": [],
            "prefilter_results": [],
            "raw_entities": [],
            "validated_nodes": [],
            "validated_edges": [],
            "invalid_entities": [],
            "validation_errors": [],
            "embeddings": {},
            "errors": [],
            "retry_count": 0,
            "processing_time": {},
            "ingestion_stats": {},
            "requires_review": False,
            "review_reasons": [],
            "_nodes": [],
            "_edges": [],
        }

        steps: tuple[tuple[str, Any], ...] = (
            ("chunk_document", chunk_document),
            ("gliner_prefilter", gliner_prefilter),
            ("extract_entities", extract_entities),
            ("validate_schema", validate_schema),
        )
        for step_name, step_fn in steps:
            _emit(store, JobProgressEvent(job_id=job_id, step=step_name, status="started"))
            state = step_fn(state)
            _emit(
                store,
                JobProgressEvent(
                    job_id=job_id,
                    step=step_name,
                    status="complete",
                    counts=_counts_for(step_name, state),
                ),
            )

        # Repair loop (silent unless invalid entities exist)
        retries = 0
        while state.get("invalid_entities") and retries < 3:
            _emit(
                store,
                JobProgressEvent(
                    job_id=job_id,
                    step="repair_extraction",
                    status="started",
                    message=f"Repairing {len(state['invalid_entities'])} invalid entities",
                ),
            )
            state = repair_extraction(state)
            retries += 1

        tail_steps = (
            ("extract_relationships", extract_relationships),
            ("resolve_coreference", resolve_coreference),
            ("validate_structural", validate_structural_step),
            ("compute_embeddings", compute_embeddings),
            ("check_review_needed", check_review_needed),
        )
        for step_name, step_fn in tail_steps:
            _emit(store, JobProgressEvent(job_id=job_id, step=step_name, status="started"))
            state = step_fn(state)
            _emit(
                store,
                JobProgressEvent(
                    job_id=job_id,
                    step=step_name,
                    status="complete",
                    counts=_counts_for(step_name, state),
                ),
            )

        # Persist to graph
        nodes = state.get("_nodes", [])
        edges = state.get("_edges", [])
        nodes_written = len(nodes)
        edges_written = len(edges)

        _emit(store, JobProgressEvent(job_id=job_id, step="write_to_graph", status="started"))
        if graph_client is not None:
            try:
                node_ids = await graph_client.batch_upsert_nodes(nodes, workspace_id, tenant_id)
                nodes_written = len(node_ids)
            except Exception as exc:
                logger.error("batch_upsert_nodes failed: %s", exc)
                state.setdefault("errors", []).append(
                    {"step": "write_to_graph", "message": f"Node upsert failed: {exc}"}
                )
            try:
                edge_ids = await graph_client.batch_upsert_edges(edges, workspace_id, tenant_id)
                edges_written = len(edge_ids)
            except Exception as exc:
                logger.error("batch_upsert_edges failed: %s", exc)
                state.setdefault("errors", []).append(
                    {"step": "write_to_graph", "message": f"Edge upsert failed: {exc}"}
                )
        _emit(
            store,
            JobProgressEvent(
                job_id=job_id,
                step="write_to_graph",
                status="complete",
                counts={"nodes_written": nodes_written, "edges_written": edges_written},
            ),
        )

        # Update job + attach SourceDocument summary
        job = store.get_job(job_id) or job
        job["status"] = "complete"
        job["completed_at"] = datetime.utcnow().isoformat()
        job["nodes_extracted"] = nodes_written
        job["edges_extracted"] = edges_written
        job["source_document"] = _build_source_document_summary(
            text=text,
            title=source_title,
            tier=tier,
            nodes_written=nodes_written,
            edges_written=edges_written,
            errors=len(state.get("errors", [])),
        )
        store.upsert_job(job)

        # Auto-reasoning summary (cheap, deterministic, never blocks the demo)
        await _attach_auto_reasoning(
            job=job,
            workspace_id=workspace_id,
            graph_client=graph_client,
            store=store,
        )

        _emit(
            store,
            JobProgressEvent(
                job_id=job_id,
                step="job",
                status="complete",
                counts={
                    "nodes_extracted": nodes_written,
                    "edges_extracted": edges_written,
                    "duration_s": int(time.time() - _started_at(job)),
                },
            ),
        )
        return job

    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Inline pipeline failed for job %s: %s", job_id, exc)
        job = store.get_job(job_id) or job
        job["status"] = "failed"
        job["error"] = str(exc)[:500]
        job["completed_at"] = datetime.utcnow().isoformat()
        store.upsert_job(job)
        _emit(
            store,
            JobProgressEvent(
                job_id=job_id,
                step="job",
                status="failed",
                message=str(exc)[:200],
            ),
        )
        return job


def _counts_for(step: str, state: dict[str, Any]) -> dict[str, int]:
    """Step-specific human-friendly progress counters."""
    if step == "chunk_document":
        return {"chunks": len(state.get("chunks", []))}
    if step == "gliner_prefilter":
        return {"chunks_prefiltered": len(state.get("prefilter_results", []))}
    if step == "extract_entities":
        return {"entities_raw": len(state.get("raw_entities", []))}
    if step == "validate_schema":
        return {
            "entities_valid": len(state.get("validated_nodes", [])),
            "entities_invalid": len(state.get("invalid_entities", [])),
        }
    if step == "extract_relationships":
        return {"edges_valid": len(state.get("validated_edges", []))}
    if step == "resolve_coreference":
        return {"entities_after_merge": len(state.get("validated_nodes", []))}
    if step == "validate_structural":
        return {"errors": len(state.get("errors", []))}
    if step == "compute_embeddings":
        return {"embeddings": len(state.get("embeddings", {}))}
    return {}


def _build_source_document_summary(
    *,
    text: str,
    title: str,
    tier: str,
    nodes_written: int,
    edges_written: int,
    errors: int,
) -> dict[str, Any]:
    return {
        "id": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16],
        "title": title or "Untitled",
        "content_hash": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest(),
        "word_count": len(text.split()),
        "language": "en",
        "ingested_at": datetime.utcnow().isoformat(),
        "extraction_tier": tier,
        "extraction_model": "gemini-2.5-flash",
        "nodes_extracted": nodes_written,
        "edges_extracted": edges_written,
        "errors": errors,
    }


async def _attach_auto_reasoning(
    *,
    job: dict[str, Any],
    workspace_id: str,
    graph_client: Any,
    store: JobStore,
) -> None:
    """Run a small set of canned theory queries and attach to the job.

    Failures are non-fatal: the job stays "complete" even if reasoning is
    unavailable (e.g. the reasoning package isn't importable in this env).
    """
    if graph_client is None:
        return
    try:
        from dialectica_reasoning import ConflictQueryEngine
    except Exception:
        return

    summary: dict[str, Any] = {}
    try:
        engine = ConflictQueryEngine(graph_client=graph_client)
        # Glasl stage
        try:
            stats = await graph_client.get_workspace_stats(workspace_id)
            summary["graph_stats"] = {
                "total_nodes": stats.total_nodes,
                "total_edges": stats.total_edges,
            }
        except Exception:
            pass
        # Escalation
        try:
            esc = await graph_client.get_escalation_trajectory(workspace_id)
            summary["escalation"] = {
                "current_stage": getattr(esc, "current_stage", None),
                "direction": getattr(esc, "direction", None),
                "velocity": getattr(esc, "velocity", None),
            }
        except Exception:
            pass
        # Top actors (best-effort)
        try:
            nodes = await graph_client.get_nodes(workspace_id, label="Actor", limit=5)
            summary["top_actors"] = [getattr(n, "name", "") for n in nodes if hasattr(n, "name")]
        except Exception:
            pass
        # If the reasoning engine exposes a quick assessment, use it
        for method_name in ("quick_assessment", "summarize"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    result = method(workspace_id)  # type: ignore[misc]
                    if hasattr(result, "__await__"):
                        result = await result
                    summary["assessment"] = result
                except Exception:
                    pass
                break
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("auto-reasoning failed for job %s: %s", job.get("job_id"), exc)
        return

    job["auto_reasoning"] = summary
    store.upsert_job(job)


def _started_at(job: dict[str, Any]) -> float:
    created = job.get("created_at")
    if not created:
        return time.time()
    try:
        return datetime.fromisoformat(created).timestamp()
    except ValueError:
        return time.time()
