from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class RiskRuleConfig(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "risk_rule_configs"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "rule_key",
            name="uq_risk_rule_configs_workspace_rule_key",
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
        nullable=False,
        index=True,
    )
    rule_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    risk_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    config_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
