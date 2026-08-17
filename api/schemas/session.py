from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class SessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    authentication_method: Optional[str] = Field(default=None, min_length=1, max_length=32)
    authentication_level: Optional[str] = Field(default=None, min_length=1, max_length=32,)
    organization_id: Optional[UUID] = None
    device_id: Optional[UUID] = None

class SessionRefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=1, max_length=4096,)

class SessionRevokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: UUID
    reason: str = Field(default="manual_revocation", min_length=1, max_length=256,)

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    organization_id: Optional[UUID] = None
    device_id: Optional[UUID] = None
    authentication_method: Optional[str] = None
    authentication_level: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_activity_at: Optional[datetime] = None
    expires_at: datetime
    revoked: bool
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None

class SessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    device_id: Optional[UUID] = None
    authentication_method: Optional[str] = None
    authentication_level: Optional[str] = None
    created_at: datetime
    last_activity_at: Optional[datetime] = None
    expires_at: datetime
    revoked: bool

class SessionListResponse(BaseModel):
    sessions: list[SessionSummary]

class SessionRevokeResponse(BaseModel):
    revoked: bool
    session_id: UUID
    message: str

__all__ = [
    "SessionCreateRequest",
    "SessionRefreshRequest",
    "SessionRevokeRequest",
    "SessionResponse",
    "SessionSummary",
    "SessionListResponse",
    "SessionRevokeResponse",
]