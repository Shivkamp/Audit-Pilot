from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentEvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    limit: int = Field(default=5, ge=1)
    include_source_trace: bool = True


class AgentEvidenceItem(BaseModel):
    content: str
    score: float
    source_type: str
    source_id: str | None = None
    chunk_type: str
    facts: dict[str, Any]
    citation: dict[str, Any]
    source_trace: dict[str, Any] | None = None


class AgentEvidenceResponse(BaseModel):
    workspace_id: UUID
    query: str | None = None
    risk_type: str | None = None
    limit: int
    evidence: list[AgentEvidenceItem]


class RiskEvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_type: str
    query: str | None = None
    limit: int = Field(default=5, ge=1)
    include_source_trace: bool = True


class FindingContextResponse(BaseModel):
    workspace_id: UUID
    risk_finding: dict[str, Any]
    related_normalized_records: list[dict[str, Any]]
    source_trace: dict[str, Any] | None = None


class SourceTraceResponse(BaseModel):
    workspace_id: UUID
    source_type: str
    source_id: str
    trace: dict[str, Any]
