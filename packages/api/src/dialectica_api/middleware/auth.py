"""
Auth Middleware — API key authentication for DIALECTICA API.

Validates X-API-Key header. Admin key = full access.
Tenant keys = workspace-scoped access.
"""
from __future__ import annotations

import hashlib
import os

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


# Public paths that don't require authentication
_PUBLIC_PATHS = {"/health", "/health/", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates X-API-Key on every request and sets request.state attributes."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip auth for public paths
        path = request.url.path
        if any(path.startswith(p) for p in _PUBLIC_PATHS):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "")
        if not api_key:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                {"detail": "Authentication required — provide X-API-Key header."},
                status_code=401,
            )

        # Validate against admin key
        admin_key = os.getenv("ADMIN_API_KEY", "dev-admin-key-change-in-production")
        if api_key == admin_key:
            request.state.tenant_id = "admin"
            request.state.is_admin = True
            return await call_next(request)

        # Validate against tenant keys (simple in-memory for dev; Spanner in prod)
        tenant_id = await _validate_tenant_key(api_key)
        if tenant_id:
            request.state.tenant_id = tenant_id
            request.state.is_admin = False
            return await call_next(request)

        from fastapi.responses import JSONResponse
        return JSONResponse(
            {"detail": "Invalid API key."},
            status_code=401,
        )


async def _validate_tenant_key(api_key: str) -> str | None:
    """Validate a tenant API key. Returns tenant_id or None."""
    # In production, look up key in Spanner or Redis cache.
    # For dev/testing: accept any key prefixed with "tenant-"
    if api_key.startswith("tenant-"):
        # Extract tenant_id from key prefix convention: tenant-{tenant_id}-{secret}
        parts = api_key.split("-", 2)
        if len(parts) >= 2:
            return parts[1]
    return None
