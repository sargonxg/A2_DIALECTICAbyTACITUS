"""
Usage Metering Middleware — Track API usage for billing and analytics.

Captures: graph queries, LLM tokens, documents ingested, nodes created.
Writes to Redis Stream for buffering, aggregates every 5 minutes.
"""

from __future__ import annotations

import contextlib
import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("dialectica.metering")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
METERING_STREAM = "dialectica:metering"


class MeteringMiddleware(BaseHTTPMiddleware):
    """Async metering middleware — records usage metrics per request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        # Extract metering context
        tenant_id = getattr(request.state, "tenant_id", "unknown")
        api_key = request.headers.get("x-api-key", "")[:8]
        path = request.url.path
        method = request.method

        # Determine operation type
        op_type = _classify_operation(method, path)

        if op_type:
            metric = {
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": tenant_id,
                "api_key_prefix": api_key,
                "operation": op_type,
                "method": method,
                "path": path,
                "latency_ms": round(latency_ms, 1),
                "status": response.status_code,
            }

            # Non-blocking write to Redis Stream
            with contextlib.suppress(Exception):
                _write_metric(metric)

        return response


def _classify_operation(method: str, path: str) -> str | None:
    """Classify the API operation for metering."""
    if "/health" in path or "/metrics" in path:
        return None  # Don't meter health checks

    if "/extract" in path:
        return "extract"
    elif "/graph" in path or "/traverse" in path:
        return "graph_query"
    elif "/analyze" in path or "/reason" in path:
        return "reasoning"
    elif "/entities" in path or "/relationships" in path:
        if method in ("POST", "PUT", "PATCH"):
            return "graph_write"
        return "graph_read"
    elif "/workspaces" in path:
        return "workspace"
    return "other"


def _write_metric(metric: dict[str, Any]) -> None:
    """Write metric to Redis Stream (non-blocking)."""
    try:
        import redis

        r = redis.from_url(REDIS_URL, socket_timeout=1)
        r.xadd(METERING_STREAM, metric, maxlen=100000)
    except Exception:
        pass  # Silently fail — metering must never break the API
