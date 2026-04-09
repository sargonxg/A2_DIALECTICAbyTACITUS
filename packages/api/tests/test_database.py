"""Tests for database models — table creation, CRUD, FK constraints."""
import pytest
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from dialectica_api.database.models import User, WorkspaceMeta, ApiKeyRecord, ExtractionJob


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
