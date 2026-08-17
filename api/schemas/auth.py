from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: Optional[str] = Field(default=None, min_length=1)
    otp: Optional[str] = Field(default=None, min_length=4, max_length=10)
    pin: Optional[str] = Field(default=None, min_length=4, max_length=32)
    device_id: Optional[UUID] = None
    remember_device: bool = False

class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    session_id: UUID
    user_id: UUID
    organization_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    action: Optional[str] = None

class TokenRefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=1)

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime
    session_id: UUID

class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: Optional[str] = None
    session_id: Optional[UUID] = None
    all_sessions: bool = False

class LogoutResponse(BaseModel):
    success: bool
    message: str

class EmailVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=1)

class EmailVerificationResponse(BaseModel):
    success: bool
    user_id: UUID
    email: EmailStr
    message: str

class ResendVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr

class OTPRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str = Field(min_length=1, max_length=320)
    purpose: str = Field(min_length=1, max_length=64)
    channel: str = Field(min_length=1, max_length=32)

class OTPVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: UUID
    code: str = Field(min_length=4, max_length=10)
    purpose: str = Field(min_length=1, max_length=64)

class OTPResponse(BaseModel):
    success: bool
    message: str
    expires_at: Optional[datetime] = None

class MagicLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    purpose: str = Field(min_length=1, max_length=64)

class MagicLinkVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=1)
    purpose: str = Field(min_length=1, max_length=64)

class MagicLinkResponse(BaseModel):
    success: bool
    message: str

class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=256)

class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=256)

class AuthErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "TokenRefreshRequest",
    "TokenRefreshResponse",
    "LogoutRequest",
    "LogoutResponse",
    "EmailVerificationRequest",
    "EmailVerificationResponse",
    "ResendVerificationRequest",
    "OTPRequest",
    "OTPVerifyRequest",
    "OTPResponse",
    "MagicLinkRequest",
    "MagicLinkVerifyRequest",
    "MagicLinkResponse",
    "PasswordChangeRequest",
    "PasswordResetRequest",
    "PasswordResetConfirmRequest",
    "AuthErrorResponse",
]