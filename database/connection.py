import logging
from typing import AsyncGenerator, Optional
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from config.settings import settings

logger = logging.getLogger(__name__)
DATABASE_URL = settings.database_url()

async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.database.echo_sql,
    pool_size=settings.database.pool_size,
    pool_timeout=settings.database.timeout_seconds,
)

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.database.echo_sql,
    pool_size=settings.database.pool_size,
    pool_timeout=settings.database.timeout_seconds,
    pool_pre_ping=True,
    pool_recycle=1800,
    max_overflow=10,
    future=True,
    connect_args={"connect_timeout": settings.database.timeout_seconds},
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SyncSessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_database_health() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return False

async def startup_db() -> None:
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established successfully.")
    except Exception as e:
        logger.error("Failed to connect to database on startup: %s", e)

async def shutdown_db() -> None:
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed.")

__all__ = [
    "async_engine",
    "sync_engine",
    "AsyncSessionLocal",
    "SyncSessionLocal",
    "get_async_db",
    "check_database_health",
    "startup_db",
    "shutdown_db",
]