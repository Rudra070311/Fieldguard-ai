import sys
from pathlib import Path
from typing import List, Optional
from pydantic import Field, SecretStr, field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class AppConfig(BaseSettings):
    name: str = Field("AuthService", description="Application name")
    version: str = Field("1.0.0", description="Semantic version")
    environment: str = Field("development", description="Environment: development/staging/production")
    debug: bool = Field(False, description="Enable debug mode (verbose error responses)")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "test"}
        if v not in allowed:
            raise ValueError(f"Invalid environment '{v}'. Allowed: {', '.join(allowed)}")
        return v

class DatabaseConfig(BaseSettings):
    url: SecretStr = Field(..., description="PostgreSQL DSN (e.g., postgresql://user:pass@localhost/db)")
    pool_size: int = Field(10, ge=1, le=100, description="Maximum connection pool size")
    timeout_seconds: int = Field(30, ge=1, description="Connection acquisition timeout")
    echo_sql: bool = Field(False, description="Echo SQL statements to logs (development only)")

class SecurityConfig(BaseSettings):
    jwt_secret: SecretStr = Field(..., description="HMAC secret for JWT signing")
    jwt_algorithm: str = Field("HS256", description="JWT signing algorithm (HS256, RS256, etc.)")
    access_token_minutes: int = Field(15, ge=1, description="Access token validity (minutes)")
    refresh_token_days: int = Field(7, ge=1, description="Refresh token validity (days)")
    encryption_key: SecretStr = Field(..., description="AES key for encrypting sensitive fields")
    pin_hash_rounds: int = Field(12, ge=4, le=31, description="bcrypt/Argon2 cost factor")
    cors_origins: List[str] = Field(["http://localhost:3000"], description="Allowed CORS origins")

class AuthConfig(BaseSettings):
    otp_length: int = Field(6, ge=4, le=10, description="Numeric OTP length")
    otp_expiry_minutes: int = Field(5, ge=1, description="OTP validity")
    magic_link_expiry_minutes: int = Field(15, ge=1, description="Magic link token validity")
    max_failed_attempts: int = Field(5, ge=1, description="Failed login attempts before lockout")
    account_lock_minutes: int = Field(30, ge=1, description="Lockout duration after max attempts")

class AIConfig(BaseSettings):
    embedding_model: str = Field("all-MiniLM-L6-v2", description="Embedding model name or HF ID")
    embedding_version: int = Field(1, description="Embedding version to support migrations")
    face_match_threshold: float = Field(0.75, ge=0.0, le=1.0, description="Face similarity threshold")
    liveness_threshold: float = Field(0.60, ge=0.0, le=1.0, description="Liveness score threshold")
    flaw_enabled: bool = Field(False, description="Enable Flaw reasoning engine")
    flaw_endpoint: Optional[str] = Field(None, description="Flaw gRPC/REST endpoint URL")
    reasoning_enabled: bool = Field(False, description="Enable explainable AI reasoning output")

class DevicesConfig(BaseSettings):
    trust_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Score to consider device trusted")
    remember_days: int = Field(90, ge=1, description="How long to remember a trusted device")
    max_devices: int = Field(10, ge=1, description="Maximum devices per user")

class RateLimitsConfig(BaseSettings):
    login_per_minute: int = Field(30, ge=1, description="Login attempts per minute per IP")
    otp_per_hour: int = Field(10, ge=1, description="OTP requests per hour per phone/email")
    api_per_minute: int = Field(120, ge=1, description="General API requests per minute")
    email_per_hour: int = Field(50, ge=1, description="Transactional emails per hour per user")

class EmailConfig(BaseSettings):
    smtp_host: Optional[str] = Field(None, description="SMTP server hostname")
    smtp_port: int = Field(587, ge=1, le=65535, description="SMTP port")
    username: Optional[str] = Field(None, description="SMTP username")
    password: Optional[SecretStr] = Field(None, description="SMTP password")
    sender: str = Field("noreply@authservice.com", description="Default sender email")
    use_tls: bool = Field(True, description="Use STARTTLS")

class LoggingConfig(BaseSettings):
    level: str = Field("INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    json_logs: bool = Field(False, description="Output logs as JSON (for production)")
    audit_enabled: bool = Field(True, description="Log audit events (login, password change, etc.)")

class FeatureFlagsConfig(BaseSettings):
    biometrics: bool = Field(False, description="Enable biometric authentication (face/fingerprint)")
    fingerprint: bool = Field(True, description="Enable device fingerprinting")
    vpn_detection: bool = Field(False, description="Detect VPN/proxy usage")
    anomaly_detection: bool = Field(False, description="Enable ML-based anomaly detection")
    flaw_reasoning: bool = Field(False, description="Enable Flaw reasoning UI/API")
    experimental: bool = Field(False, description="Unstable experimental features")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    devices: DevicesConfig = Field(default_factory=DevicesConfig)
    rate_limits: RateLimitsConfig = Field(default_factory=RateLimitsConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    features: FeatureFlagsConfig = Field(default_factory=FeatureFlagsConfig)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.app.environment == "production" and self.app.debug:
            print("WARNING: Debug mode is enabled in production!", file=sys.stderr)

    def database_url(self) -> str:
        return self.database.url.get_secret_value()

    def jwt_secret_value(self) -> str:
        return self.security.jwt_secret.get_secret_value()

    def encryption_key_value(self) -> str:
        return self.security.encryption_key.get_secret_value()

settings = Settings()