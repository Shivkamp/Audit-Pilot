from __future__ import annotations

from app.core.constants import (
    DEFAULT_HIGH_VALUE_TRANSACTION_THRESHOLD,
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
    RISK_RULE_KEY_HIGH_VALUE_TRANSACTION_V1,
    RISK_SEVERITY_MEDIUM,
    RISK_TYPE_HIGH_VALUE_TRANSACTION,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, to_decimal


class HighValueTransactionRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_HIGH_VALUE_TRANSACTION_V1
    risk_type = RISK_TYPE_HIGH_VALUE_TRANSACTION
    default_severity = RISK_SEVERITY_MEDIUM
    default_is_enabled = False

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        config = self.get_rule_config(context)
        config_data = config.get("config_data") or {}

        source_category = (
            clean_string(config_data.get("source_category"))
            or NORMALIZED_CATEGORY_VENDOR_LEDGER
        )
        amount_field = clean_string(config_data.get("amount_field")) or "gross_amount"
        threshold = to_decimal(config.get("threshold_amount"))
        if threshold is None:
            threshold = float(DEFAULT_HIGH_VALUE_TRANSACTION_THRESHOLD)

        severity = self.resolve_severity(context)

        findings: list[RiskRuleFinding] = []
        for record in records_by_category.get(source_category, []):
            data = record.normalized_data if isinstance(record.normalized_data, dict) else {}
            amount = to_decimal(data.get(amount_field))
            if amount is None or amount < threshold:
                continue

            vendor_code = clean_string(data.get("vendor_code"))
            vendor_name = clean_string(data.get("vendor_name"))
            invoice_number = clean_string(data.get("invoice_number"))

            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title="High value transaction detected",
                    description=(
                        "Transaction amount meets or exceeds the configured high-value "
                        "threshold."
                    ),
                    document_id=record.document_id,
                    primary_normalized_record_id=record.id,
                    related_normalized_record_ids=[record.id],
                    risk_data={
                        "source_category": source_category,
                        "amount_field": amount_field,
                        "amount": amount,
                        "threshold_amount": threshold,
                        "vendor_code": vendor_code,
                        "vendor_name": vendor_name,
                        "invoice_number": invoice_number,
                    },
                )
            )

        return findings
