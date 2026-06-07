from __future__ import annotations

from app.core.constants import (
    NORMALIZED_CATEGORY_TDS_WORKING,
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
    NORMALIZED_CATEGORY_VENDOR_MASTER,
    RISK_RULE_KEY_MISSING_PAN_V1,
    RISK_SEVERITY_HIGH,
    RISK_TYPE_MISSING_PAN,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, is_blank, safe_lower


class MissingPanRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_MISSING_PAN_V1
    risk_type = RISK_TYPE_MISSING_PAN
    default_severity = RISK_SEVERITY_HIGH

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        grouped: dict[str, dict] = {}
        severity = self.resolve_severity(context)
        category_order = (
            NORMALIZED_CATEGORY_VENDOR_MASTER,
            NORMALIZED_CATEGORY_VENDOR_LEDGER,
            NORMALIZED_CATEGORY_TDS_WORKING,
        )

        for category in category_order:
            records = records_by_category.get(category, [])
            for record in records:
                data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

                if category != NORMALIZED_CATEGORY_VENDOR_MASTER and "vendor_pan" not in data:
                    continue

                vendor_code = clean_string(data.get("vendor_code"))
                vendor_name = clean_string(data.get("vendor_name"))
                vendor_pan = data.get("vendor_pan")

                if not vendor_code and not vendor_name:
                    continue

                if not is_blank(vendor_pan):
                    continue

                vendor_key = safe_lower(vendor_code) or safe_lower(vendor_name) or ""
                group = grouped.get(vendor_key)

                if group is None:
                    group = {
                        "vendor_code": vendor_code,
                        "vendor_name": vendor_name,
                        "record_ids": [record.id],
                        "primary_record_id": record.id,
                        "primary_document_id": record.document_id,
                        "primary_category": category,
                    }
                    grouped[vendor_key] = group
                    continue

                if vendor_code and not group["vendor_code"]:
                    group["vendor_code"] = vendor_code
                if vendor_name and not group["vendor_name"]:
                    group["vendor_name"] = vendor_name

                if record.id not in group["record_ids"]:
                    group["record_ids"].append(record.id)

                if (
                    category == NORMALIZED_CATEGORY_VENDOR_MASTER
                    and group["primary_category"] != NORMALIZED_CATEGORY_VENDOR_MASTER
                ):
                    group["primary_record_id"] = record.id
                    group["primary_document_id"] = record.document_id
                    group["primary_category"] = category

        findings: list[RiskRuleFinding] = []
        for group in grouped.values():
            vendor_code = group["vendor_code"]
            vendor_name = group["vendor_name"]
            vendor_label = vendor_code or vendor_name or "unknown_vendor"

            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title=f"Missing PAN for vendor {vendor_label}",
                    description=(
                        "Vendor PAN is missing in normalized records. "
                        f"Vendor: {vendor_name or vendor_code or 'Unknown'}"
                    ),
                    document_id=group["primary_document_id"],
                    primary_normalized_record_id=group["primary_record_id"],
                    related_normalized_record_ids=group["record_ids"],
                    risk_data={
                        "vendor_code": vendor_code,
                        "vendor_name": vendor_name,
                        "related_record_count": len(group["record_ids"]),
                    },
                )
            )

        return findings
