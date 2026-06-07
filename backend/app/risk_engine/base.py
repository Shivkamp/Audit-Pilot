from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.models.normalized_record import NormalizedRecord


@dataclass(slots=True)
class RiskRuleFinding:
    risk_type: str
    severity: str
    title: str
    description: str
    document_id: UUID | None = None
    primary_normalized_record_id: UUID | None = None
    related_normalized_record_ids: list[UUID] | None = None
    risk_data: dict[str, Any] | None = None


@dataclass(slots=True)
class RuleContext:
    workspace_id: UUID
    config_by_rule_key: dict[str, dict[str, Any]]


class BaseRiskRule(ABC):
    rule_key: str = ""
    risk_type: str = ""
    default_severity: str = "HIGH"
    default_is_enabled: bool = True

    def get_rule_config(self, context: RuleContext) -> dict[str, Any]:
        return context.config_by_rule_key.get(self.rule_key, {})

    def is_enabled(self, context: RuleContext) -> bool:
        config = self.get_rule_config(context)
        is_enabled = config.get("is_enabled")
        if is_enabled is None:
            return self.default_is_enabled
        return bool(is_enabled)

    def resolve_severity(self, context: RuleContext) -> str:
        config = self.get_rule_config(context)
        severity = config.get("severity")
        if isinstance(severity, str) and severity:
            return severity
        return self.default_severity

    @abstractmethod
    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        raise NotImplementedError
