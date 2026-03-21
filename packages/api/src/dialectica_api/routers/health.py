"""
Health Router — Liveness, readiness, and deep health check endpoints.

/health       — Full health with dependency checks (200 or 503)
/health/live  — Liveness probe for Cloud Run (always 200)
/health/ready — Readiness probe (200 when graph connected, 503 otherwise)
/health/deep  — Deep check including Vertex AI, Pub/Sub, GCS
"""
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

_start_time = time.time()


class ServiceCheck(BaseModel):
    service: str
    status: str  # "up" | "down" | "unavailable"
    latency_ms: float = 0.0
    details: str = ""


class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str = "2.0.0"
    environment: str = "development"
    graph_backend: str = ""
    timestamp: str = ""
    uptime_seconds: float = 0.0
    checks: dict[str, ServiceCheck] = {}
    node_types_registered: int = 15
    theory_frameworks: int = 15


class LiveResponse(BaseModel):
    status: str = "ok"


class ReadinessResponse(BaseModel):
    status: str
    checks: list[ServiceCheck]


class DeepHealthResponse(BaseModel):
    status: str
    checks: list[ServiceCheck]
    environment: str
    uptime_seconds: float = 0.0


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse, include_in_schema=True)
async def health_check(
    response: Response,
    settings: Any = Depends(get_settings),
    graph_client: Any = Depends(get_graph_client),
) -> HealthResponse:
    """Full health check with dependency status. Returns 503 if critical services down."""
    env = os.getenv("ENVIRONMENT", "development")
    uptime = time.time() - _start_time
    checks: dict[str, ServiceCheck] = {}

    # Check graph
    graph_check = await _check_graph(graph_client, settings)
    checks["neo4j" if settings.graph_backend == "neo4j" else settings.graph_backend] = graph_check

    # Check redis
    redis_check = await _check_redis()
    checks["redis"] = redis_check

    # Determine overall status
    all_checks = list(checks.values())
    if all(c.status == "up" for c in all_checks):
        status = "healthy"
    elif graph_check.status == "down":
        status = "unhealthy"
        response.status_code = 503
    else:
        status = "degraded"

    return HealthResponse(
        status=status,
        environment=env,
        graph_backend=settings.graph_backend,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(uptime, 1),
        checks=checks,
    )


@router.get("/health/live", response_model=LiveResponse)
async def liveness_check() -> LiveResponse:
    """Liveness probe — always returns 200 if process is running."""
    return LiveResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check(
    response: Response,
    settings: Any = Depends(get_settings),
    graph_client: Any = Depends(get_graph_client),
) -> ReadinessResponse:
    """Readiness check — 200 when Neo4j is connected, 503 otherwise."""
    checks: list[ServiceCheck] = []

    graph_check = await _check_graph(graph_client, settings)
    checks.append(graph_check)

    redis_check = await _check_redis()
    checks.append(redis_check)

    if graph_check.status == "up":
        overall = "ok" if all(c.status == "up" for c in checks) else "degraded"
    else:
        overall = "not_ready"
        response.status_code = 503

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

    overall = "ok" if all(c.status == "up" for c in checks) else "degraded"
    env = os.getenv("ENVIRONMENT", "development")
    uptime = time.time() - _start_time

    return DeepHealthResponse(
        status=overall,
        checks=checks,
        environment=env,
        uptime_seconds=round(uptime, 1),
    )


# ── Internal Checks ───────────────────────────────────────────────────────


async def _check_graph(graph_client: Any, settings: Any) -> ServiceCheck:
    """Check graph database connectivity."""
    service_name = f"graph:{getattr(settings, 'graph_backend', 'unknown')}"
    start = time.time()
    try:
        if graph_client is not None:
            await graph_client.get_nodes("__health__", limit=1)
            latency = (time.time() - start) * 1000
            return ServiceCheck(
                service=service_name, status="up",
                latency_ms=round(latency, 1), details="connected",
            )
        return ServiceCheck(service=service_name, status="unavailable", details="no client")
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service=service_name, status="down",
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
        return ServiceCheck(service="redis", status="up", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service="redis", status="down",
            latency_ms=round(latency, 1), details=str(e)[:100],
        )


async def _check_vertex_ai() -> ServiceCheck:
    start = time.time()
    try:
        import vertexai
        vertexai.init()
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="vertex_ai", status="up", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service="vertex_ai", status="down",
            latency_ms=round(latency, 1), details=str(e)[:100],
        )


async def _check_pubsub() -> ServiceCheck:
    start = time.time()
    try:
        from google.cloud import pubsub_v1
        project = os.getenv("GCP_PROJECT_ID", "")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, "dialectica-extraction-requests")
        publisher.get_topic(request={"topic": topic_path})
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="pubsub", status="up", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service="pubsub", status="down",
            latency_ms=round(latency, 1), details=str(e)[:100],
        )


async def _check_gcs() -> ServiceCheck:
    start = time.time()
    try:
        from google.cloud import storage
        bucket_name = os.getenv("GCS_DOCUMENTS_BUCKET", "dialectica-documents")
        client = storage.Client()
        client.get_bucket(bucket_name)
        latency = (time.time() - start) * 1000
        return ServiceCheck(service="gcs", status="up", latency_ms=round(latency, 1))
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ServiceCheck(
            service="gcs", status="down",
            latency_ms=round(latency, 1), details=str(e)[:100],
        )
