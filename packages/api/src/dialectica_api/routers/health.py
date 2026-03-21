"""
Health Router — Liveness, readiness, and deep health check endpoints.
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "2.0.0"
    graph_backend: str = ""


class ServiceCheck(BaseModel):
    service: str
    status: str  # "ok" | "error" | "unavailable"
    latency_ms: float = 0.0
    details: str = ""


class ReadinessResponse(BaseModel):
    status: str
    checks: list[ServiceCheck]


class DeepHealthResponse(BaseModel):
    status: str
    checks: list[ServiceCheck]
    environment: str
    uptime_seconds: float = 0.0


_start_time = time.time()


@router.get("/health", response_model=HealthResponse, include_in_schema=True)
async def health_check(
    settings: Any = Depends(get_settings),
) -> HealthResponse:
    """Basic liveness check — returns 200 if process is running."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
        graph_backend=settings.graph_backend,
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(
    settings: Any = Depends(get_settings),
    graph_client: Any = Depends(get_graph_client),
) -> ReadinessResponse:
    """Readiness check — verifies backing services are connected."""
    checks: list[ServiceCheck] = []

    # Graph database check
    checks.append(await _check_graph(graph_client, settings))

    # Redis check
    checks.append(await _check_redis())

    overall = "ok" if all(c.status == "ok" for c in checks) else "degraded"
    return ReadinessResponse(status=overall, checks=checks)


@router.get("/health/deep", response_model=DeepHealthResponse)
async def deep_health_check(
    settings: Any = Depends(get_settings),
    graph_client: Any = Depends(get_graph_client),
) -> DeepHealthResponse:
    """Deep health check — full system connectivity verification."""
    checks: list[ServiceCheck] = []

    checks.append(await _check_graph(graph_client, settings))
    checks.append(await _check_redis())
    checks.append(await _check_vertex_ai())
    checks.append(await _check_pubsub())
    checks.append(await _check_gcs())

    overall = "ok" if all(c.status == "ok" for c in checks) else "degraded"
    env = os.getenv("ENVIRONMENT", "development")
    uptime = time.time() - _start_time

    return DeepHealthResponse(
        status=overall,
        checks=checks,
        environment=env,
        uptime_seconds=round(uptime, 1),
    )


async def _check_graph(graph_client: Any, settings: Any) -> ServiceCheck:
    """Check graph database connectivity."""
    start = time.time()
    try:
        if graph_client is not None:
            await graph_client.get_nodes("__health__", limit=1)
            latency = (time.time() - start) * 1000
            return ServiceCheck(
                service=f"graph:{getattr(settings, 'graph_backend', 'unknown')}",
                status="ok",
                latency_ms=round(latency, 1),
                details="connected",
            )
        return ServiceCheck(service="graph", status="unavailable", details="no client configured")
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service="graph", status="error",
            latency_ms=round(latency, 1), details=str(e)[:100],
        )


async def _check_redis() -> ServiceCheck:
    """Check Redis connectivity."""
    start = time.time()
    try:
        import redis
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(url, socket_timeout=2)
        r.ping()
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="redis", status="ok", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="redis", status="error", latency_ms=round(latency, 1), details=str(e)[:100])


async def _check_vertex_ai() -> ServiceCheck:
    """Check Vertex AI connectivity."""
    start = time.time()
    try:
        import vertexai
        vertexai.init()
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="vertex_ai", status="ok", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="vertex_ai", status="error", latency_ms=round(latency, 1), details=str(e)[:100])


async def _check_pubsub() -> ServiceCheck:
    """Check Pub/Sub topic existence."""
    start = time.time()
    try:
        from google.cloud import pubsub_v1
        project = os.getenv("GCP_PROJECT_ID", "")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, "dialectica-extraction-requests")
        publisher.get_topic(request={"topic": topic_path})
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="pubsub", status="ok", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="pubsub", status="error", latency_ms=round(latency, 1), details=str(e)[:100])


async def _check_gcs() -> ServiceCheck:
    """Check GCS bucket access."""
    start = time.time()
    try:
        from google.cloud import storage
        bucket_name = os.getenv("GCS_DOCUMENTS_BUCKET", "dialectica-documents")
        client = storage.Client()
        client.get_bucket(bucket_name)
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="gcs", status="ok", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="gcs", status="error", latency_ms=round(latency, 1), details=str(e)[:100])
