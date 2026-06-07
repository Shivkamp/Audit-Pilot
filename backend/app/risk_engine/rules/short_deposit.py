from __future__ import annotations

from collections import defaultdict

from app.core.constants import (
    NORMALIZED_CATEGORY_TDS_CHALLAN,
    NORMALIZED_CATEGORY_TDS_WORKING,
    RISK_RULE_KEY_SHORT_DEPOSIT_V1,
    RISK_SEVERITY_CRITICAL,
    RISK_SEVERITY_HIGH,
    RISK_TYPE_SHORT_DEPOSIT,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, make_key, to_decimal


class ShortDepositRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_SHORT_DEPOSIT_V1
    risk_type = RISK_TYPE_SHORT_DEPOSIT
    default_severity = RISK_SEVERITY_HIGH

    def __init__(self, critical_threshold: float) -> None:
        self.critical_threshold = float(critical_threshold)

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        working_records = records_by_category.get(NORMALIZED_CATEGORY_TDS_WORKING, [])
        challan_records = records_by_category.get(NORMALIZED_CATEGORY_TDS_CHALLAN, [])
        config = self.get_rule_config(context)
        config_data = config.get("config_data") or {}

        configured_severity = self.resolve_severity(context)
        critical_threshold = self._resolve_critical_threshold(config, config_data)
        ignore_shortfall_below = self._resolve_ignore_shortfall_below(config_data)

        if not challan_records:
            return []

        expected_totals: dict[tuple[str, ...], float] = defaultdict(float)
        deposited_totals: dict[tuple[str, ...], float] = defaultdict(float)

        working_ids_by_key: dict[tuple[str, ...], list] = defaultdict(list)
        challan_ids_by_key: dict[tuple[str, ...], list] = defaultdict(list)
        key_meta: dict[tuple[str, ...], dict[str, str]] = {}
        primary_working_record_by_key: dict[tuple[str, ...], NormalizedRecord] = {}

        for record in working_records:
            data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

            deduction_month = clean_string(data.get("deduction_month"))
            tds_section = clean_string(data.get("tds_section"))
            tds_deducted = to_decimal(data.get("tds_deducted"))
            tds_required = to_decimal(data.get("tds_required"))
            expected_amount = tds_deducted if tds_deducted is not None else tds_required

            if not deduction_month or not tds_section or expected_amount is None:
                continue

            key = make_key(deduction_month, tds_section)
            expected_totals[key] += expected_amount
            working_ids_by_key[key].append(record.id)
            key_meta.setdefault(
                key,
                {
                    "deduction_month": deduction_month,
                    "tds_section": tds_section,
                },
            )
            primary_working_record_by_key.setdefault(key, record)

        for record in challan_records:
            data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

            deduction_month = clean_string(data.get("deduction_month"))
            tds_section = clean_string(data.get("tds_section"))
            tds_deposited = to_decimal(data.get("tds_deposited"))

            if not deduction_month or not tds_section or tds_deposited is None:
                continue

            key = make_key(deduction_month, tds_section)
            deposited_totals[key] += tds_deposited
            challan_ids_by_key[key].append(record.id)
            key_meta.setdefault(
                key,
                {
                    "deduction_month": deduction_month,
                    "tds_section": tds_section,
                },
            )

        if not deposited_totals:
            return []

        findings: list[RiskRuleFinding] = []
        for key, expected_total in expected_totals.items():
            deposited_total = deposited_totals.get(key, 0.0)

            if deposited_total >= expected_total:
                continue

            shortfall = expected_total - deposited_total
            if ignore_shortfall_below is not None and shortfall < ignore_shortfall_below:
                continue

            severity = (
                RISK_SEVERITY_CRITICAL
                if shortfall >= critical_threshold
                else configured_severity
            )

            primary_record = primary_working_record_by_key.get(key)
            if primary_record is None:
                continue

            related_ids = [
                *working_ids_by_key.get(key, []),
                *challan_ids_by_key.get(key, []),
            ]

            meta = key_meta.get(key, {})
            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title="Short deposit detected",
                    description=(
                        "Deposited TDS is lower than expected TDS when aggregated by "
                        "deduction month and section."
                    ),
                    document_id=primary_record.document_id,
                    primary_normalized_record_id=primary_record.id,
                    related_normalized_record_ids=list(dict.fromkeys(related_ids)),
                    risk_data={
                        "deduction_month": meta.get("deduction_month"),
                        "tds_section": meta.get("tds_section"),
                        "expected_total": expected_total,
                        "deposited_total": deposited_total,
                        "shortfall": shortfall,
                        "critical_threshold_amount": critical_threshold,
                        "ignore_shortfall_below": ignore_shortfall_below,
                    },
                )
            )

        return findings

    def _resolve_critical_threshold(self, config: dict, config_data: dict) -> float:
        configured_threshold = to_decimal(config_data.get("critical_threshold_amount"))
        if configured_threshold is None:
            configured_threshold = to_decimal(config.get("threshold_amount"))

        if configured_threshold is None or configured_threshold < 0:
            return self.critical_threshold

        return float(configured_threshold)

    def _resolve_ignore_shortfall_below(self, config_data: dict) -> float | None:
        ignore_shortfall_below = to_decimal(config_data.get("ignore_shortfall_below"))
        if ignore_shortfall_below is None or ignore_shortfall_below < 0:
            return None

        return float(ignore_shortfall_below)
