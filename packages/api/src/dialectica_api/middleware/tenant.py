"""
Tenant Middleware — Extract and validate tenant context.
"""
from __future__ import annotations

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class TenantMiddleware(BaseHTTPMiddleware):
    """Ensures tenant_id is set on every request state."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not hasattr(request.state, "tenant_id") or not request.state.tenant_id:
            request.state.tenant_id = "public"
            request.state.is_admin = False
        return await call_next(request)
