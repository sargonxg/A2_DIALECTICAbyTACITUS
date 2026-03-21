"""
Observability Middleware — Request ID, latency logging, and tenant context.

Provides:
  - RequestIdMiddleware: adds X-Request-ID header
  - LatencyMiddleware: logs request latency
  - TenantContextMiddleware: extracts tenant_id for structured logging
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("dialectica.observability")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID header to all requests for tracing."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:12])
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LatencyMiddleware(BaseHTTPMiddleware):
    """Log request latency and method/path for all requests."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        request_id = getattr(request.state, "request_id", "-")
        tenant_id = getattr(request.state, "tenant_id", "-")

        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "latency_ms": round(latency_ms, 1),
                "request_id": request_id,
                "tenant_id": tenant_id,
            },
        )
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Extract tenant_id from auth state and attach to request for logging."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Tenant ID is set by AuthMiddleware; fall back to header
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            tenant_id = request.headers.get("x-tenant-id", "unknown")
            request.state.tenant_id = tenant_id

        workspace_id = request.path_params.get("workspace_id", "")
        if workspace_id:
            request.state.workspace_id = workspace_id

        return await call_next(request)
