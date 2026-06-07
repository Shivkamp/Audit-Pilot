from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class NormalizedRecord(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "normalized_records"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("extracted_records.id"),
        nullable=False,
        index=True,
    )
    record_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    normalized_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    normalization_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    normalization_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    normalization_errors: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)