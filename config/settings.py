from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class AppConfig(BaseSettings):
    name: str = Field("AuthService")
    version: str = Field("1.0.0")
    environment: str = Field("development")
    debug: bool = Field(False)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "staging", "production", "test"}

        if value not in allowed:
            raise ValueError(
                f"Invalid environment '{value}'. "
                f"Allowed: {', '.join(sorted(allowed))}"
            )

        return value

class DatabaseConfig(BaseSettings):
    url: SecretStr = Field(...)
    pool_size: int = Field(10, ge=1, le=100)
    timeout_seconds: int = Field(30, ge=1)
    echo_sql: bool = Field(False)

class SecurityConfig(BaseSettings):
    jwt_secret: SecretStr = Field(...)
    jwt_algorithm: str = Field("HS256")
    access_token_minutes: int = Field(15, ge=1)
    refresh_token_days: int = Field(7, ge=1)
    encryption_key: SecretStr = Field(...)
    pin_hash_rounds: int = Field(12, ge=4, le=31)
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

class AuthConfig(BaseSettings):
    otp_length: int = Field(6, ge=4, le=10)
    otp_expiry_minutes: int = Field(5, ge=1)
    magic_link_expiry_minutes: int = Field(15, ge=1)
    max_failed_attempts: int = Field(5, ge=1)
    account_lock_minutes: int = Field(30, ge=1)
    pin_length: int = Field(6, ge=4, le=12)

class AIConfig(BaseSettings):
    embedding_model: str = Field("all-MiniLM-L6-v2")
    embedding_version: int = Field(1, ge=1)
    face_match_threshold: float = Field(0.75, ge=0.0, le=1.0)
    liveness_threshold: float = Field(0.60, ge=0.0, le=1.0)
    flaw_enabled: bool = Field(False)
    flaw_endpoint: Optional[str] = Field(None)
    reasoning_enabled: bool = Field(False)

class DevicesConfig(BaseSettings):
    trust_threshold: float = Field(0.85, ge=0.0, le=1.0)
    remember_days: int = Field(90, ge=1)
    max_devices: int = Field(10, ge=1)

class RateLimitsConfig(BaseSettings):
    login_per_minute: int = Field(30, ge=1)
    otp_per_hour: int = Field(10, ge=1)
    api_per_minute: int = Field(120, ge=1)
    email_per_hour: int = Field(50, ge=1)

class EmailConfig(BaseSettings):
    smtp_host: Optional[str] = Field(None)
    smtp_port: int = Field(587, ge=1, le=65535)
    username: Optional[str] = Field(None)
    password: Optional[SecretStr] = Field(None)
    sender: str = Field("noreply@authservice.com")
    use_tls: bool = Field(True)

class LoggingConfig(BaseSettings):
    level: str = Field("INFO")
    json_logs: bool = Field(False)
    audit_enabled: bool = Field(True)

class FeatureFlagsConfig(BaseSettings):
    biometrics: bool = Field(False)
    fingerprint: bool = Field(True)
    vpn_detection: bool = Field(False)
    anomaly_detection: bool = Field(False)
    flaw_reasoning: bool = Field(False)
    experimental: bool = Field(False)

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