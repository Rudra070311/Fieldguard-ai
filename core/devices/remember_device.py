from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

class RememberDeviceManager:
    def __init__(
        self,
        session,
        settings,
        device_repository,
        trust_manager,
        fingerprint_manager,
        audit_logger,
        risk_engine,
    ):
        self.session = session
        self.settings = settings
        self.device_repository = device_repository
        self.trust_manager = trust_manager
        self.fingerprint_manager = fingerprint_manager
        self.audit_logger = audit_logger
        self.risk_engine = risk_engine
        
    async def remember(self, user_id: UUID, device_id: UUID, fingerprint: Optional[float] = None, trust_score: Optional[float] = None, expires_at: Optional[datetime] = None):
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if device.user_id != user_id:
            return False
        if getattr(device, "revoked", False):
            return False
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=self.settings.devices.remember_days)

        if trust_score is None:
            trust_score = await self.trust_manager.calculate(
                device_id=device_id,
                fingerprint=fingerprint,
            )

        if trust_score < self.settings.devices.trust_threshold:
            return False

        await self.device_repository.remember_device(
            user_id=user_id,
            device_id=device_id,
            fingerprint=fingerprint,
            trust_score=trust_score,
            expires_at=expires_at,
        )
        await self.audit_logger.log_device_trusted(
            user_id=user_id,
            device_id=device_id,
        )
        await self.risk_engine.update_device_risk_score(
            device_id=device_id,
            revoked=False,
        )
        await self.session.commit()

        return True
    
    async def is_remembered(self, user_id: UUID, device_id: UUID):
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if device.user_id != user_id:
            return False
        if getattr(device, "revoked", False):
            return False

        expires_at = getattr(device, "remembered_until", None)

        if expires_at is not None:
            now = datetime.now(timezone.utc)

            if expires_at <= now:
                await self.device_repository.unremember_device(user_id, device_id)
                await self.session.flush()
                return False

        return bool(getattr(device, "remembered", False))


    async def get_remembered_devices(self, user_id: UUID):
        devices = await self.device_repository.get_by_user(user_id)
        now = datetime.now(timezone.utc)
        remembered = []

        for device in devices:
            if getattr(device, "revoked", False):
                continue
            if not getattr(device, "remembered", False):
                continue

            expires_at = getattr(device, "remembered_until", None)

            if expires_at is not None and expires_at <= now:
                await self.device_repository.unremember_device(user_id, device.id,)
                continue
            remembered.append(device)

        await self.session.flush()

        return remembered

    async def refresh(self, fingerprint: Optional[str] = None, trust_score: Optional[float] = None, device_id: UUID = None):
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if getattr(device, "revoked", False):
            return False
        if fingerprint is None:
            fingerprint = getattr(device, "fingerprint", None)
        if fingerprint is None:
            return False
        if trust_score is None:
            trust_score = await self.trust_manager.calculate(device_id=device_id, fingerprint=fingerprint,)
        if trust_score < self.settings.devices.trust_threshold:
            return False

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=self.settings.devices.remember_days
        )

        await self.device_repository.remember_device(
            user_id=device.user_id,
            device_id=device_id,
            fingerprint=fingerprint,
            trust_score=trust_score,
            expires_at=expires_at,
        )
        await self.session.flush()

        return True


    async def unremember(self, user_id: UUID, device_id: UUID):
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if device.user_id != user_id:
            return False

        await self.device_repository.unremember_device(
            user_id,
            device_id,
        )
        await self.audit_logger.log_device_unremembered(
            user_id=user_id,
            device_id=device_id,
        )
        await self.session.commit()
        
        return True