from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import UUID

class NotificationType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    OTP = "otp"
    MAGIC_LINK = "magic_link"
    PASSWORD_CHANGED = "password_changed"
    PIN_CHANGED = "pin_changed"
    DEVICE_REGISTERED = "device_registered"
    DEVICE_REVOKED = "device_revoked"
    SECURITY_ALERT = "security_alert"
    LOGIN_ALERT = "login_alert"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

@dataclass(frozen=True)
class NotificationEvent:
    type: NotificationType
    user_id: UUID
    channel: NotificationChannel
    destination: str
    data: Mapping[str, Any] = field(default_factory=dict)
    request_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None