"""Tests for database models — table creation, CRUD, FK constraints."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from dialectica_api.database.models import (
    ApiKeyRecord,
    ExtractionJob,
    GraphEdgeRecord,
    GraphObjectRecord,
    OntologyProfileRecord,
    PipelineRun,
    SourceChunkRecord,
    User,
    WorkspaceMeta,
)


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_user_insert_and_query(session: AsyncSession):
    user = User(email="test@example.com", name="Test User")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.tier == "free"


@pytest.mark.asyncio
async def test_workspace_meta_insert(session: AsyncSession):
    user = User(email="owner@example.com", name="Owner")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    ws = WorkspaceMeta(name="Test WS", owner_id=user.id)
    session.add(ws)
    await session.commit()
    await session.refresh(ws)
    assert ws.id is not None
    assert ws.status == "active"
    assert ws.owner_id == user.id


@pytest.mark.asyncio
async def test_api_key_record_insert(session: AsyncSession):
    user = User(email="apikey@example.com", name="API User")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    key = ApiKeyRecord(key_hash="abc123hash", name="My Key", user_id=user.id, tier="free")
    session.add(key)
    await session.commit()
    await session.refresh(key)
    assert key.id is not None
    assert key.rate_limit == 100
    assert key.revoked_at is None


@pytest.mark.asyncio
async def test_extraction_job_insert(session: AsyncSession):
    user = User(email="job@example.com", name="Job User")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    ws = WorkspaceMeta(name="Job WS", owner_id=user.id)
    session.add(ws)
    await session.commit()
    await session.refresh(ws)

    job = ExtractionJob(workspace_id=ws.id, status="pending")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    assert job.id is not None
    assert job.status == "pending"
    assert job.completed_at is None


@pytest.mark.asyncio
async def test_pipeline_audit_models_insert(session: AsyncSession):
    run = PipelineRun(
        id="episode_1",
        workspace_id="ws",
        tenant_id="tenant",
        source_id="source_1",
        source_hash="hash",
        source_title="fixture",
        objective="Understand the conflict",
        ontology_profile="human-friction",
        pipeline={"stages": ["source_cleaning", "neo4j_upsert"]},
    )
    session.add(run)
    session.add(
        SourceChunkRecord(
            id="chunk_1",
            run_id=run.id,
            workspace_id="ws",
            source_id="source_1",
            ordinal=0,
            label="Chunk 1",
            text="Alice must meet Bob.",
        )
    )
    session.add(
        OntologyProfileRecord(
            id="episode_1:ontology",
            run_id=run.id,
            workspace_id="ws",
            profile_id="human-friction",
            plan={"required_nodes": ["Actor", "Claim"]},
        )
    )
    session.add(
        GraphObjectRecord(
            id="actor_1",
            run_id=run.id,
            workspace_id="ws",
            kind="Actor",
            source_ids=["source_1"],
            payload={"name": "Alice"},
        )
    )
    session.add(
        GraphEdgeRecord(
            id="edge_1",
            run_id=run.id,
            workspace_id="ws",
            kind="MENTIONS",
            source_id="actor_1",
            target_id="claim_1",
            source_ids=["source_1"],
            payload={"kind": "MENTIONS"},
        )
    )
    await session.commit()
    await session.refresh(run)

    assert run.id == "episode_1"
    assert run.status == "running"
    assert run.pipeline["stages"]
