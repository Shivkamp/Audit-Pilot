from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.constants import AUTH_TOKEN_TYPE_BEARER
from app.schemas.user import UserResponse


class AuthRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str
    full_name: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Email is required.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.strip()) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return value


class AuthLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Email is required.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password is required.")
        return value


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = AUTH_TOKEN_TYPE_BEARER
    user: UserResponse
