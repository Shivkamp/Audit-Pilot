from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RiskRuleConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    rule_key: str
    risk_type: str
    is_enabled: bool
    severity: str
    threshold_amount: float | None = None
    threshold_percent: float | None = None
    config_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class RiskRuleConfigInitializeResponse(BaseModel):
    workspace_id: UUID
    created_count: int
    existing_count: int
    total_configs: int


class RiskRuleConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_enabled: bool | None = None
    severity: str | None = None
    threshold_amount: float | None = None
    threshold_percent: float | None = None
    config_data: dict[str, Any] | None = None


class RiskRuleConfigBulkUpdateItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_key: str
    is_enabled: bool | None = None
    severity: str | None = None
    threshold_amount: float | None = None
    threshold_percent: float | None = None
    config_data: dict[str, Any] | None = None


class RiskRuleConfigBulkUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    configs: list[RiskRuleConfigBulkUpdateItem]


class RiskRuleConfigListResponse(BaseModel):
    workspace_id: UUID
    total_records: int
    limit: int
    offset: int
    configs: list[RiskRuleConfigResponse]


class RiskRuleConfigResetResponse(BaseModel):
    workspace_id: UUID
    total_configs: int
