from __future__ import annotations

from typing import Any

_NORMALIZED_FIELD_LABELS: dict[str, str] = {
    "vendor_code": "Vendor code",
    "vendor_name": "Vendor",
    "vendor_pan": "PAN",
    "supplier_name": "Supplier",
    "supplier_pan": "Supplier PAN",
    "invoice_number": "Invoice",
    "invoice_date": "Invoice date",
    "gross_amount": "Gross amount",
    "amount_paid_or_credited": "Amount paid or credited",
    "tds_section": "Section",
    "tds_rate": "TDS rate",
    "tds_required": "TDS required",
    "tds_deducted": "TDS deducted",
    "deduction_month": "Deduction month",
    "transaction_month": "Transaction month",
    "tds_deposited": "TDS deposited",
    "tax_deposited": "Tax deposited",
    "challan_serial_no": "Challan serial",
    "bsr_code": "BSR code",
    "deposit_date": "Deposit date",
}

_RISK_DATA_FIELD_LABELS: dict[str, str] = {
    "vendor_code": "Vendor code",
    "vendor_name": "Vendor",
    "vendor_pan": "PAN",
    "invoice_number": "Invoice",
    "invoice_date": "Invoice date",
    "deduction_month": "Month",
    "transaction_month": "Transaction month",
    "tds_section": "Section",
    "tds_required": "Expected TDS",
    "tds_deducted": "Actual TDS deducted",
    "expected_tds_deposit": "Expected TDS deposit",
    "actual_tds_deposited": "Actual TDS deposit",
    "tds_deposited": "TDS deposited",
    "shortfall": "Shortfall",
    "gross_amount": "Gross amount",
}



def format_normalized_record_text(record: Any) -> str:
    record_category = _clean_text(_get(record, "record_category")) or "normalized"
    normalized_data = _as_dict(_get(record, "normalized_data"))

    label = record_category.replace("_", " ")
    sentences: list[str] = [f"{label.title()} record."]

    vendor_name = _clean_text(normalized_data.get("vendor_name")) or _clean_text(
        normalized_data.get("supplier_name")
    )
    vendor_pan = _clean_text(normalized_data.get("vendor_pan")) or _clean_text(
        normalized_data.get("supplier_pan")
    )

    vendor_parts: list[str] = []
    if vendor_name:
        vendor_parts.append(f"vendor {vendor_name}")
    if vendor_pan:
        vendor_parts.append(f"PAN {vendor_pan}")
    if vendor_parts:
        sentences.append("For " + ", ".join(vendor_parts) + ".")

    invoice_number = _clean_text(normalized_data.get("invoice_number"))
    invoice_date = _clean_text(normalized_data.get("invoice_date"))
    if invoice_number or invoice_date:
        invoice_phrase = "Invoice"
        if invoice_number:
            invoice_phrase += f" {invoice_number}"
        if invoice_date:
            invoice_phrase += f" dated {invoice_date}"
        sentences.append(invoice_phrase + ".")

    key_facts = _build_fact_pairs(normalized_data, _NORMALIZED_FIELD_LABELS)
    if key_facts:
        sentences.append(" ".join(key_facts))

    return " ".join(sentence.strip() for sentence in sentences if sentence).strip()



def format_risk_finding_text(finding: Any) -> str:
    title = _clean_text(_get(finding, "title")) or "Risk finding"
    description = _clean_text(_get(finding, "description"))
    risk_type = _clean_text(_get(finding, "risk_type"))
    severity = _clean_text(_get(finding, "severity"))
    status = _clean_text(_get(finding, "status"))
    risk_data = _as_dict(_get(finding, "risk_data"))

    sentences: list[str] = [f"Risk finding: {title}."]
    if risk_type:
        sentences.append(f"Risk type {risk_type}.")
    if severity:
        sentences.append(f"Severity {severity}.")
    if status:
        sentences.append(f"Status {status}.")
    if description:
        sentences.append(description.rstrip(".") + ".")

    risk_facts = _build_fact_pairs(risk_data, _RISK_DATA_FIELD_LABELS)
    if risk_facts:
        sentences.append(" ".join(risk_facts))

    return " ".join(sentence.strip() for sentence in sentences if sentence).strip()



def pick_common_knowledge_fields(payload: dict[str, Any]) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for field_name in _NORMALIZED_FIELD_LABELS.keys():
        value = payload.get(field_name)
        if value is None:
            continue

        if isinstance(value, str):
            clean_value = _clean_text(value)
            if clean_value is None:
                continue
            selected[field_name] = clean_value
            continue

        selected[field_name] = value

    return selected



def _build_fact_pairs(payload: dict[str, Any], labels: dict[str, str]) -> list[str]:
    facts: list[str] = []
    for key, label in labels.items():
        if key not in payload:
            continue

        value = payload.get(key)
        formatted = _format_value(key, value)
        if formatted is None:
            continue

        facts.append(f"{label} {formatted}.")

    return facts



def _format_value(key: str, value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        text = _clean_text(value)
        if text is None:
            return None
        if "amount" in key or key in {"tds_required", "tds_deducted", "tds_deposited", "tax_deposited", "shortfall"}:
            return _format_currency(text)
        return text

    if isinstance(value, bool):
        return "yes" if value else "no"

    if isinstance(value, (int, float)):
        if "amount" in key or key in {"tds_required", "tds_deducted", "tds_deposited", "tax_deposited", "shortfall"}:
            return _format_currency(value)
        return str(value)

    return _clean_text(value)



def _format_currency(value: Any) -> str | None:
    if isinstance(value, str):
        text = _clean_text(value)
        if text is None:
            return None
        normalized = text.replace(",", "")
        try:
            parsed = float(normalized)
        except ValueError:
            return text
        return f"INR {parsed:,.2f}".rstrip("0").rstrip(".")

    if isinstance(value, (int, float)):
        return f"INR {float(value):,.2f}".rstrip("0").rstrip(".")

    return _clean_text(value)



def _get(record: Any, key: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)



def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text



def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}
