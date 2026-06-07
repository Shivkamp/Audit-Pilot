from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.constants import ALLOWED_WORKSPACE_MEMBER_ROLES
from app.schemas.user import UserResponse


class WorkspaceMemberCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    role: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned:
            raise ValueError("Email is required.")
        return cleaned

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_WORKSPACE_MEMBER_ROLES:
            raise ValueError("Invalid workspace member role.")
        return cleaned


class WorkspaceMemberUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_WORKSPACE_MEMBER_ROLES:
            raise ValueError("Invalid workspace member role.")
        return cleaned


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime
    user: UserResponse | None = None


class WorkspaceMyMembershipResponse(BaseModel):
    workspace_id: UUID
    user_id: UUID
    role: str
    permissions: dict[str, bool]
