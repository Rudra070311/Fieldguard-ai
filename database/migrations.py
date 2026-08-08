from __future__ import annotations
import logging
from typing import Final
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine
from .base import Base

logger = logging.getLogger(__name__)

MODEL_TABLES: Final[frozenset[str]] = frozenset(
    Base.metadata.tables.keys()
)

def get_metadata():
    return Base.metadata

def get_model_tables() -> frozenset[str]:
    return MODEL_TABLES

async def check_schema_connection(engine: AsyncEngine) -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database schema connection check failed.")
        return False

async def list_existing_tables(engine: AsyncEngine) -> list[str]:
    async with engine.connect() as connection:
        tables = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names()
        )
    return sorted(tables)

def get_missing_tables(existing_tables: list[str]) -> list[str]:
    existing = set(existing_tables)
    return sorted(MODEL_TABLES - existing)

__all__ = [
    "MODEL_TABLES",
    "get_metadata",
    "get_model_tables",
    "check_schema_connection",
    "list_existing_tables",
    "get_missing_tables",
]