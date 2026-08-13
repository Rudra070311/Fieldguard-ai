from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import Settings
from database.models import Pin
from .pin_hash import PinHasher
from .pin_verify import PinVerifier
from .lockout import LockoutManager
from .recovery import PinRecoveryManager

@dataclass(frozen=True)
class PinVerificationResult:
    success: bool
    locked: bool = False
    remaining_attempts: Optional[int] = None
    reason: Optional[str] = None

class PinService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        pin_hasher: PinHasher,
        pin_verifier: PinVerifier,
        lockout_manager: LockoutManager,
        recovery_manager: PinRecoveryManager,
        audit_logger: Any,
        risk_engine: Any,
    ) -> None:
        self.session = session
        self.settings = settings
        self.pin_hasher = pin_hasher
        self.pin_verifier = pin_verifier
        self.lockout_manager = lockout_manager
        self.recovery_manager = recovery_manager
        self.audit_logger = audit_logger
        self.risk_engine = risk_engine

    async def create_pin(self, user_id: UUID, pin: str, *, device_id: Optional[UUID] = None, request_id: Optional[UUID] = None) -> Pin:
        if not pin:
            raise ValueError("PIN cannot be empty.")

        existing = await self.pin_repository.get_active_by_user(user_id)

        if existing is not None:
            raise ValueError("An active PIN already exists.")

        self.pin_verifier.validate_pin_format(pin)
        pin_hash = self.pin_hasher.hash(pin)
        now = datetime.now(timezone.utc)
        pin_record = await self.pin_repository.create(
            user_id=user_id,
            pin_hash=pin_hash,
            hash_algorithm=self.pin_hasher.algorithm,
            hash_version=self.pin_hasher.version,
            failed_attempts=0,
            locked_until=None,
            created_at=now,
            updated_at=now,
            last_verified_at=None,
            last_changed_at=now,
            active=True,
        )

        await self.session.commit()
        await self.audit_logger.log_pin_created(
            user_id=user_id,
            device_id=device_id,
            request_id=request_id,
        )

        return pin_record

    async def verify_pin(self, pin: str, user_id: UUID, *, device_id: Optional[UUID] = None, ip_address: Optional[str] = None, request_id: Optional[UUID] = None) -> PinVerificationResult:
        pin_record = await self.pin_repository.get_active_by_user(user_id)

        if pin_record is None:
            return PinVerificationResult(
                success=False,
                reason="pin_not_configured",
            )

        if await self.lockout_manager.is_locked(pin_record):
            return PinVerificationResult(
                success=False,
                locked=True,
                reason="pin_locked",
            )

        is_valid = self.pin_hasher.verify(pin, pin_record.pin_hash,)

        if is_valid:
            await self.pin_repository.mark_verified(pin_record.id, verified_at=datetime.now(timezone.utc),)
            await self.lockout_manager.reset(pin_record.id)
            await self.session.commit()
            await self.audit_logger.log_pin_verified(
                user_id=user_id,
                device_id=device_id,
                request_id=request_id,
            )
            await self.risk_engine.record_pin_result(
                user_id=user_id,
                device_id=device_id,
                success=True,
                ip_address=ip_address,
            )

            return PinVerificationResult(success=True,)

        lockout_state = await self.lockout_manager.record_failure(pin_record.id)

        await self.session.commit()
        await self.audit_logger.log_pin_failed(
            user_id=user_id,
            device_id=device_id,
            request_id=request_id,
        )
        await self.risk_engine.record_pin_result(
            user_id=user_id,
            device_id=device_id,
            success=False,
            ip_address=ip_address,
        )

        return PinVerificationResult(
            success=False,
            locked=lockout_state.locked,
            remaining_attempts=lockout_state.remaining_attempts,
            reason="invalid_pin",
        )

    async def change_pin(self, user_id: UUID, current_pin: str, new_pin: str, *, device_id: Optional[UUID] = None, ip_address: Optional[str] = None, request_id: Optional[UUID] = None) -> Pin:
        verification = await self.verify_pin(
            user_id=user_id,
            pin=current_pin,
            device_id=device_id,
            ip_address=ip_address,
            request_id=request_id,
        )

        if not verification.success:
            raise ValueError("Current PIN is invalid.")

        self.pin_verifier.validate_pin_format(new_pin)

        if self.pin_hasher.verify(new_pin, (await self.pin_repository.get_active_by_user(user_id)).pin_hash):
            raise ValueError("New PIN must differ from the current PIN.")

        pin_record = await self.pin_repository.get_active_by_user(user_id)

        if pin_record is None:
            raise ValueError("PIN is not configured.")

        new_hash = self.pin_hasher.hash(new_pin)
        now = datetime.now(timezone.utc)

        await self.pin_repository.update_hash(
            pin_record.id,
            pin_hash=new_hash,
            hash_algorithm=self.pin_hasher.algorithm,
            hash_version=self.pin_hasher.version,
            failed_attempts=0,
            locked_until=None,
            last_changed_at=now,
        )
        await self.session.commit()
        await self.audit_logger.log_pin_changed(
            user_id=user_id,
            device_id=device_id,
            request_id=request_id,
        )

        return await self.pin_repository.get_by_id(pin_record.id)

    async def reset_pin(self, user_id: UUID, new_pin: str, recovery_token: str, *, device_id: Optional[UUID] = None, request_id: Optional[UUID] = None) -> Pin:
        if not recovery_token:
            raise ValueError("Recovery token is required.")

        self.pin_verifier.validate_pin_format(new_pin)
        recovery = await self.recovery_manager.verify(
            user_id=user_id,
            token=recovery_token,
        )

        if not recovery:
            raise ValueError("Invalid or expired recovery token.")

        pin_record = await self.pin_repository.get_active_by_user(user_id)
        new_hash = self.pin_hasher.hash(new_pin)
        now = datetime.now(timezone.utc)

        if pin_record is None:
            pin_record = await self.pin_repository.create(
                user_id=user_id,
                pin_hash=new_hash,
                hash_algorithm=self.pin_hasher.algorithm,
                hash_version=self.pin_hasher.version,
                failed_attempts=0,
                locked_until=None,
                created_at=now,
                updated_at=now,
                last_verified_at=None,
                last_changed_at=now,
                active=True,
            )
        else:
            await self.pin_repository.update_hash(
                pin_record.id,
                pin_hash=new_hash,
                hash_algorithm=self.pin_hasher.algorithm,
                hash_version=self.pin_hasher.version,
                failed_attempts=0,
                locked_until=None,
                last_changed_at=now,
            )

        await self.recovery_manager.consume(
            user_id=user_id,
            token=recovery_token,
        )
        await self.session.commit()
        await self.audit_logger.log_pin_reset(
            user_id=user_id,
            device_id=device_id,
            request_id=request_id,
        )

        return pin_record

    async def delete_pin(self, user_id: UUID, *, request_id: Optional[UUID] = None) -> bool:
        pin_record = await self.pin_repository.get_active_by_user(user_id)

        if pin_record is None:
            return False

        await self.pin_repository.deactivate(pin_record.id)
        await self.session.commit()
        await self.audit_logger.log_pin_deleted(
            user_id=user_id,
            request_id=request_id,
        )

        return True

    async def has_pin(self, user_id: UUID) -> bool:
        pin_record = await self.pin_repository.get_active_by_user(user_id)
        return pin_record is not None

    async def get_pin_status(self, user_id: UUID) -> dict[str, Any]:
        pin_record = await self.pin_repository.get_active_by_user(user_id)

        if pin_record is None:
            return {
                "configured": False,
                "locked": False,
                "failed_attempts": 0,
                "last_verified_at": None,
                "last_changed_at": None,
            }

        locked = await self.lockout_manager.is_locked(pin_record)

        return {
            "configured": True,
            "locked": locked,
            "failed_attempts": pin_record.failed_attempts,
            "last_verified_at": pin_record.last_verified_at,
            "last_changed_at": pin_record.last_changed_at,
        }

    async def unlock_pin(self, user_id: UUID, *, request_id: Optional[UUID] = None) -> bool:
        pin_record = await self.pin_repository.get_active_by_user(user_id)

        if pin_record is None:
            return False

        await self.lockout_manager.reset(pin_record.id)
        await self.session.commit()
        await self.audit_logger.log_pin_unlocked(
            user_id=user_id,
            request_id=request_id,
        )

        return True