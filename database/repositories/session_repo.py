from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from ..models import Session

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, session_id: UUID,) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token_hash(self, token_hash: str,) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(
                Session.session_token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def get_active_for_user(self, user_id: UUID,) -> list[Session]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.revoked.is_(False),
                Session.expires_at > now,
            )
        )
        return list(result.scalars().all())

    async def create(self, **session_data,) -> Session:
        session = Session(**session_data)
        self.session.add(session)
        await self.session.flush()

        return session

    async def revoke(self, session_id: UUID, reason: Optional[str] = None,) -> Optional[Session]:
        values = {
            "revoked": True,
            "revoked_at": func.now(),
        }

        if reason is not None:
            values["revocation_reason"] = reason

        await self.session.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(**values)
        )
        await self.session.flush()

        return await self.get_by_id(session_id)

    async def revoke_all_for_user(self, user_id: UUID, reason: Optional[str] = None,) -> None:
        values = {
            "revoked": True,
            "revoked_at": func.now(),
        }

        if reason is not None:
            values["revocation_reason"] = reason

        await self.session.execute(
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.revoked.is_(False),
            )
            .values(**values)
        )

        await self.session.flush()

    async def delete_expired(self) -> None:
        await self.session.execute(
            Session.__table__.delete().where(
                Session.expires_at < func.now()
            )
        )

        await self.session.flush()

__all__ = ["SessionRepository"]