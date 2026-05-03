"""Async SQLAlchemy engine + session factory for DIALECTICA metadata store."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

_engine = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        from dialectica_api.config import get_settings

        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.environment == "development",
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_factory


async def create_db_and_tables() -> None:
    """Create all tables if they don't exist. Called on API startup."""
    # Import models so SQLModel.metadata is populated
    from dialectica_api.database import models  # noqa: F401

    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
