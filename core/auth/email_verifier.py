from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID, uuid4
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

class EmailVerifier:
    def __init__(self, session, settings, email_sender):
        self.session = session
        self.settings = settings
        self.email_sender = email_sender

    async def create_verification(self, user_id: UUID, email: str,):
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.settings.email_verification_token_minutes)
        claims: Dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "iat": now,
            "exp": expires_at,
            "iss": self.settings.app.name,
            "aud": "ideez-api",
            "jti": str(uuid4()),
            "token_type": "email_verification",
        }
        token = jwt.encode(
            claims,
            self.settings.jwt_secret_value(),
            algorithm=self.settings.security.jwt_algorithm,
        )
        await self.session.execute({"user_id": str(user_id), "token": token, "expires_at": expires_at},)
        await self.session.commit()
        await self.email_sender.send_verification_email(email, token)

        return token

    async def verify(self, token: str,):
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_value(),
                algorithms=[self.settings.security.jwt_algorithm],
                issuer=self.settings.app.name,
                audience="ideez-api",
            )
        except ExpiredSignatureError:
            raise ValueError("Verification token has expired.")
        except InvalidTokenError:
            raise ValueError("Invalid verification token.")

        user_id = UUID(payload["sub"])
        email = payload["email"]

        verification_record = await self.session.get_verification_by_token(token)
        if not verification_record or verification_record.user_id != str(user_id):
            raise ValueError("Invalid verification token.")

        await self.session.mark_email_as_verified(user_id, email)
        await self.session.delete_verification_record(token)

        return {"user_id": user_id, "email": email}

    async def resend(self, user_id: UUID,):
        verification_record = await self.session.get_verification_by_user_id(user_id)
        if not verification_record:
            raise ValueError("No verification record found for this user.")

        email = verification_record.email
        await self.create_verification(user_id, email)
        yield {"message": "Verification email resent."}

    async def invalidate(self, user_id: UUID,):
        verification_record = await self.session.get_verification_by_user_id(user_id)
        if not verification_record:
            raise ValueError("No verification record found for this user.")

        await self.session.delete_verification_record(verification_record.token)
        yield {"message": "Verification token invalidated."}