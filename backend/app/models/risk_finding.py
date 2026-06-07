from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import RISK_STATUS_OPEN
from app.models.base import Base, TimestampMixin, UUIDMixin


class RiskFinding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "risk_findings"
    __table_args__ = (
        Index("ix_risk_findings_created_at", "created_at"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
        nullable=True,
        index=True,
    )
    primary_normalized_record_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("normalized_records.id"),
        nullable=True,
        index=True,
    )
    related_normalized_record_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    risk_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=RISK_STATUS_OPEN,
        server_default=text("'open'"),
        index=True,
    )
