"""SQLModel table definitions for DIALECTICA metadata store.

Stores user/workspace/API key/job metadata in PostgreSQL (Cloud SQL in production).
Neo4j still holds all conflict graph data.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, Text, UniqueConstraint
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
    template: str | None = None
    status: str = "active"  # active | archived | deleted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyRecord(SQLModel, table=True):
    __tablename__ = "api_key_records"

    id: str = Field(default_factory=_ulid, primary_key=True)
    key_hash: str = Field(unique=True)  # bcrypt hash of the raw API key
    name: str
    user_id: str = Field(foreign_key="users.id", index=True)
    tier: str = "standard"
    rate_limit: int = 100  # requests per minute
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: datetime | None = None


class ExtractionJob(SQLModel, table=True):
    __tablename__ = "extraction_jobs"

    id: str = Field(default_factory=_ulid, primary_key=True)
    workspace_id: str = Field(foreign_key="workspace_meta.id", index=True)
    status: str = "pending"  # pending | running | completed | failed
    progress: float = 0.0
    stats: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class PipelineRun(SQLModel, table=True):
    """Durable Cloud SQL audit row for ingestion and graph materialization."""

    __tablename__ = "pipeline_runs"

    id: str = Field(primary_key=True)
    workspace_id: str = Field(index=True)
    tenant_id: str = Field(default="default", index=True)
    source_id: str = Field(index=True)
    source_hash: str = Field(index=True)
    source_title: str = ""
    source_type: str = "text"
    source_uri: str | None = None
    objective: str = ""
    ontology_profile: str = "human-friction"
    status: str = Field(default="running", index=True)
    duplicate: bool = False
    object_count: int = 0
    edge_count: int = 0
    chunk_count: int = 0
    cleaned_chars: int = 0
    original_chars: int = 0
    pipeline: dict = Field(default_factory=dict, sa_column=Column(JSON))
    errors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: datetime | None = None


class SourceChunkRecord(SQLModel, table=True):
    """Pre-ingestion chunk record for large-scale ingestion without Databricks."""

    __tablename__ = "source_chunk_records"
    __table_args__ = (UniqueConstraint("run_id", "ordinal", name="uq_source_chunk_run_ordinal"),)

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    source_id: str = Field(index=True)
    ordinal: int
    label: str
    start_char: int = 0
    end_char: int = 0
    char_count: int = 0
    reason: str = ""
    text: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OntologyProfileRecord(SQLModel, table=True):
    """Dynamic ontology profile chosen/generated for a pipeline run."""

    __tablename__ = "ontology_profile_records"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    profile_id: str = Field(index=True)
    objective: str = ""
    plan: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GraphObjectRecord(SQLModel, table=True):
    """Cloud SQL mirror of graph objects for audit, search fallback, and rebuilds."""

    __tablename__ = "graph_object_records"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    tenant_id: str = Field(default="default", index=True)
    kind: str = Field(index=True)
    source_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    confidence: float = 1.0
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class GraphEdgeRecord(SQLModel, table=True):
    """Cloud SQL mirror of graph edges for audit, search fallback, and rebuilds."""

    __tablename__ = "graph_edge_records"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    workspace_id: str = Field(index=True)
    tenant_id: str = Field(default="default", index=True)
    kind: str = Field(index=True)
    source_id: str = Field(index=True)
    target_id: str = Field(index=True)
    source_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    confidence: float = 1.0
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
