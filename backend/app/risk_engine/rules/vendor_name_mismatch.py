from __future__ import annotations

from collections import defaultdict

from app.core.constants import (
    NORMALIZED_CATEGORY_TDS_WORKING,
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
    NORMALIZED_CATEGORY_VENDOR_MASTER,
    RISK_RULE_KEY_VENDOR_NAME_MISMATCH_V1,
    RISK_SEVERITY_MEDIUM,
    RISK_TYPE_VENDOR_NAME_MISMATCH,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, normalize_vendor_name, safe_lower


class VendorNameMismatchRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_VENDOR_NAME_MISMATCH_V1
    risk_type = RISK_TYPE_VENDOR_NAME_MISMATCH
    default_severity = RISK_SEVERITY_MEDIUM

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        categories = (
            NORMALIZED_CATEGORY_VENDOR_MASTER,
            NORMALIZED_CATEGORY_VENDOR_LEDGER,
            NORMALIZED_CATEGORY_TDS_WORKING,
        )
        severity = self.resolve_severity(context)

        names_by_code: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        record_ids_by_code: dict[str, list] = defaultdict(list)
        primary_record_by_code: dict[str, NormalizedRecord] = {}
        display_vendor_code: dict[str, str] = {}

        for category in categories:
            for record in records_by_category.get(category, []):
                data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

                vendor_code = clean_string(data.get("vendor_code"))
                vendor_name = clean_string(data.get("vendor_name"))
                normalized_name = normalize_vendor_name(vendor_name)

                if not vendor_code or not vendor_name or not normalized_name:
                    continue

                code_key = safe_lower(vendor_code)
                if code_key is None:
                    continue

                names_by_code[code_key][normalized_name].add(vendor_name)
                record_ids_by_code[code_key].append(record.id)
                primary_record_by_code.setdefault(code_key, record)
                display_vendor_code.setdefault(code_key, vendor_code)

        findings: list[RiskRuleFinding] = []
        for code_key, normalized_name_map in names_by_code.items():
            if len(normalized_name_map) <= 1:
                continue

            primary_record = primary_record_by_code.get(code_key)
            if primary_record is None:
                continue

            observed_names: list[str] = []
            for original_name_set in normalized_name_map.values():
                observed_names.extend(original_name_set)

            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title=(
                        "Vendor name mismatch detected for vendor code "
                        f"{display_vendor_code.get(code_key, code_key)}"
                    ),
                    description=(
                        "Multiple normalized vendor names were observed for the same "
                        "vendor code across normalized records."
                    ),
                    document_id=primary_record.document_id,
                    primary_normalized_record_id=primary_record.id,
                    related_normalized_record_ids=list(dict.fromkeys(record_ids_by_code[code_key])),
                    risk_data={
                        "vendor_code": display_vendor_code.get(code_key),
                        "observed_names": sorted(set(observed_names)),
                    },
                )
            )

        return findings
