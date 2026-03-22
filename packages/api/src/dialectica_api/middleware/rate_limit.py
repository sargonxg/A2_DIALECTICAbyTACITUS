"""
Rate Limit Middleware — Sliding window per API key.

Default: 100 req/min. Backends: in-memory (dev) or Redis (production).
Backend selected via RATE_LIMIT_BACKEND env var (memory|redis).
"""

from __future__ import annotations

import abc
import logging
import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("dialectica.rate_limit")

_WINDOW_SECONDS = 60
_MAX_PER_WINDOW = 100


# ─── Backend ABC ──────────────────────────────────────────────────────────────


class RateLimitBackend(abc.ABC):
    """Abstract rate-limit backend."""

    @abc.abstractmethod
    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int, float]:
        """Check whether *key* is within its rate limit.

        Returns:
            (allowed, remaining, reset_at)
            - allowed: True if the request should proceed
            - remaining: number of requests left in the window
            - reset_at: UNIX timestamp when the window resets
        """
        ...

    async def close(self) -> None:  # noqa: B027
        """Clean up resources (optional)."""


# ─── In-Memory Backend ────────────────────────────────────────────────────────


class InMemoryBackend(RateLimitBackend):
    """Simple in-memory sliding window — suitable for single-process dev."""

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int, float]:
        now = time.time()
        window_start = now - window

        # Prune expired timestamps
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]

        if len(self._buckets[key]) >= limit:
            reset_at = self._buckets[key][0] + window
            remaining = 0
            return False, remaining, reset_at

        self._buckets[key].append(now)
        remaining = limit - len(self._buckets[key])
        reset_at = now + window
        return True, remaining, reset_at


# ─── Redis Backend ────────────────────────────────────────────────────────────


class RedisBackend(RateLimitBackend):
    """Redis sorted-set sliding window — production-grade, multi-process safe."""

    def __init__(self, redis_url: str) -> None:
        try:
            import redis.asyncio as aioredis
        except ImportError as err:
            raise ImportError(
                "redis package required for RedisBackend. "
                "Install with: pip install 'redis[hiredis]'"
            ) from err
        self._redis = aioredis.from_url(redis_url, decode_responses=True)

    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int, float]:

        now = time.time()
        window_start = now - window
        redis_key = f"rl:{key}"

        pipe = self._redis.pipeline(transaction=True)
        # Remove entries outside the window
        pipe.zremrangebyscore(redis_key, "-inf", window_start)
        # Count current entries
        pipe.zcard(redis_key)
        # Add current request (score = timestamp, member = unique)
        member = f"{now}:{id(pipe)}"
        pipe.zadd(redis_key, {member: now})
        # Set expiry on the key so it doesn't persist forever
        pipe.expire(redis_key, window + 1)
        # Get the oldest entry for reset_at
        pipe.zrange(redis_key, 0, 0, withscores=True)

        results = await pipe.execute()
        current_count = results[1]  # zcard result (before adding new)

        if current_count >= limit:
            # Over limit — remove the entry we just added
            await self._redis.zrem(redis_key, member)
            oldest = results[4]  # zrange result
            reset_at = oldest[0][1] + window if oldest else now + window
            return False, 0, reset_at

        remaining = limit - (current_count + 1)
        reset_at = now + window
        return True, remaining, reset_at

    async def close(self) -> None:
        await self._redis.close()


# ─── Backend Factory ──────────────────────────────────────────────────────────

_backend: RateLimitBackend | None = None


def get_rate_limit_backend() -> RateLimitBackend:
    """Return the configured rate-limit backend (singleton)."""
    global _backend
    if _backend is not None:
        return _backend

    from dialectica_api.config import get_settings

    settings = get_settings()
    backend_type = settings.rate_limit_backend.lower()

    if backend_type == "redis":
        logger.info('{"event":"rate_limit_backend","type":"redis","url":"%s"}', settings.redis_url)
        _backend = RedisBackend(settings.redis_url)
    else:
        logger.info('{"event":"rate_limit_backend","type":"memory"}')
        _backend = InMemoryBackend()

    return _backend


def set_rate_limit_backend(backend: RateLimitBackend) -> None:
    """Override the backend (useful for testing)."""
    global _backend
    _backend = backend


# ─── Middleware ────────────────────────────────────────────────────────────────


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiting per API key."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health/metrics endpoints
        path = request.url.path
        if path in {"/health", "/health/", "/metrics"}:
            return await call_next(request)

        api_key = request.headers.get(
            "X-API-Key", request.client.host if request.client else "unknown"
        )

        backend = get_rate_limit_backend()
        allowed, remaining, reset_at = await backend.check_rate_limit(
            api_key, _MAX_PER_WINDOW, _WINDOW_SECONDS
        )

        if not allowed:
            from fastapi.responses import JSONResponse

            return JSONResponse(
                {"detail": "Rate limit exceeded. Retry after window resets."},
                status_code=429,
                headers={
                    "X-RateLimit-Reset": str(int(reset_at)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Limit": str(_MAX_PER_WINDOW),
                    "Retry-After": str(max(1, int(reset_at - time.time()))),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(_MAX_PER_WINDOW)
        return response
