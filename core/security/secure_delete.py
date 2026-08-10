from __future__ import annotations
from typing import Any, Iterable, Optional
from uuid import UUID
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

class SecureDeleteManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def delete_by_id(self, model: Any, record_id: UUID,) -> bool:
        result = await self.session.execute(delete(model).where(model.id == record_id))
        await self.session.flush()
        return result.rowcount > 0

    async def delete_by_ids(self, model: Any, record_ids: Iterable[UUID],) -> int:
        ids = list(record_ids)

        if not ids:
            return 0

        result = await self.session.execute(delete(model).where(model.id.in_(ids)))
        await self.session.flush()

        return result.rowcount or 0

    async def delete_for_user(self, model: Any, user_id: UUID,) -> int:
        result = await self.session.execute(delete(model).where(model.user_id == user_id))
        await self.session.flush()

        return result.rowcount or 0

    async def delete_with_filter(self, model: Any, *conditions: Any,) -> int:
        if not conditions:
            raise ValueError("Refusing unrestricted deletion.")

        result = await self.session.execute(delete(model).where(*conditions))
        await self.session.flush()

        return result.rowcount or 0

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()