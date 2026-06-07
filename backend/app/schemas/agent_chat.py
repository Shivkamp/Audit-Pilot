from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.config import settings


class AgentChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    include_evidence: bool = True
    include_source_trace: bool = True
    max_evidence: int = Field(default_factory=lambda: int(settings.agent_max_evidence), ge=1, le=20)


class CitationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_type: str | None = None
    source_id: str | None = None
    chunk_id: str | None = None
    document_id: str | None = None
    chunk_type: str | None = None


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: str | None = None
    score: float | None = None
    source_type: str | None = None
    source_id: str | None = None
    chunk_type: str | None = None
    citation: CitationItem | None = None


class SourceTraceItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_type: str | None = None
    source_id: str | None = None
    risk_finding_id: str | None = None


class AgentChatResponse(BaseModel):
    workspace_id: UUID
    message: str
    intent: str
    answer: str
    citations: list[CitationItem]
    evidence: list[EvidenceItem]
    source_traces: list[SourceTraceItem] | None = None
    warnings: list[str]
    confidence: str
    provider: str | None = None
    model: str | None = None
