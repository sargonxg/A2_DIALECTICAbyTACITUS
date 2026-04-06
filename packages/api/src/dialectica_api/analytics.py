"""
BigQuery Analytics Client for DIALECTICA API.

Logs extraction events, query events, and benchmark results to BigQuery
for operational analytics and model quality tracking.

BigQuery is an optional dependency — the client degrades gracefully
when google-cloud-bigquery is not installed or credentials are missing.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy import of google.cloud.bigquery
# ---------------------------------------------------------------------------

_bigquery_mod: Any = None
_bigquery_import_attempted: bool = False


def _get_bigquery() -> Any:
    """Lazy-load google.cloud.bigquery; returns the module or None."""
    global _bigquery_mod, _bigquery_import_attempted  # noqa: PLW0603
    if not _bigquery_import_attempted:
        _bigquery_import_attempted = True
        try:
            import google.cloud.bigquery as bq  # type: ignore[import-untyped]

            _bigquery_mod = bq
        except ImportError:
            logger.warning("google-cloud-bigquery not installed — analytics events will be dropped")
    return _bigquery_mod


# ---------------------------------------------------------------------------
# AnalyticsClient
# ---------------------------------------------------------------------------


class AnalyticsClient:
    """Write analytics rows to BigQuery.

    All public methods are async-safe (they offload the synchronous BQ
    client call to a thread-pool executor so they never block the event loop).
    If BigQuery is unavailable the methods log a warning and return silently.
    """

    def __init__(
        self,
        project_id: str | None = None,
        dataset_id: str = "dialectica_analytics",
    ) -> None:
        self._project_id = project_id or os.environ.get("GCP_PROJECT_ID", "")
        self._dataset_id = dataset_id
        self._client: Any = None
        self._init_attempted: bool = False

    # -- internal helpers ----------------------------------------------------

    def _ensure_client(self) -> Any:
        """Return a bigquery.Client or None (idempotent)."""
        if self._init_attempted:
            return self._client
        self._init_attempted = True
        bq = _get_bigquery()
        if bq is None:
            return None
        try:
            self._client = bq.Client(project=self._project_id or None)
        except Exception:
            logger.warning("Failed to create BigQuery client", exc_info=True)
        return self._client

    def _table_ref(self, table_name: str) -> str:
        return f"{self._project_id}.{self._dataset_id}.{table_name}"

    def _insert_rows_sync(self, table_name: str, rows: list[dict[str, Any]]) -> None:
        """Synchronous row insert — called from a thread."""
        client = self._ensure_client()
        if client is None:
            logger.debug(
                "BigQuery client unavailable — dropping %d rows for %s",
                len(rows),
                table_name,
            )
            return
        errors = client.insert_rows_json(self._table_ref(table_name), rows)
        if errors:
            logger.error("BigQuery insert errors for %s: %s", table_name, errors)

    async def _insert_rows(self, table_name: str, rows: list[dict[str, Any]]) -> None:
        """Offload synchronous BQ insert to a thread so we stay async-safe."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._insert_rows_sync, table_name, rows)

    # -- public API ----------------------------------------------------------

    async def log_extraction(
        self,
        *,
        workspace_id: str,
        tenant_id: str,
        nodes_extracted: int,
        edges_extracted: int,
        processing_time_ms: float,
        tier: str,
        errors: int = 0,
        timestamp: datetime | None = None,
    ) -> None:
        """Log a single extraction event."""
        ts = timestamp or datetime.now(UTC)
        row = {
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
            "nodes_extracted": nodes_extracted,
            "edges_extracted": edges_extracted,
            "processing_time_ms": processing_time_ms,
            "tier": tier,
            "errors": errors,
            "timestamp": ts.isoformat(),
        }
        await self._insert_rows("extraction_events", [row])

    async def log_query(
        self,
        *,
        workspace_id: str,
        query_text: str,
        mode: str,
        response_time_ms: float,
        nodes_retrieved: int,
        confidence: float | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """Log a single query event."""
        ts = timestamp or datetime.now(UTC)
        row = {
            "workspace_id": workspace_id,
            "query_text": query_text,
            "mode": mode,
            "response_time_ms": response_time_ms,
            "nodes_retrieved": nodes_retrieved,
            "confidence": confidence,
            "timestamp": ts.isoformat(),
        }
        await self._insert_rows("query_events", [row])

    async def log_benchmark(
        self,
        *,
        benchmark_id: str,
        corpus_id: str,
        tier: str,
        model: str,
        f1: float,
        precision: float,
        recall: float,
        extraction_time_ms: float,
        hallucination_rate: float,
        timestamp: datetime | None = None,
    ) -> None:
        """Log a single benchmark result."""
        ts = timestamp or datetime.now(UTC)
        row = {
            "benchmark_id": benchmark_id,
            "corpus_id": corpus_id,
            "tier": tier,
            "model": model,
            "f1": f1,
            "precision": precision,
            "recall": recall,
            "extraction_time_ms": extraction_time_ms,
            "hallucination_rate": hallucination_rate,
            "timestamp": ts.isoformat(),
        }
        await self._insert_rows("benchmark_results", [row])
