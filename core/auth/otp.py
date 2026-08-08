from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import hashlib
import hmac
import secrets

class OTPManager:
    def __init__(
        self,
        session,
        settings,
        otp_repository,
        notification_sender,
        rate_limiter,
    ):
        self.session = session
        self.settings = settings
        self.otp_repository = otp_repository
        self.notification_sender = notification_sender
        self.rate_limiter = rate_limiter

    def _generate_code(self) -> str:
        length = self.settings.auth.otp_length
        upper_bound = 10 ** length

        return str(secrets.randbelow(upper_bound)).zfill(length)

    def _hash_code(self, code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def _verify_hash(self, code: str, stored_hash: str) -> bool:
        calculated_hash = self._hash_code(code)

        return hmac.compare_digest(
            calculated_hash,
            stored_hash,
        )

    def _expiration_time(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.auth.otp_expiry_minutes
        )

    async def generate_otp(self, user_id: UUID, otp_type: str,) -> str:
        allowed = await self.rate_limiter.is_allowed(
            user_id=user_id,
            action="otp",
        )

        if not allowed:
            raise ValueError("OTP rate limit exceeded. Please try again later.")

        otp = self._generate_code()
        otp_hash = self._hash_code(otp)
        expires_at = self._expiration_time()

        await self.otp_repository.invalidate_active(
            user_id=user_id,
            purpose=otp_type,
        )
        await self.otp_repository.create(
            user_id=user_id,
            purpose=otp_type,
            otp_hash=otp_hash,
            expires_at=expires_at,
        )
        await self.notification_sender.send_otp(
            user_id=user_id,
            otp=otp,
            purpose=otp_type,
        )

        return otp

    async def create(self, user_id: UUID, purpose: str, channel: str,) -> bool:
        if channel not in {"email", "sms"}:
            raise ValueError("Unsupported OTP delivery channel.")

        await self.generate_otp(
            user_id=user_id,
            otp_type=purpose,
        )

        return True

    async def verify(self, user_id: UUID, code: str, purpose: str,) -> bool:
        if not code:
            return False

        record = await self.otp_repository.get_active(
            user_id=user_id,
            purpose=purpose,
        )

        if record is None:
            return False

        now = datetime.now(timezone.utc)

        if record.expires_at <= now:
            await self.otp_repository.invalidate(record.id )
            return False

        if getattr(record, "used_at", None) is not None:
            return False

        max_attempts = self.settings.auth.max_failed_attempts

        if record.failed_attempts >= max_attempts:
            await self.otp_repository.invalidate(record.id)
            return False

        if not self._verify_hash(code, record.otp_hash,):
            await self.otp_repository.increment_failed_attempts(record.id)
            return False

        consumed = await self.otp_repository.consume(
            record.id,
            verified_at=now,
        )

        if not consumed:
            return False

        return True

    async def resend(self, user_id: UUID, purpose: str,) -> bool:
        allowed = await self.rate_limiter.is_allowed(user_id=user_id, action="otp_resend",)

        if not allowed:
            raise ValueError("OTP resend rate limit exceeded.")

        await self.otp_repository.invalidate_active(
            user_id=user_id,
            purpose=purpose,
        )
        await self.generate_otp(
            user_id=user_id,
            otp_type=purpose,
        )

        return True

    async def invalidate(self, user_id: UUID, purpose: str,) -> None:
        await self.otp_repository.invalidate_active(user_id=user_id, purpose=purpose,)

    async def cleanup_expired(self) -> int:
        return await self.otp_repository.delete_expired(now=datetime.now(timezone.utc))

__all__ = [
    "OTPManager",
]