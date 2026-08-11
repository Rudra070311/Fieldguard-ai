from __future__ import annotations
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

class PinRecoveryManager:
    def __init__(
        self,
        session: AsyncSession,
        settings,
        user_repository,
        pin_repository,
        otp_manager,
        magic_link_manager,
        pin_service,
        audit_logger,
        rate_limiter,
        risk_engine,
        session_manager,
    ) -> None:
        self.session = session
        self.settings = settings
        self.user_repository = user_repository
        self.pin_repository = pin_repository
        self.otp_manager = otp_manager
        self.magic_link_manager = magic_link_manager
        self.pin_service = pin_service
        self.audit_logger = audit_logger
        self.rate_limiter = rate_limiter
        self.risk_engine = risk_engine
        self.session_manager = session_manager

    async def request_recovery(self, user_id: UUID, method: str, destination: str,) -> dict[str, Any]:
        if method not in {"otp", "magic_link"}:
            raise ValueError("Unsupported recovery method.")
        if not destination:
            raise ValueError("Recovery destination is required.")

        allowed = await self.is_recovery_allowed(user_id)

        if not allowed:
            raise ValueError("PIN recovery is temporarily unavailable.")

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            return {
                "status": "recovery_requested",
                "method": method,
            }

        if method == "otp":
            await self.otp_manager.create(
                user_id=user_id,
                destination=destination,
                purpose="pin_recovery",
                channel="email",
            )

        elif method == "magic_link":
            await self.magic_link_manager.generate_magic_link(
                user_id=user_id,
                purpose="pin_recovery",
            )

        await self.audit_logger.log_event(
            user_id=user_id,
            event_type="pin_recovery_requested",
            result="success",
            metadata={"method": method,},
        )

        return {
            "status": "recovery_requested",
            "method": method,
        }

    async def verify_recovery(self, user_id: UUID, code_or_token: str, method: str,) -> dict[str, Any] | None:
        if not code_or_token:
            return None

        if method == "otp":
            verified = await self.otp_manager.verify(
                user_id=user_id,
                code=code_or_token,
                purpose="pin_recovery",
            )

        elif method == "magic_link":
            verified = await self.magic_link_manager.verify_magic_link(
                token=code_or_token,
                purpose="pin_recovery",
            )

        else:
            return None

        if not verified:
            await self._record_failed_recovery(
                user_id=user_id,
                method=method,
            )
            return None

        recovery_token = (
            await self.pin_repository.create_recovery_authorization(
                user_id=user_id,
                purpose="pin_recovery",
            )
        )

        await self.audit_logger.log_event(
            user_id=user_id,
            event_type="pin_recovery_verified",
            result="success",
            metadata={"method": method,},
        )

        return {
            "recovery_token": recovery_token,
            "expires_in_seconds": getattr(
                self.settings.auth,
                "pin_recovery_authorization_seconds",
                600,
            ),
        }

    async def reset_pin(self, user_id: UUID, recovery_token: str, new_pin: str,) -> bool:
        if not recovery_token:
            return False
        if not new_pin:
            raise ValueError("New PIN is required.")

        authorization = (
            await self.pin_repository.consume_recovery_authorization(
                user_id=user_id,
                token=recovery_token,
                purpose="pin_recovery",
            )
        )

        if authorization is None:
            await self._record_failed_recovery(
                user_id=user_id,
                method="recovery_authorization",
            )
            return False

        try:
            await self.pin_service.change_pin(
                user_id=user_id,
                new_pin=new_pin,
            )
            await self.session_manager.revoke_all_for_user(
                user_id=user_id,
                reason="pin_recovery",
            )
            await self.pin_repository.invalidate_all_recovery_tokens(
                user_id=user_id,
            )
            await self.audit_logger.log_event(
                user_id=user_id,
                event_type="pin_recovered",
                result="success",
            )
            await self.risk_engine.record_security_event(
                user_id=user_id,
                event_type="pin_recovery_completed",
            )
            await self.session.commit()

            return True

        except Exception:
            await self.session.rollback()
            raise

    async def recover_with_otp(self, user_id: UUID, otp: str,) -> dict[str, Any] | None:
        return await self.verify_recovery(
            user_id=user_id,
            code_or_token=otp,
            method="otp",
        )

    async def recover_with_magic_link(self, user_id: UUID, token: str) -> dict[str, Any] | None:
        return await self.verify_recovery(
            user_id=user_id,
            code_or_token=token,
            method="magic_link",
        )

    async def invalidate_recovery(self, user_id: UUID,) -> None:
        await self.pin_repository.invalidate_all_recovery_tokens(
            user_id=user_id,
        )
        await self.otp_manager.invalidate(
            user_id=user_id,
            purpose="pin_recovery",
        )
        await self.audit_logger.log_event(
            user_id=user_id,
            event_type="pin_recovery_invalidated",
            result="success",
        )
        await self.session.commit()

    async def is_recovery_allowed(self, user_id: UUID,) -> bool:
        allowed = await self.rate_limiter.is_allowed(
            user_id=user_id,
            action="pin_recovery",
        )

        if not allowed:
            return False

        risk_score = await self.risk_engine.get_user_risk_score(user_id=user_id)
        max_risk = getattr(
            self.settings.security,
            "max_pin_recovery_risk",
            0.85,
        )

        return risk_score <= max_risk

    async def _record_failed_recovery(self, user_id: UUID, method: str,) -> None:
        await self.audit_logger.log_event(
            user_id=user_id,
            event_type="pin_recovery_failed",
            result="failure",
            metadata={"method": method,},
        )
        await self.risk_engine.record_security_event(
            user_id=user_id,
            event_type="pin_recovery_failed",
        )

__all__ = ["PinRecoveryManager"]