from __future__ import annotations

from app.core.constants import (
    NORMALIZED_CATEGORY_TDS_WORKING,
    RISK_RULE_KEY_TDS_MISMATCH_V1,
    RISK_SEVERITY_HIGH,
    RISK_TYPE_TDS_MISMATCH,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, to_decimal


class TdsMismatchRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_TDS_MISMATCH_V1
    risk_type = RISK_TYPE_TDS_MISMATCH
    default_severity = RISK_SEVERITY_HIGH

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        working_records = records_by_category.get(NORMALIZED_CATEGORY_TDS_WORKING, [])
        config = self.get_rule_config(context)
        config_data = config.get("config_data") or {}
        severity = self.resolve_severity(context)

        ignore_shortfall_below = to_decimal(config_data.get("ignore_shortfall_below"))
        if ignore_shortfall_below is None:
            ignore_shortfall_below = to_decimal(config.get("threshold_amount"))
        if ignore_shortfall_below is None or ignore_shortfall_below < 0:
            ignore_shortfall_below = 0.0

        findings: list[RiskRuleFinding] = []
        for record in working_records:
            data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

            tds_required = to_decimal(data.get("tds_required"))
            tds_deducted = to_decimal(data.get("tds_deducted"))

            if tds_required is None or tds_deducted is None:
                continue

            shortfall = tds_required - tds_deducted
            if shortfall <= 0:
                continue
            if shortfall < ignore_shortfall_below:
                continue

            vendor_code = clean_string(data.get("vendor_code"))
            vendor_name = clean_string(data.get("vendor_name"))
            invoice_number = clean_string(data.get("invoice_number"))
            section = clean_string(data.get("tds_section"))

            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title="TDS mismatch detected",
                    description=(
                        "TDS deducted is lower than TDS required as per normalized "
                        "TDS working records."
                    ),
                    document_id=record.document_id,
                    primary_normalized_record_id=record.id,
                    related_normalized_record_ids=[record.id],
                    risk_data={
                        "vendor_code": vendor_code,
                        "vendor_name": vendor_name,
                        "invoice_number": invoice_number,
                        "tds_section": section,
                        "tds_required": tds_required,
                        "tds_deducted": tds_deducted,
                        "shortfall": shortfall,
                        "ignore_shortfall_below": ignore_shortfall_below,
                    },
                )
            )

        return findings
