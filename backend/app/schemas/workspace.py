from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None
    financial_year: str


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    financial_year: str | None = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    name: str
    description: str | None = None
    financial_year: str
    status: str
    created_at: datetime
    updated_at: datetime
