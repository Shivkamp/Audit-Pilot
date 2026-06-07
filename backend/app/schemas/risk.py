from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RiskFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID | None = None
    primary_normalized_record_id: UUID | None = None
    related_normalized_record_ids: list[str] | None = None
    risk_type: str
    severity: str
    title: str
    description: str
    risk_data: dict[str, Any] | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class RiskFindingListResponse(BaseModel):
    workspace_id: UUID | None = None
    document_id: UUID | None = None
    total_records: int
    limit: int
    offset: int
    findings: list[RiskFindingResponse]


class RiskSummaryResponse(BaseModel):
    workspace_id: UUID
    total_findings: int
    counts_by_status: dict[str, int]
    counts_by_severity: dict[str, int]
    counts_by_risk_type: dict[str, int]


class RiskRunResponse(BaseModel):
    workspace_id: UUID
    total_findings: int
    summary: RiskSummaryResponse


class RiskFindingStatusUpdate(BaseModel):
    status: str
