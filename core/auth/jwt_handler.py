from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from config.settings import settings

class JWTError(Exception):
    pass

class JWTExpiredError(JWTError):
    pass

class JWTValidationError(JWTError):
    pass

class JWTHandler:
    def __init__(self) -> None:
        self.secret = settings.jwt_secret_value()
        self.algorithm = settings.security.jwt_algorithm
        self.access_token_minutes = (settings.security.access_token_minutes)
        self.issuer = settings.app.name
        self.audience = "ideez-api"

    def create_access_token(self, user_id: UUID, session_id: UUID, organization_id: Optional[UUID] = None, additional_claims: Optional[Dict[str, Any]] = None,) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.access_token_minutes)
        claims: Dict[str, Any] = {
            "sub": str(user_id),
            "sid": str(session_id),
            "iat": now,
            "exp": expires_at,
            "iss": self.issuer,
            "aud": self.audience,
            "jti": str(uuid4()),
            "token_type": "access",
        }

        if organization_id is not None:
            claims["org"] = str(organization_id)

        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(
            claims,
            self.secret,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str,) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "require": [
                        "sub",
                        "sid",
                        "iat",
                        "exp",
                        "iss",
                        "aud",
                        "jti",
                        "token_type",
                    ]
                },
            )

        except ExpiredSignatureError as exc:
            raise JWTExpiredError("Access token has expired.") from exc

        except InvalidTokenError as exc:
            raise JWTValidationError("Invalid access token.") from exc

        if payload.get("token_type") != "access":
            raise JWTValidationError("Invalid token type.")

        return payload

    def verify_access_token(self, token: str) -> bool:
        try:
            self.decode_access_token(token)
            return True
        except JWTError:
            return False

    def get_subject(self, token: str) -> UUID:
        payload = self.decode_access_token(token)

        try:
            return UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise JWTValidationError("Invalid subject in access token.") from exc

    def get_session_id(self, token: str) -> UUID:
        payload = self.decode_access_token(token)

        try:
            return UUID(payload["sid"])
        except (KeyError, ValueError) as exc:
            raise JWTValidationError("Invalid session ID in access token.") from exc

    def get_organization_id(self, token: str,) -> Optional[UUID]:
        payload = self.decode_access_token(token)
        organization_id = payload.get("org")

        if organization_id is None:
            return None

        try:
            return UUID(organization_id)
        except ValueError as exc:
            raise JWTValidationError("Invalid organization ID in access token.") from exc

    def get_jti(self, token: str) -> str:
        payload = self.decode_access_token(token)

        try:
            return str(payload["jti"])
        except KeyError as exc:
            raise JWTValidationError("Token does not contain a JTI.") from exc

    def is_expired(self, token: str) -> bool:
        try:
            self.decode_access_token(token)
            return False
        except JWTExpiredError:
            return True
        except JWTError:
            return True

__all__ = [
    "JWTError",
    "JWTExpiredError",
    "JWTValidationError",
    "JWTHandler",
]