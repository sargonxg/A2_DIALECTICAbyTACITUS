"""
Logging Middleware — Structured JSON logging for GCP Cloud Logging.
"""

from __future__ import annotations

import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("dialectica.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request as structured JSON compatible with GCP Cloud Logging."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        response = await call_next(request)

        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        tenant_id = getattr(request.state, "tenant_id", "unknown")

        log_entry = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
            "tenant_id": tenant_id,
            "user_agent": request.headers.get("user-agent", ""),
        }
        logger.info(json.dumps(log_entry))

        response.headers["X-Request-ID"] = request_id
        return response
