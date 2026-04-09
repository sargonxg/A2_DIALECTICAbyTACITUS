"""SQLModel table definitions for DIALECTICA metadata store.

Stores user/workspace/API key/job metadata in PostgreSQL (Cloud SQL in production).
Neo4j still holds all conflict graph data.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def _ulid() -> str:
    from ulid import ULID

    return str(ULID())


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=_ulid, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    tier: str = "free"  # free | pro | enterprise
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceMeta(SQLModel, table=True):
    __tablename__ = "workspace_meta"

    id: str = Field(default_factory=_ulid, primary_key=True)
    name: str
    description: str = ""
    owner_id: str = Field(foreign_key="users.id", index=True)
    domain: str = "human_friction"  # human_friction | conflict_warfare
    template: Optional[str] = None
    status: str = "active"  # active | archived | deleted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyRecord(SQLModel, table=True):
    __tablename__ = "api_key_records"

    id: str = Field(default_factory=_ulid, primary_key=True)
    key_hash: str = Field(index=True)  # bcrypt hash of the raw API key
    name: str
    user_id: str = Field(foreign_key="users.id", index=True)
    tier: str = "standard"
    rate_limit: int = 100  # requests per minute
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None


class ExtractionJob(SQLModel, table=True):
    __tablename__ = "extraction_jobs"

    id: str = Field(default_factory=_ulid, primary_key=True)
    workspace_id: str = Field(foreign_key="workspace_meta.id", index=True)
    status: str = "pending"  # pending | running | completed | failed
    progress: float = 0.0
    stats: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
