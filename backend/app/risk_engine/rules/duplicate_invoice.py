from __future__ import annotations

from app.core.constants import (
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
    RISK_RULE_KEY_DUPLICATE_INVOICE_V1,
    RISK_SEVERITY_HIGH,
    RISK_TYPE_DUPLICATE_INVOICE,
)
from app.models.normalized_record import NormalizedRecord
from app.risk_engine.base import BaseRiskRule, RiskRuleFinding, RuleContext
from app.risk_engine.utils import clean_string, make_key, to_decimal


class DuplicateInvoiceRule(BaseRiskRule):
    rule_key = RISK_RULE_KEY_DUPLICATE_INVOICE_V1
    risk_type = RISK_TYPE_DUPLICATE_INVOICE
    default_severity = RISK_SEVERITY_HIGH

    def run(
        self,
        records_by_category: dict[str, list[NormalizedRecord]],
        context: RuleContext,
    ) -> list[RiskRuleFinding]:
        ledger_records = records_by_category.get(NORMALIZED_CATEGORY_VENDOR_LEDGER, [])
        config_data = self.get_rule_config(context).get("config_data") or {}
        severity = self.resolve_severity(context)

        match_on_vendor = bool(config_data.get("match_on_vendor", True))
        match_on_invoice_number = bool(config_data.get("match_on_invoice_number", True))
        match_on_invoice_date = bool(config_data.get("match_on_invoice_date", True))
        match_on_gross_amount = bool(config_data.get("match_on_gross_amount", True))

        if not any(
            (
                match_on_vendor,
                match_on_invoice_number,
                match_on_invoice_date,
                match_on_gross_amount,
            )
        ):
            match_on_vendor = True
            match_on_invoice_number = True
            match_on_invoice_date = True
            match_on_gross_amount = True

        grouped: dict[tuple[str, ...], list[NormalizedRecord]] = {}
        grouping_details: dict[tuple[str, ...], dict] = {}

        for record in ledger_records:
            data = record.normalized_data if isinstance(record.normalized_data, dict) else {}

            invoice_number = clean_string(data.get("invoice_number"))
            if not invoice_number:
                continue

            vendor_code = clean_string(data.get("vendor_code"))
            vendor_name = clean_string(data.get("vendor_name"))
            vendor_identity = vendor_code or vendor_name
            if not vendor_identity:
                continue

            invoice_date = clean_string(data.get("invoice_date"))
            gross_amount = to_decimal(data.get("gross_amount"))

            key_parts: list = []
            if match_on_vendor:
                key_parts.append(vendor_identity)
            if match_on_invoice_number:
                key_parts.append(invoice_number)
            if match_on_invoice_date:
                key_parts.append(invoice_date)
            if match_on_gross_amount:
                key_parts.append(gross_amount)

            key = make_key(*key_parts)
            grouped.setdefault(key, []).append(record)
            grouping_details.setdefault(
                key,
                {
                    "vendor_code": vendor_code,
                    "vendor_name": vendor_name,
                    "invoice_number": invoice_number,
                    "invoice_date": invoice_date,
                    "gross_amount": gross_amount,
                },
            )

        findings: list[RiskRuleFinding] = []
        for key, group_records in grouped.items():
            if len(group_records) <= 1:
                continue

            details = grouping_details[key]
            primary_record = group_records[0]
            related_ids = [record.id for record in group_records]

            findings.append(
                RiskRuleFinding(
                    risk_type=self.risk_type,
                    severity=severity,
                    title=f"Duplicate invoice detected: {details['invoice_number']}",
                    description=(
                        "Multiple normalized vendor ledger records share the same "
                        "vendor, invoice number, invoice date, and gross amount."
                    ),
                    document_id=primary_record.document_id,
                    primary_normalized_record_id=primary_record.id,
                    related_normalized_record_ids=related_ids,
                    risk_data={
                        "vendor_code": details["vendor_code"],
                        "vendor_name": details["vendor_name"],
                        "invoice_number": details["invoice_number"],
                        "invoice_date": details["invoice_date"],
                        "gross_amount": details["gross_amount"],
                        "duplicate_count": len(group_records),
                    },
                )
            )

        return findings
