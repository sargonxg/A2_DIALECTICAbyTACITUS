"""
Usage Middleware — Track API calls per tenant per endpoint.
"""

from __future__ import annotations

from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# In-memory usage counters: {tenant_id: {endpoint: count}}
_usage_counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))


class UsageMiddleware(BaseHTTPMiddleware):
    """Records API usage per tenant per endpoint for billing/analytics."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        tenant_id = getattr(request.state, "tenant_id", "unknown")
        endpoint = f"{request.method} {request.url.path}"
        _usage_counters[tenant_id][endpoint] += 1
        return response


def get_usage_stats(tenant_id: str) -> dict[str, int]:
    """Return API usage stats for a tenant."""
    return dict(_usage_counters.get(tenant_id, {}))


def get_all_usage_stats() -> dict[str, dict[str, int]]:
    """Return all usage stats (admin only)."""
    return {k: dict(v) for k, v in _usage_counters.items()}
