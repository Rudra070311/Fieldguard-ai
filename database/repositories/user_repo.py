from __future__ import annotations
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        normalized_email = email.strip().lower()

        result = await self.session.execute(
            select(User).where(User.email == normalized_email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def create(self, **user_data) -> User:
        if "email" in user_data:
            user_data["email"] = user_data["email"].strip().lower()

        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()

        return user

    async def update(self, user_id: UUID, **changes) -> Optional[User]:
        if not changes:
            return await self.get_by_id(user_id)

        if "email" in changes and changes["email"] is not None:
            changes["email"] = changes["email"].strip().lower()

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**changes)
        )
        await self.session.flush()

        return await self.get_by_id(user_id)

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)

        if user is None:
            return False

        await self.session.delete(user)
        await self.session.flush()

        return True

__all__ = ["UserRepository"]