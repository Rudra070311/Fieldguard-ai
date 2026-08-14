from __future__ import annotations
from enum import StrEnum

class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"

class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAction(StrEnum):
    ALLOW = "allow"
    VERIFY_DEVICE = "verify_trusted_device"
    REQUIRE_OTP_PIN = "require_OTP_and_PIN"
    BLOCK = "block"
    ESCALATE = "escalate_to_human"

class AuthenticationMethod(StrEnum):
    PASSWORD = "password"
    PIN = "pin"
    OTP = "otp"
    MAGIC_LINK = "magic_link"
    FACIAL = "facial"
    REFRESH_TOKEN = "refresh_token"

class AuthenticationLevel(StrEnum):
    PASSWORD = "password"
    PIN = "pin"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    REFRESH = "refresh"

class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    MAGIC_LINK = "magic_link"
    OTP = "otp"

class DeviceStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    REMEMBERED = "remembered"

class OTPChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"

class OTPPurpose(StrEnum):
    LOGIN = "login"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    PIN_RECOVERY = "pin_recovery"
    DEVICE_VERIFICATION = "device_verification"

class AuditEvent(StrEnum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_REVOKED = "session_revoked"
    DEVICE_REGISTERED = "device_registered"
    DEVICE_REVOKED = "device_revoked"
    DEVICE_RESTORED = "device_restored"
    PIN_CREATED = "pin_created"
    PIN_CHANGED = "pin_changed"
    PIN_VERIFIED = "pin_verified"
    PIN_FAILED = "pin_failed"
    PIN_LOCKED = "pin_locked"
    OTP_CREATED = "otp_created"
    OTP_VERIFIED = "otp_verified"
    OTP_FAILED = "otp_failed"
    MAGIC_LINK_CREATED = "magic_link_created"
    MAGIC_LINK_VERIFIED = "magic_link_verified"
    EMAIL_VERIFIED = "email_verified"
    RISK_DETECTED = "risk_detected"

DEFAULT_ACCESS_TOKEN_TYPE = TokenType.ACCESS
DEFAULT_REFRESH_TOKEN_TYPE = TokenType.REFRESH
DEFAULT_JWT_ISSUER = "iDeez"
DEFAULT_JWT_AUDIENCE = "ideez-api"
DEFAULT_EMBEDDING_VERSION = "v1"
DEFAULT_POLICY_VERSION = "v1"
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 256
MIN_PIN_LENGTH = 4
MAX_PIN_LENGTH = 12
MAX_USER_AGENT_LENGTH = 512
MAX_IP_ADDRESS_LENGTH = 45
DEFAULT_RISK_SCORE = 0.0
MAX_RISK_SCORE = 1.0