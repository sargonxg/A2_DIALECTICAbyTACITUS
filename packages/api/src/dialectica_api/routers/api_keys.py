"""
API Key Management Router — CRUD for scoped API keys.

Key format: pk_live_... (production), pk_test_... (sandbox)
Scopes: graph:read, graph:write, extract, reason, admin
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from dialectica_api.deps import get_current_tenant

router = APIRouter(prefix="/v1/api-keys", tags=["api-keys"])

# In-memory store (Redis/DB in production)
_key_store: dict[str, dict[str, Any]] = {}

VALID_SCOPES = {"graph:read", "graph:write", "extract", "reason", "admin"}


class CreateKeyRequest(BaseModel):
    name: str
    scopes: list[str] = Field(default=["graph:read"])
    environment: str = Field(default="live", pattern="^(live|test)$")
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class APIKeyResponse(BaseModel):
    key_id: str
    name: str
    key_prefix: str
    scopes: list[str]
    environment: str
    created_at: str
    expires_at: str | None = None
    last_used_at: str | None = None


class APIKeyCreated(APIKeyResponse):
    key: str  # Full key — only returned on creation


class RotateKeyRequest(BaseModel):
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


def _generate_key(environment: str) -> str:
    """Generate a prefixed API key."""
    prefix = "pk_live_" if environment == "live" else "pk_test_"
    return prefix + secrets.token_urlsafe(32)


@router.post("", response_model=APIKeyCreated, status_code=201)
async def create_api_key(
    body: CreateKeyRequest,
    tenant_id: str = Depends(get_current_tenant),
) -> APIKeyCreated:
    """Create a new scoped API key."""
    # Validate scopes
    invalid = set(body.scopes) - VALID_SCOPES
    if invalid:
        raise HTTPException(400, f"Invalid scopes: {invalid}. Valid: {VALID_SCOPES}")

    key = _generate_key(body.environment)
    key_id = str(uuid.uuid4())[:12]
    now = datetime.utcnow()
    expires_at = None
    if body.expires_in_days:
        expires_at = (now + timedelta(days=body.expires_in_days)).isoformat()

    entry = {
        "key_id": key_id,
        "name": body.name,
        "key_hash": hashlib.sha256(key.encode()).hexdigest(),
        "key_prefix": key[:12] + "...",
        "scopes": body.scopes,
        "environment": body.environment,
        "tenant_id": tenant_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at,
        "last_used_at": None,
    }
    _key_store[key_id] = entry

    return APIKeyCreated(
        key_id=key_id,
        name=body.name,
        key=key,
        key_prefix=entry["key_prefix"],
        scopes=body.scopes,
        environment=body.environment,
        created_at=entry["created_at"],
        expires_at=expires_at,
    )


@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(
    tenant_id: str = Depends(get_current_tenant),
) -> list[APIKeyResponse]:
    """List API keys for the current tenant."""
    return [
        APIKeyResponse(
            key_id=e["key_id"],
            name=e["name"],
            key_prefix=e["key_prefix"],
            scopes=e["scopes"],
            environment=e["environment"],
            created_at=e["created_at"],
            expires_at=e.get("expires_at"),
            last_used_at=e.get("last_used_at"),
        )
        for e in _key_store.values()
        if e["tenant_id"] == tenant_id
    ]


@router.delete("/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> None:
    """Revoke an API key."""
    entry = _key_store.get(key_id)
    if not entry or entry["tenant_id"] != tenant_id:
        raise HTTPException(404, "Key not found")
    del _key_store[key_id]


@router.post("/{key_id}/rotate", response_model=APIKeyCreated)
async def rotate_api_key(
    key_id: str,
    body: RotateKeyRequest,
    tenant_id: str = Depends(get_current_tenant),
) -> APIKeyCreated:
    """Rotate an API key — generates a new key, invalidates the old one."""
    entry = _key_store.get(key_id)
    if not entry or entry["tenant_id"] != tenant_id:
        raise HTTPException(404, "Key not found")

    new_key = _generate_key(entry["environment"])
    now = datetime.utcnow()
    expires_at = None
    if body.expires_in_days:
        expires_at = (now + timedelta(days=body.expires_in_days)).isoformat()

    entry["key_hash"] = hashlib.sha256(new_key.encode()).hexdigest()
    entry["key_prefix"] = new_key[:12] + "..."
    entry["created_at"] = now.isoformat()
    entry["expires_at"] = expires_at

    return APIKeyCreated(
        key_id=key_id,
        name=entry["name"],
        key=new_key,
        key_prefix=entry["key_prefix"],
        scopes=entry["scopes"],
        environment=entry["environment"],
        created_at=entry["created_at"],
        expires_at=expires_at,
    )
