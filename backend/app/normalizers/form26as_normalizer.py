from __future__ import annotations

import re
from typing import Any

from app.core.constants import (
    EXTRACTION_RECORD_TYPE_METADATA,
    EXTRACTION_RECORD_TYPE_TEXT,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_SKIPPED,
    NORMALIZED_CATEGORY_FORM_26AS,
)
from app.normalizers.base import BaseNormalizer, NormalizedItem
from app.normalizers.common import (
    build_error,
    clean_string,
    get_record_raw_data,
    get_record_raw_text,
    get_record_value,
    get_value,
    parse_date,
    parse_decimal,
    parse_month,
)
from app.normalizers.field_aliases import (
    AMOUNT_PAID_OR_CREDITED_ALIASES,
    ASSESSEE_PAN_ALIASES,
    BSR_CODE_ALIASES,
    CHALLAN_SERIAL_NO_ALIASES,
    DEDUCTOR_NAME_ALIASES,
    DEDUCTOR_TAN_ALIASES,
    DEPOSIT_DATE_ALIASES,
    TDS_DEPOSITED_ALIASES,
    TDS_SECTION_ALIASES,
)

_TEXT_PATTERNS = {
    "assessee_name": r"(?im)^\s*assessee\s*(?:name)?\s*[:\-]\s*(.+)$",
    "assessee_pan": r"(?im)^\s*assessee\s*pan\s*[:\-]\s*([A-Z0-9]+)",
    "deductor_tan": r"(?im)^\s*(?:deductor\s*tan|tan)\s*[:\-]\s*([A-Z0-9]+)",
    "deductor_name": r"(?im)^\s*deductor\s*(?:name)?\s*[:\-]\s*(.+)$",
    "tds_section": r"(?im)^\s*(?:tds\s*section|section)\s*[:\-]\s*([A-Za-z0-9]+)",
    "transaction_month": (
        r"(?im)^\s*(?:transaction\s*month|month|period)\s*[:\-]\s*([A-Za-z]{3,9}[-\s]\d{4}|\d{4}[-/]\d{1,2}|\d{1,2}[-/]\d{4})"
    ),
    "amount_paid_or_credited": (
        r"(?im)^\s*(?:amount\s*paid(?:\s*or\s*credited)?|amount\s*credited)\s*[:\-]\s*([\(\)\d,\.₹\sA-Za-z-]+)$"
    ),
    "tax_deposited": (
        r"(?im)^\s*(?:tax\s*deposited|tds\s*deposited)\s*[:\-]\s*([\(\)\d,\.₹\sA-Za-z-]+)$"
    ),
    "challan_serial_no": (
        r"(?im)^\s*challan\s*(?:serial\s*)?(?:no\.?|number)?\s*[:\-]\s*([A-Z0-9\-/]+)"
    ),
    "bsr_code": r"(?im)^\s*bsr\s*code\s*[:\-]\s*([A-Z0-9\-/]+)",
}


class Form26ASNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)
        raw_text = get_record_raw_text(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA and not raw_text:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_FORM_26AS,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        text_mode = False
        text_values: dict[str, str | None] = {}
        if not raw_data and raw_text and record_type == EXTRACTION_RECORD_TYPE_TEXT:
            text_mode = True
            text_values = self._extract_from_text(raw_text)

        if raw_data:
            assessee_name = clean_string(get_value(raw_data, ("assessee_name", "taxpayer_name")))
            assessee_pan = clean_string(get_value(raw_data, ASSESSEE_PAN_ALIASES))
            deductor_tan = clean_string(get_value(raw_data, DEDUCTOR_TAN_ALIASES))
            deductor_name = clean_string(get_value(raw_data, DEDUCTOR_NAME_ALIASES))
            tds_section = clean_string(get_value(raw_data, TDS_SECTION_ALIASES))

            transaction_month_raw = get_value(
                raw_data,
                ("transaction_month", "deduction_month", "month", "period"),
            )
            transaction_month = parse_month(transaction_month_raw)

            amount_paid_or_credited_raw = get_value(raw_data, AMOUNT_PAID_OR_CREDITED_ALIASES)
            amount_paid_or_credited = parse_decimal(amount_paid_or_credited_raw)

            tax_deposited_raw = get_value(raw_data, TDS_DEPOSITED_ALIASES)
            tax_deposited = parse_decimal(tax_deposited_raw)

            deposit_date_raw = get_value(raw_data, DEPOSIT_DATE_ALIASES)
            deposit_date = parse_date(deposit_date_raw)

            challan_serial_no = clean_string(get_value(raw_data, CHALLAN_SERIAL_NO_ALIASES))
            bsr_code = clean_string(get_value(raw_data, BSR_CODE_ALIASES))
        else:
            assessee_name = clean_string(text_values.get("assessee_name"))
            assessee_pan = clean_string(text_values.get("assessee_pan"))
            deductor_tan = clean_string(text_values.get("deductor_tan"))
            deductor_name = clean_string(text_values.get("deductor_name"))
            tds_section = clean_string(text_values.get("tds_section"))
            transaction_month_raw = text_values.get("transaction_month")
            transaction_month = parse_month(transaction_month_raw)
            amount_paid_or_credited_raw = text_values.get("amount_paid_or_credited")
            amount_paid_or_credited = parse_decimal(amount_paid_or_credited_raw)
            tax_deposited_raw = text_values.get("tax_deposited")
            tax_deposited = parse_decimal(tax_deposited_raw)
            deposit_date_raw = text_values.get("deposit_date")
            deposit_date = parse_date(deposit_date_raw)
            challan_serial_no = clean_string(text_values.get("challan_serial_no"))
            bsr_code = clean_string(text_values.get("bsr_code"))

        normalized_data = {
            "assessee_name": assessee_name,
            "assessee_pan": assessee_pan,
            "deductor_tan": deductor_tan,
            "deductor_name": deductor_name,
            "tds_section": tds_section,
            "transaction_month": transaction_month,
            "deposit_date": deposit_date,
            "amount_paid_or_credited": amount_paid_or_credited,
            "tax_deposited": tax_deposited,
            "challan_serial_no": challan_serial_no,
            "bsr_code": bsr_code,
        }

        if text_mode and not any(value is not None for value in normalized_data.values()):
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_FORM_26AS,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        errors: list[dict[str, str]] = []

        if transaction_month_raw is not None and transaction_month is None:
            errors.append(build_error("transaction_month", "Unable to parse month"))
        if amount_paid_or_credited_raw is not None and amount_paid_or_credited is None:
            errors.append(build_error("amount_paid_or_credited", "Unable to parse amount"))
        if tax_deposited_raw is not None and tax_deposited is None:
            errors.append(build_error("tax_deposited", "Unable to parse amount"))

        if tax_deposited is None:
            errors.append(build_error("tax_deposited", "Required field is missing"))

        for field_name, field_value in (
            ("assessee_pan", assessee_pan),
            ("deductor_tan", deductor_tan),
            ("tds_section", tds_section),
            ("transaction_month", transaction_month),
            ("deposit_date", deposit_date),
            ("challan_serial_no", challan_serial_no),
        ):
            if field_value is None:
                errors.append(build_error(field_name, "Preferred field is missing"))

        if tax_deposited is None and not text_mode:
            status_value = NORMALIZATION_STATUS_FAILED
            confidence = 0.0
        elif tax_deposited is None:
            status_value = NORMALIZATION_STATUS_PARTIAL
            confidence = 0.55
        elif errors:
            status_value = NORMALIZATION_STATUS_PARTIAL
            confidence = 0.7
        else:
            status_value = NORMALIZATION_STATUS_NORMALIZED
            confidence = 0.95

        return NormalizedItem(
            source_record_id=source_record_id,
            record_category=NORMALIZED_CATEGORY_FORM_26AS,
            normalized_data=normalized_data,
            normalization_status=status_value,
            normalization_confidence=confidence,
            normalization_errors=errors or None,
        )

    @staticmethod
    def _extract_from_text(raw_text: str) -> dict[str, str | None]:
        extracted: dict[str, str | None] = {}
        for field, pattern in _TEXT_PATTERNS.items():
            match = re.search(pattern, raw_text)
            extracted[field] = clean_string(match.group(1)) if match else None
        return extracted