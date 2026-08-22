from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import Settings
from database.models import Pin

@dataclass(frozen=True)
class LockoutState:
    locked: bool
    remaining_attempts: Optional[int]
    locked_until: Optional[datetime] = None

class LockoutManager:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def _get_pin(self, pin_id: UUID) -> Pin:
        result = await self.session.execute(select(Pin).where(Pin.id == pin_id))
        pin_record = result.scalar_one_or_none()

        if pin_record is None:
            raise ValueError("PIN record not found.")

        return pin_record

    async def is_locked(self, pin_record: Pin) -> bool:
        now = datetime.now(timezone.utc)

        if pin_record.locked_until is None:
            return False
        if pin_record.locked_until <= now:
            await self._clear_expired_lock(pin_record)
            return False

        return True

    async def record_failure(self, pin_id: UUID) -> LockoutState:
        pin_record = await self._get_pin(pin_id)

        if await self.is_locked(pin_record):
            return LockoutState(
                locked=True,
                remaining_attempts=0,
                locked_until=pin_record.locked_until,
            )

        now = datetime.now(timezone.utc)
        max_attempts = self.settings.auth.max_failed_attempts
        lockout_minutes = self.settings.auth.account_lock_minutes
        failed_attempts = max(0, pin_record.failed_attempts) + 1
        pin_record.failed_attempts = failed_attempts

        if failed_attempts >= max_attempts:
            locked_until = now + timedelta(minutes=lockout_minutes)
            pin_record.locked_until = locked_until

            await self.session.flush()

            return LockoutState(
                locked=True,
                remaining_attempts=0,
                locked_until=locked_until,
            )

        pin_record.locked_until = None

        await self.session.flush()

        return LockoutState(
            locked=False,
            remaining_attempts=max_attempts - failed_attempts,
            locked_until=None,
        )

    async def reset(self, pin_id: UUID) -> None:
        pin_record = await self._get_pin(pin_id)
        pin_record.failed_attempts = 0
        pin_record.locked_until = None

        await self.session.flush()

    async def unlock(self, pin_id: UUID) -> None:
        await self.reset(pin_id)

    async def get_state(self, pin_id: UUID) -> LockoutState:
        pin_record = await self._get_pin(pin_id)
        locked = await self.is_locked(pin_record)

        if locked:
            return LockoutState(
                locked=True,
                remaining_attempts=0,
                locked_until=pin_record.locked_until,
            )

        max_attempts = self.settings.auth.max_failed_attempts
        failed_attempts = max(0, pin_record.failed_attempts)
        remaining = max(0, max_attempts - failed_attempts)

        return LockoutState(
            locked=False,
            remaining_attempts=remaining,
            locked_until=None,
        )

    async def _clear_expired_lock(self, pin_record: Pin) -> None:
        pin_record.failed_attempts = 0
        pin_record.locked_until = None

        await self.session.flush()