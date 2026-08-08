from __future__ import annotations
from typing import Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Device

class DeviceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, device_id: UUID) -> Optional[Device]:
        result = await self.session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID) -> list[Device]:
        result = await self.session.execute(
            select(Device).where(Device.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_by_fingerprint(self, fingerprint: str) -> Optional[Device]:
        result = await self.session.execute(
            select(Device).where(Device.fingerprint == fingerprint)
        )
        return result.scalar_one_or_none()

    async def create(self, **device_data) -> Device:
        device = Device(**device_data)
        self.session.add(device)
        await self.session.flush()
        return device

    async def update_trust(self, device_id: UUID, trust_score: float) -> Optional[Device]:
        await self.session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(trust_score=trust_score)
        )
        await self.session.flush()
        return await self.get_by_id(device_id)
    
    async def revoke(self, device_id: UUID) -> Optional[Device]:
        await self.session.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(revoked=True)
        )
        await self.session.flush()
        return await self.get_by_id(device_id)
    
    async def delete(self, device_id: UUID) -> bool:
        device = await self.get_by_id(device_id)

        if device is None:
            return False

        await self.session.delete(device)
        await self.session.flush()
        return True
    
__all__ = ["DeviceRepository"]