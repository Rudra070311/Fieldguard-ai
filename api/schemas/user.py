from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    full_name: str = Field(min_length=1, max_length=256)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password cannot start or end with whitespace.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number.")

        return value

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = " ".join(value.split())

        if not value:
            raise ValueError("Full name cannot be empty.")

        return value

class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=256,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = " ".join(value.split())

        if not value:
            raise ValueError("Full name cannot be empty.")

        return value


class UserPasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password cannot start or end with whitespace.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number.")

        return value

class UserPasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=1, max_length=4096)
    new_password: str = Field(min_length=8, max_length=256)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if value.strip() != value:
            raise ValueError("Password cannot start or end with whitespace.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number.")

        return value

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    full_name: str
    email_verified: bool
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    full_name: str
    active: bool

__all__ = [
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserPasswordChangeRequest",
    "UserPasswordResetRequest",
    "UserResponse",
    "UserSummary",
]