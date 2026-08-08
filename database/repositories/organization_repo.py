from __future__ import annotations
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Organization

class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, organization_id: UUID) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.id == organization_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_for_user(self, user_id: UUID) -> list[Organization]:
        result = await self.session.execute(
            select(Organization).where(Organization.user_id == user_id)
        )
        return result.scalars().all()
    
    async def create(self, **organization_data) -> Organization:
        organization = Organization(**organization_data)
        self.session.add(organization)
        await self.session.flush()

        return organization

    async def update(self, organization_id: UUID, **organization_data) -> Optional[Organization]:
        await self.session.execute(
            update(Organization)
            .where(Organization.id == organization_id)
            .values(**organization_data)
        )
        await self.session.flush()
        return await self.get_by_id(organization_id)
    
    async def delete(self, organization_id: UUID) -> bool:
        organization = await self.get_by_id(organization_id)

        if organization is None:
            return False

        await self.session.delete(organization)
        await self.session.flush()

        return True
        
__all__ = ["OrganizationRepository"]