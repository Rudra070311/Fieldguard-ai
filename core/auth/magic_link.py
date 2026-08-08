from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID

class MagicLinkPurpose(str, Enum):
    LOGIN = "login"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"

class MagicLinkError(Exception):
    pass

class MagicLinkRateLimitError(MagicLinkError):
    pass

class InvalidMagicLinkError(MagicLinkError):
    pass

class MagicLinkManager:
    TOKEN_BYTES = 32

    def __init__(
        self,
        magic_link_repository,
        user_repository,
        session_manager,
        email_sender,
        rate_limiter,
        risk_engine,
        settings,
    ):
        self.magic_link_repository = magic_link_repository
        self.user_repository = user_repository
        self.session_manager = session_manager
        self.email_sender = email_sender
        self.rate_limiter = rate_limiter
        self.risk_engine = risk_engine
        self.settings = settings

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_purpose(purpose: str) -> MagicLinkPurpose:
        try:
            return MagicLinkPurpose(purpose)
        except ValueError as exc:
            raise InvalidMagicLinkError("Unsupported magic-link purpose.") from exc

    def _expiration_time(self) -> datetime:
        minutes = self.settings.auth.magic_link_expiry_minutes
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    def _base_url(self) -> str:
        return self.settings.auth.magic_link_base_url.rstrip("/")

    async def generate_magic_link(self, user_id: UUID, purpose: str,) -> str:
        purpose_enum = self._validate_purpose(purpose)
        allowed = await self.rate_limiter.is_allowed(
            user_id=user_id,
            action="magic_link",
        )

        if not allowed:
            raise MagicLinkRateLimitError("Magic-link rate limit exceeded.")

        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            raise InvalidMagicLinkError("Unable to generate magic link.")

        token = secrets.token_urlsafe(self.TOKEN_BYTES)
        token_hash = self._hash_token(token)
        expires_at = self._expiration_time()

        await self.magic_link_repository.create(
            user_id=user_id,
            token_hash=token_hash,
            purpose=purpose_enum.value,
            expires_at=expires_at,
        )

        magic_link_url = (
            f"{self._base_url()}"
            f"?token={token}"
            f"&purpose={purpose_enum.value}"
        )

        await self.email_sender.send_magic_link(
            user_id=user_id,
            magic_link_url=magic_link_url,
            purpose=purpose_enum.value,
        )

        return magic_link_url

    async def verify_magic_link(self, token: str, purpose: str, *, risk_context: dict[str, Any] | None = None,) -> dict[str, Any]:
        purpose_enum = self._validate_purpose(purpose)

        if not token or len(token) < 20:
            raise InvalidMagicLinkError("Invalid magic link.")
        
        token_hash = self._hash_token(token)

        stored_link = await self.magic_link_repository.get_by_token_hash(
            token_hash=token_hash,
            purpose=purpose_enum.value,
        )

        if stored_link is None:
            raise InvalidMagicLinkError("Invalid or expired magic link.")

        now = datetime.now(timezone.utc)

        if stored_link.expires_at <= now:
            await self.magic_link_repository.delete(stored_link.id)
            raise InvalidMagicLinkError("Magic link has expired.")

        if getattr(stored_link, "used_at", None) is not None:
            raise InvalidMagicLinkError("Magic link has already been used.")

        user_id = stored_link.user_id
        factors = risk_context or {}
        risk_result = await self.risk_engine.evaluate(
            user_id=user_id,
            event_type="magic_link_verification",
            factors=factors,
        )
        action = risk_result.get("action", "allow")

        if action == "block":
            await self.magic_link_repository.delete(stored_link.id)
            raise InvalidMagicLinkError("Magic-link authentication was denied.")

        consumed = await self.magic_link_repository.consume(
            link_id=stored_link.id,
            consumed_at=now,
        )

        if not consumed:
            raise InvalidMagicLinkError("Magic link has already been used.")

        session = None

        if purpose_enum == MagicLinkPurpose.LOGIN:
            session = await self.session_manager.create_authenticated_session(
                user_id=user_id,
                authentication_method="magic_link",
                authentication_level="passwordless",
                risk_result=risk_result,
            )

        elif purpose_enum == MagicLinkPurpose.EMAIL_VERIFICATION:
            await self.user_repository.mark_email_verified(user_id=user_id,)

        elif purpose_enum == MagicLinkPurpose.PASSWORD_RESET:
            pass

        return {
            "success": True,
            "user_id": user_id,
            "purpose": purpose_enum.value,
            "risk": risk_result,
            "session": session,
        }

    async def resend_magic_link(self, user_id: UUID, purpose: str,) -> str:
        purpose_enum = self._validate_purpose(purpose)
        allowed = await self.rate_limiter.is_allowed(
            user_id=user_id,
            action="magic_link",
        )

        if not allowed:
            raise MagicLinkRateLimitError("Magic-link rate limit exceeded.")

        await self.magic_link_repository.invalidate_active(
            user_id=user_id,
            purpose=purpose_enum.value,
        )

        return await self.generate_magic_link(
            user_id=user_id,
            purpose=purpose_enum.value,
        )

    async def invalidate_magic_link(self, token: str, purpose: str,) -> None:
        purpose_enum = self._validate_purpose(purpose)
        token_hash = self._hash_token(token)

        await self.magic_link_repository.invalidate_by_hash(
            token_hash=token_hash,
            purpose=purpose_enum.value,
        )

    async def cleanup_expired_magic_links(self) -> int:
        return await self.magic_link_repository.delete_expired(now=datetime.now(timezone.utc))


__all__ = [
    "MagicLinkManager",
    "MagicLinkPurpose",
    "MagicLinkError",
    "MagicLinkRateLimitError",
    "InvalidMagicLinkError",
]