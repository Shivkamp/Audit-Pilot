from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import RiskRuleFinding, RuleContext
from app.risk_engine.rules import (
    DuplicateInvoiceRule,
    HighValueTransactionRule,
    MissingPanRule,
    ShortDepositRule,
    TdsMismatchRule,
    VendorNameMismatchRule,
)


class RiskEngine:
    def __init__(
        self,
        short_deposit_critical_threshold: float,
        *,
        workspace_id: UUID | None = None,
        config_by_rule_key: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self._workspace_id = workspace_id or UUID(int=0)
        self._config_by_rule_key = config_by_rule_key or {}
        self._rules = [
            MissingPanRule(),
            DuplicateInvoiceRule(),
            TdsMismatchRule(),
            ShortDepositRule(critical_threshold=short_deposit_critical_threshold),
            VendorNameMismatchRule(),
            HighValueTransactionRule(),
        ]

    def run(self, records_by_category: dict[str, list[NormalizedRecord]]) -> list[RiskRuleFinding]:
        context = RuleContext(
            workspace_id=self._workspace_id,
            config_by_rule_key=self._config_by_rule_key,
        )

        findings: list[RiskRuleFinding] = []
        for rule in self._rules:
            if not rule.is_enabled(context):
                continue

            findings.extend(rule.run(records_by_category, context))
        return findings
