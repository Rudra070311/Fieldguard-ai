from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PinCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pin: str = Field(min_length=4, max_length=12)
    confirm_pin: str = Field(min_length=4, max_length=12)

    @field_validator("pin", "confirm_pin")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("PIN must contain only digits.")

        return value

    def model_post_init(self) -> None:
        if self.pin != self.confirm_pin:
            raise ValueError("PIN and confirmation PIN do not match.")

class PinVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pin: str = Field(min_length=4, max_length=12)

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("PIN must contain only digits.")

        return value

class PinChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_pin: str = Field(min_length=4, max_length=12)
    new_pin: str = Field(min_length=4, max_length=12)
    confirm_pin: str = Field(min_length=4, max_length=12)

    @field_validator("current_pin", "new_pin", "confirm_pin")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("PIN must contain only digits.")

        return value

    def model_post_init(self) -> None:
        if self.new_pin != self.confirm_pin:
            raise ValueError("PIN and confirmation PIN do not match.")
        if self.current_pin == self.new_pin:
            raise ValueError("New PIN must differ from current PIN.")

class PinRecoveryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recovery_token: str = Field(min_length=1, max_length=4096)
    new_pin: str = Field(min_length=4, max_length=12)
    confirm_pin: str = Field(min_length=4, max_length=12)

    @field_validator("new_pin", "confirm_pin")
    @classmethod
    def validate_pin(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("PIN must contain only digits.")

        return value

    def model_post_init(self) -> None:
        if self.new_pin != self.confirm_pin:
            raise ValueError("PIN and confirmation PIN do not match.")

class PinUnlockRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    recovery_token: str = Field(min_length=1, max_length=4096)

class PinStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    configured: bool
    active: bool
    locked: bool
    locked_until: Optional[datetime] = None
    failed_attempts: int = Field(ge=0)

class PinVerifyResponse(BaseModel):
    verified: bool
    message: str

class PinRecoveryResponse(BaseModel):
    message: str

__all__ = [
    "PinCreateRequest",
    "PinVerifyRequest",
    "PinChangeRequest",
    "PinRecoveryRequest",
    "PinUnlockRequest",
    "PinStatusResponse",
    "PinVerifyResponse",
    "PinRecoveryResponse",
]