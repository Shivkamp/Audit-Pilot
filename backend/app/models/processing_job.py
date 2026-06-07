from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import JOB_STATUS_PENDING, JOB_TYPE_DOCUMENT_PROCESSING
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.workspace import Workspace


class ProcessingJob(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "processing_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )
    job_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=JOB_TYPE_DOCUMENT_PROCESSING,
        server_default=text("'document_processing'"),
    )
    status: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=JOB_STATUS_PENDING,
        server_default=text("'pending'"),
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    current_step: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    document: Mapped["Document"] = relationship(back_populates="processing_jobs")
    workspace: Mapped["Workspace"] = relationship(back_populates="processing_jobs")
