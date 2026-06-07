from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ClientCreate(BaseModel):
    name: str
    pan: str | None = None
    gstin: str | None = None
    tan: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    industry: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = None
    pan: str | None = None
    gstin: str | None = None
    tan: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    industry: str | None = None


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    pan: str | None = None
    gstin: str | None = None
    tan: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    industry: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
