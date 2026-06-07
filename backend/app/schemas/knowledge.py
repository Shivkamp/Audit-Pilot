from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeIndexRebuildResponse(BaseModel):
    workspace_id: UUID
    total_chunks: int
    normalized_record_chunks: int
    risk_finding_chunks: int
    embedded_chunks: int
    failed_chunks: int


class KnowledgeIndexSummaryResponse(BaseModel):
    workspace_id: UUID
    total_chunks: int
    by_source_type: dict[str, int]
    by_chunk_type: dict[str, int]
    by_embedding_status: dict[str, int]


class KnowledgeSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    limit: int = Field(default=5, ge=1)
    include_retrieval_debug: bool = False


class KnowledgeSearchResult(BaseModel):
    chunk_id: UUID
    score: float
    source_type: str
    source_id: str | None = None
    chunk_type: str
    chunk_text: str
    chunk_metadata: dict[str, Any] | None = None
    retrieval_debug: dict[str, Any] | None = None


class KnowledgeSearchResponse(BaseModel):
    workspace_id: UUID
    query: str
    limit: int
    results: list[KnowledgeSearchResult]


class KnowledgeChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    document_id: UUID | None = None
    source_type: str
    source_id: str | None = None
    chunk_type: str
    chunk_text: str
    chunk_metadata: dict[str, Any] | None = None
    embedding: list[float] | None = None
    embedding_model: str | None = None
    embedding_provider: str | None = None
    embedding_status: str
    embedding_error: str | None = None
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkListResponse(BaseModel):
    workspace_id: UUID
    total_records: int
    limit: int
    offset: int
    chunks: list[KnowledgeChunkResponse]


class KnowledgeIndexDeleteResponse(BaseModel):
    workspace_id: UUID
    deleted_chunks: int
