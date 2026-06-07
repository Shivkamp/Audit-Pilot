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
    NORMALIZED_CATEGORY_TDS_CHALLAN,
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
    BSR_CODE_ALIASES,
    CHALLAN_SERIAL_NO_ALIASES,
    DEDUCTOR_TAN_ALIASES,
    DEDUCTION_MONTH_ALIASES,
    DEPOSIT_DATE_ALIASES,
    TDS_DEPOSITED_ALIASES,
    TDS_SECTION_ALIASES,
)

_TEXT_PATTERNS = {
    "tan": r"(?im)^\s*(?:tan|deductor\s*tan)\s*[:\-]\s*([A-Z0-9]+)",
    "challan_serial_no": (
        r"(?im)^\s*challan\s*(?:serial\s*)?(?:no\.?|number)?\s*[:\-]\s*([A-Z0-9\-/]+)"
    ),
    "bsr_code": r"(?im)^\s*bsr\s*code\s*[:\-]\s*([A-Z0-9\-/]+)",
    "deduction_month": (
        r"(?im)^\s*(?:deduction\s*month|month|period)\s*[:\-]\s*([A-Za-z]{3,9}[-\s]\d{4}|\d{4}[-/]\d{1,2}|\d{1,2}[-/]\d{4})"
    ),
    "tds_section": r"(?im)^\s*(?:tds\s*section|section)\s*[:\-]\s*([A-Za-z0-9]+)",
    "tds_as_per_working": (
        r"(?im)^\s*(?:tds\s*as\s*per\s*working|tds\s*required)\s*[:\-]\s*([\(\)\d,\.₹\sA-Za-z-]+)$"
    ),
    "tds_deposited": (
        r"(?im)^\s*(?:tds\s*deposited(?:\s*as\s*per\s*challan)?|tax\s*deposited)\s*[:\-]\s*([\(\)\d,\.₹\sA-Za-z-]+)$"
    ),
    "deposit_date": (
        r"(?im)^\s*(?:deposit\s*date|challan\s*date|payment\s*date)\s*[:\-]\s*([\d]{1,4}[/-][\d]{1,2}[/-][\d]{1,4})"
    ),
}


class TDSChallanNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)
        raw_text = get_record_raw_text(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA and not raw_text:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_TDS_CHALLAN,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        text_values: dict[str, str | None] = {}
        text_mode = False
        if not raw_data and raw_text and record_type == EXTRACTION_RECORD_TYPE_TEXT:
            text_values = self._extract_from_text(raw_text)
            text_mode = True

        if raw_data:
            tan = clean_string(get_value(raw_data, DEDUCTOR_TAN_ALIASES))
            challan_serial_no = clean_string(get_value(raw_data, CHALLAN_SERIAL_NO_ALIASES))
            bsr_code = clean_string(get_value(raw_data, BSR_CODE_ALIASES))

            deduction_month_raw = get_value(raw_data, DEDUCTION_MONTH_ALIASES)
            deduction_month = parse_month(deduction_month_raw)

            tds_section = clean_string(get_value(raw_data, TDS_SECTION_ALIASES))

            tds_as_per_working_raw = get_value(
                raw_data,
                ("tds_as_per_working", "tds_required", "tds_as_per_working_amount", "tds_deducted_as_per_working"),
            )
            tds_as_per_working = parse_decimal(tds_as_per_working_raw)

            tds_deposited_raw = get_value(raw_data, TDS_DEPOSITED_ALIASES)
            tds_deposited = parse_decimal(tds_deposited_raw)

            deposit_date_raw = get_value(raw_data, DEPOSIT_DATE_ALIASES)
            deposit_date = parse_date(deposit_date_raw)
        else:
            tan = clean_string(text_values.get("tan"))
            challan_serial_no = clean_string(text_values.get("challan_serial_no"))
            bsr_code = clean_string(text_values.get("bsr_code"))
            deduction_month = parse_month(text_values.get("deduction_month"))
            tds_section = clean_string(text_values.get("tds_section"))
            tds_as_per_working = parse_decimal(text_values.get("tds_as_per_working"))
            tds_deposited = parse_decimal(text_values.get("tds_deposited"))
            deposit_date = parse_date(text_values.get("deposit_date"))

            deduction_month_raw = text_values.get("deduction_month")
            tds_as_per_working_raw = text_values.get("tds_as_per_working")
            tds_deposited_raw = text_values.get("tds_deposited")
            deposit_date_raw = text_values.get("deposit_date")

        normalized_data = {
            "tan": tan,
            "challan_serial_no": challan_serial_no,
            "bsr_code": bsr_code,
            "deduction_month": deduction_month,
            "tds_section": tds_section,
            "tds_as_per_working": tds_as_per_working,
            "tds_deposited": tds_deposited,
            "deposit_date": deposit_date,
        }

        if text_mode and not any(value is not None for value in normalized_data.values()):
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_TDS_CHALLAN,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        errors: list[dict[str, str]] = []

        if deduction_month_raw is not None and deduction_month is None:
            errors.append(build_error("deduction_month", "Unable to parse month"))
        if tds_as_per_working_raw is not None and tds_as_per_working is None:
            errors.append(build_error("tds_as_per_working", "Unable to parse amount"))
        if tds_deposited_raw is not None and tds_deposited is None:
            errors.append(build_error("tds_deposited", "Unable to parse amount"))
        if deposit_date_raw is not None and deposit_date is None:
            errors.append(build_error("deposit_date", "Unable to parse date"))

        required_missing = challan_serial_no is None or tds_deposited is None
        if required_missing:
            if challan_serial_no is None:
                errors.append(build_error("challan_serial_no", "Required field is missing"))
            if tds_deposited is None:
                errors.append(build_error("tds_deposited", "Required field is missing"))

        for field_name, field_value in (
            ("bsr_code", bsr_code),
            ("deduction_month", deduction_month),
            ("tds_section", tds_section),
            ("deposit_date", deposit_date),
        ):
            if field_value is None:
                errors.append(build_error(field_name, "Preferred field is missing"))

        if required_missing and not text_mode:
            status_value = NORMALIZATION_STATUS_FAILED
            confidence = 0.0
        elif required_missing:
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
            record_category=NORMALIZED_CATEGORY_TDS_CHALLAN,
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