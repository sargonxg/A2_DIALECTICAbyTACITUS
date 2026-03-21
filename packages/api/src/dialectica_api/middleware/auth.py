"""
Auth Middleware — API key authentication for DIALECTICA API.

Supports multiple API keys with permission levels (admin, standard, readonly).
Keys loaded from API_KEYS_JSON env var or ADMIN_API_KEY for backward compat.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("dialectica.auth")

# Public paths that don't require authentication
_PUBLIC_PATHS = {"/health", "/health/", "/docs", "/openapi.json", "/redoc", "/metrics", "/v1/waitlist"}

# Permission levels (ordered from least to most privileged)
PERMISSION_LEVELS = ("readonly", "standard", "admin")


# ─── Key Store ────────────────────────────────────────────────────────────────


class APIKeyEntry:
    """Parsed API key with metadata."""

    __slots__ = ("key", "level", "tenant_id", "expires_at")

    def __init__(
        self,
        key: str,
        level: str = "admin",
        tenant_id: str = "admin",
        expires_at: str | None = None,
    ) -> None:
        self.key = key
        if level not in PERMISSION_LEVELS:
            raise ValueError(f"Invalid permission level: {level!r}. Must be one of {PERMISSION_LEVELS}")
        self.level = level
        self.tenant_id = tenant_id
        self.expires_at = expires_at

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > expiry
        except (ValueError, TypeError):
            return True  # Malformed date treated as expired

    @property
    def is_admin(self) -> bool:
        return self.level == "admin"

    @property
    def is_readonly(self) -> bool:
        return self.level == "readonly"


def load_api_keys() -> dict[str, APIKeyEntry]:
    """Load API keys from environment configuration.

    Priority:
    1. API_KEYS_JSON — full key definitions with permissions
    2. ADMIN_API_KEY — backward-compatible single admin key
    """
    keys: dict[str, APIKeyEntry] = {}

    # Load from API_KEYS_JSON if available
    api_keys_json = os.getenv("API_KEYS_JSON", "").strip()
    if api_keys_json and api_keys_json != "[]":
        try:
            entries = json.loads(api_keys_json)
            if not isinstance(entries, list):
                raise ValueError("API_KEYS_JSON must be a JSON array")
            for entry in entries:
                if not isinstance(entry, dict) or "key" not in entry:
                    logger.warning('{"event":"api_key_load_skip","reason":"missing key field"}')
                    continue
                api_entry = APIKeyEntry(
                    key=entry["key"],
                    level=entry.get("level", "standard"),
                    tenant_id=entry.get("tenant_id", "default"),
                    expires_at=entry.get("expires_at"),
                )
                keys[api_entry.key] = api_entry
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error('{"event":"api_keys_json_parse_error","error":"%s"}', exc)

    # Backward compatibility: ADMIN_API_KEY
    admin_key = os.getenv("ADMIN_API_KEY", "").strip()
    if admin_key and admin_key not in keys:
        keys[admin_key] = APIKeyEntry(
            key=admin_key, level="admin", tenant_id="admin"
        )

    return keys


def validate_production_config() -> None:
    """Raise if production environment is missing required auth config.

    Called at startup — prevents running production without a real admin key.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment != "production":
        return

    admin_key = os.getenv("ADMIN_API_KEY", "").strip()
    api_keys_json = os.getenv("API_KEYS_JSON", "").strip()

    has_admin_key = bool(admin_key) and admin_key != "dev-admin-key-change-in-production"
    has_api_keys = bool(api_keys_json) and api_keys_json != "[]"

    if not has_admin_key and not has_api_keys:
        raise RuntimeError(
            "PRODUCTION SAFETY: ADMIN_API_KEY (or API_KEYS_JSON with admin-level key) "
            "must be set when ENVIRONMENT=production. "
            "Refusing to start with default/missing credentials."
        )


# ─── Middleware ────────────────────────────────────────────────────────────────


class AuthMiddleware(BaseHTTPMiddleware):
    """Validates X-API-Key on every request and sets request.state attributes."""

    def __init__(self, app: Any, **kwargs: Any) -> None:
        super().__init__(app, **kwargs)
        self._keys: dict[str, APIKeyEntry] | None = None

    def _get_keys(self) -> dict[str, APIKeyEntry]:
        if self._keys is None:
            self._keys = load_api_keys()
        return self._keys

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        from fastapi.responses import JSONResponse

        # Skip auth for public paths
        path = request.url.path
        if any(path.startswith(p) for p in _PUBLIC_PATHS):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "")
        if not api_key:
            return JSONResponse(
                {"detail": "Authentication required — provide X-API-Key header."},
                status_code=401,
            )

        keys = self._get_keys()
        entry = keys.get(api_key)

        if entry is None:
            return JSONResponse(
                {"detail": "Invalid API key."},
                status_code=401,
            )

        # Check expiration
        if entry.is_expired:
            return JSONResponse(
                {"detail": "API key has expired."},
                status_code=401,
            )

        # Read-only keys blocked on non-GET methods
        if entry.is_readonly and request.method not in ("GET", "HEAD", "OPTIONS"):
            return JSONResponse(
                {"detail": "Read-only API key cannot perform write operations."},
                status_code=403,
            )

        # Set request state
        request.state.tenant_id = entry.tenant_id
        request.state.is_admin = entry.is_admin
        request.state.permission_level = entry.level

        return await call_next(request)
