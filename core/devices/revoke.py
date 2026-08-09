from __future__ import annotations
from typing import Optional
from uuid import UUID

class DeviceRevocationManager:
    def __init__(
        self,
        session,
        settings,
        device_repository,
        session_manager,
        audit_logger,
        risk_engine,
    ):
        self.session = session
        self.settings = settings
        self.device_repository = device_repository
        self.session_manager = session_manager
        self.audit_logger = audit_logger
        self.risk_engine = risk_engine

    async def revoke_device(self, user_id: UUID, device_id: UUID, reason: str = "manual_revocation",) -> bool:
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if device.user_id != user_id:
            return False

        await self.device_repository.revoke_device(
            device_id=device_id,
            reason=reason,
        )
        await self.revoke_device_sessions(
            device_id=device_id,
            reason=reason,
        )
        await self.audit_logger.log_device_revocation(
            user_id=user_id,
            device_id=device_id,
            reason=reason,
        )
        await self.risk_engine.update_device_risk_score(
            device_id=device_id,
            revoked=True,
        )
        await self.session.commit()

        return True

    async def revoke_all_devices(self, user_id: UUID, reason: str = "all_devices_revoked",) -> int:
        devices = await self.device_repository.get_by_user(user_id)
        revoked_count = 0

        for device in devices:
            if getattr(device, "revoked", False):
                continue

            await self.device_repository.revoke_device(
                device_id=device.id,
                reason=reason,
            )
            await self.revoke_device_sessions(
                device_id=device.id,
                reason=reason,
            )
            await self.audit_logger.log_device_revocation(
                user_id=user_id,
                device_id=device.id,
                reason=reason,
            )
            await self.risk_engine.update_device_risk_score(
                device_id=device.id,
                revoked=True,
            )
            revoked_count += 1
            
        await self.session.commit()

        return revoked_count

    async def revoke_device_sessions(self, device_id: UUID, reason: str = "device_revoked",) -> None:
        await self.session_manager.revoke_sessions_for_device(
            device_id=device_id,
            reason=reason,
        )

    async def is_revoked(self, device_id: UUID,) -> bool:
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False

        return bool(getattr(device, "revoked", False))

    async def restore(self, user_id: UUID, device_id: UUID,) -> bool:
        device = await self.device_repository.get_by_id(device_id)

        if device is None:
            return False
        if device.user_id != user_id:
            return False

        await self.device_repository.restore_device(
            device_id=device_id,
        )
        await self.audit_logger.log_device_restoration(
            user_id=user_id,
            device_id=device_id,
        )
        await self.risk_engine.update_device_risk_score(
            device_id=device_id,
            revoked=False,
        )
        await self.session.commit()
        
        return True