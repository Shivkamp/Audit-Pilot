from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    DOCUMENT_STATUS_UPLOADED,
    DOCUMENT_TYPE_UNKNOWN,
    DOCUMENT_UPLOAD_SOURCE_MANUAL,
)
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.extracted_record import ExtractedRecord
    from app.models.processing_job import ProcessingJob
    from app.models.workspace import Workspace


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(16), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_backend: Mapped[str] = mapped_column(String(20), nullable=False)
    storage_bucket: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DOCUMENT_TYPE_UNKNOWN,
        server_default=text("'unknown'"),
    )
    classification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    classification_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    classification_reason: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    classified_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=DOCUMENT_STATUS_UPLOADED,
        server_default=text("'uploaded'"),
    )
    upload_source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=DOCUMENT_UPLOAD_SOURCE_MANUAL,
        server_default=text("'manual'"),
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="documents")
    processing_jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="document")
    extracted_records: Mapped[list["ExtractedRecord"]] = relationship(back_populates="document")