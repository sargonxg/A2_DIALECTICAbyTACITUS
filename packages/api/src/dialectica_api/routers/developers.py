"""
Developers Router — API key management and usage endpoints.
"""
from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant
from dialectica_api.middleware.usage import get_usage_stats

router = APIRouter(prefix="/v1/developers", tags=["developers"])

# In-memory key store (use Spanner in production)
_api_keys: dict[str, dict[str, Any]] = {}


class ApiKeyCreate(BaseModel):
    name: str
    rate_limit_per_min: int = 100


class ApiKeyResponse(BaseModel):
    key_id: str
    name: str
    api_key: str
    tenant_id: str
    created_at: str
    rate_limit_per_min: int


@router.post("/keys", response_model=ApiKeyResponse, status_code=201)
async def create_api_key(
    body: ApiKeyCreate,
    tenant_id: str = Depends(get_current_tenant),
) -> ApiKeyResponse:
    """Create a new API key for the current tenant."""
    key_id = str(uuid.uuid4())[:8]
    api_key = f"tenant-{tenant_id}-{secrets.token_urlsafe(24)}"
    now = datetime.utcnow().isoformat()
    key_data = {
        "key_id": key_id,
        "name": body.name,
        "api_key": api_key,
        "tenant_id": tenant_id,
        "created_at": now,
        "rate_limit_per_min": body.rate_limit_per_min,
    }
    _api_keys[key_id] = key_data
    return ApiKeyResponse(**key_data)


@router.get("/keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    tenant_id: str = Depends(get_current_tenant),
) -> list[ApiKeyResponse]:
    """List API keys for the current tenant."""
    return [
        ApiKeyResponse(**k)
        for k in _api_keys.values()
        if k["tenant_id"] == tenant_id
    ]


@router.delete("/keys/{key_id}", status_code=204)
async def delete_api_key(
    key_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> None:
    """Delete an API key."""
    key = _api_keys.get(key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found.")
    if key["tenant_id"] != tenant_id and tenant_id != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
    del _api_keys[key_id]


@router.get("/usage")
async def get_my_usage(
    tenant_id: str = Depends(get_current_tenant),
) -> dict[str, Any]:
    """Get API usage statistics for the current tenant."""
    return {
        "tenant_id": tenant_id,
        "usage": get_usage_stats(tenant_id),
    }
