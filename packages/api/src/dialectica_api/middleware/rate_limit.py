"""
Rate Limit Middleware — Token bucket per API key.

Default: 100 req/min, 1000 req/hour. In-memory (Redis in prod).
"""
from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


# In-memory rate limit state: {api_key: [(timestamp, count)]}
_buckets: dict[str, list[float]] = defaultdict(list)

_WINDOW_SECONDS = 60
_MAX_PER_WINDOW = 100


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiting per API key."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        api_key = request.headers.get("X-API-Key", request.client.host if request.client else "unknown")
        now = time.time()

        # Clean old entries
        window_start = now - _WINDOW_SECONDS
        _buckets[api_key] = [t for t in _buckets[api_key] if t > window_start]

        if len(_buckets[api_key]) >= _MAX_PER_WINDOW:
            from fastapi.responses import JSONResponse
            reset_at = int(_buckets[api_key][0] + _WINDOW_SECONDS)
            return JSONResponse(
                {"detail": "Rate limit exceeded. Retry after window resets."},
                status_code=429,
                headers={"X-RateLimit-Reset": str(reset_at)},
            )

        _buckets[api_key].append(now)
        response = await call_next(request)
        remaining = _MAX_PER_WINDOW - len(_buckets[api_key])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(_MAX_PER_WINDOW)
        return response
