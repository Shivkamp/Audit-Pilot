from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import STATUS_ACTIVE
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.document import Document
    from app.models.extracted_record import ExtractedRecord
    from app.models.processing_job import ProcessingJob
    from app.models.workspace_member import WorkspaceMember


class Workspace(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("clients.id"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    financial_year: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=STATUS_ACTIVE,
        server_default=text("'active'"),
    )

    client: Mapped["Client"] = relationship(back_populates="workspaces")
    documents: Mapped[list["Document"]] = relationship(back_populates="workspace")
    processing_jobs: Mapped[list["ProcessingJob"]] = relationship(back_populates="workspace")
    extracted_records: Mapped[list["ExtractedRecord"]] = relationship(back_populates="workspace")
    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace")
