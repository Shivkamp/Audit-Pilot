from __future__ import annotations

from typing import Any

from app.core.constants import (
    EXTRACTION_RECORD_TYPE_METADATA,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_SKIPPED,
    NORMALIZED_CATEGORY_TDS_WORKING,
)
from app.normalizers.base import BaseNormalizer, NormalizedItem
from app.normalizers.common import (
    build_error,
    clean_string,
    get_record_raw_data,
    get_record_value,
    get_value,
    parse_date,
    parse_decimal,
    parse_month,
    parse_rate,
)
from app.normalizers.field_aliases import (
    AMOUNT_PAID_OR_CREDITED_ALIASES,
    DEDUCTION_MONTH_ALIASES,
    INVOICE_DATE_ALIASES,
    INVOICE_NUMBER_ALIASES,
    TDS_DEDUCTED_ALIASES,
    TDS_RATE_ALIASES,
    TDS_REQUIRED_ALIASES,
    TDS_SECTION_ALIASES,
    VENDOR_CODE_ALIASES,
    VENDOR_NAME_ALIASES,
    VENDOR_PAN_ALIASES,
)


class TDSWorkingNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_TDS_WORKING,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        errors: list[dict[str, str]] = []

        if not raw_data:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_TDS_WORKING,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_FAILED,
                normalization_confidence=0.0,
                normalization_errors=[build_error("raw_data", "Raw row data missing")],
            )

        deduction_month_raw = get_value(raw_data, DEDUCTION_MONTH_ALIASES)
        deduction_month = parse_month(deduction_month_raw)

        vendor_code = clean_string(get_value(raw_data, VENDOR_CODE_ALIASES))
        vendor_name = clean_string(get_value(raw_data, VENDOR_NAME_ALIASES))
        vendor_pan = clean_string(get_value(raw_data, VENDOR_PAN_ALIASES))
        invoice_number = clean_string(get_value(raw_data, INVOICE_NUMBER_ALIASES))

        invoice_date_raw = get_value(raw_data, INVOICE_DATE_ALIASES)
        invoice_date = parse_date(invoice_date_raw)

        tds_section = clean_string(get_value(raw_data, TDS_SECTION_ALIASES))

        tds_rate_raw = get_value(raw_data, TDS_RATE_ALIASES)
        tds_rate = parse_rate(tds_rate_raw)

        amount_raw = get_value(raw_data, AMOUNT_PAID_OR_CREDITED_ALIASES)
        amount_paid_or_credited = parse_decimal(amount_raw)

        tds_required_raw = get_value(raw_data, TDS_REQUIRED_ALIASES)
        tds_required = parse_decimal(tds_required_raw)

        tds_deducted_raw = get_value(raw_data, TDS_DEDUCTED_ALIASES)
        tds_deducted = parse_decimal(tds_deducted_raw)

        if not vendor_name:
            errors.append(build_error("vendor_name", "Required field is missing"))
        if not tds_section:
            errors.append(build_error("tds_section", "Required field is missing"))
        if amount_paid_or_credited is None:
            if amount_raw is None:
                errors.append(build_error("amount_paid_or_credited", "Required field is missing"))
            else:
                errors.append(build_error("amount_paid_or_credited", "Unable to parse amount"))

        if deduction_month_raw is not None and deduction_month is None:
            errors.append(build_error("deduction_month", "Unable to parse month"))
        if invoice_date_raw is not None and invoice_date is None:
            errors.append(build_error("invoice_date", "Unable to parse date"))
        if tds_rate_raw is not None and tds_rate is None:
            errors.append(build_error("tds_rate", "Unable to parse rate"))
        if tds_required_raw is not None and tds_required is None:
            errors.append(build_error("tds_required", "Unable to parse amount"))
        if tds_deducted_raw is not None and tds_deducted is None:
            errors.append(build_error("tds_deducted", "Unable to parse amount"))

        for field_name, field_value in (
            ("vendor_pan", vendor_pan),
            ("invoice_number", invoice_number),
            ("tds_required", tds_required),
            ("tds_deducted", tds_deducted),
        ):
            if field_value is None:
                errors.append(build_error(field_name, "Preferred field is missing"))

        normalized_data = {
            "deduction_month": deduction_month,
            "vendor_code": vendor_code,
            "vendor_name": vendor_name,
            "vendor_pan": vendor_pan,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "tds_section": tds_section,
            "tds_rate": tds_rate,
            "amount_paid_or_credited": amount_paid_or_credited,
            "tds_required": tds_required,
            "tds_deducted": tds_deducted,
        }

        required_missing = (not vendor_name) or (amount_paid_or_credited is None) or (not tds_section)
        if required_missing:
            status_value = NORMALIZATION_STATUS_FAILED
            confidence = 0.0
        elif errors:
            status_value = NORMALIZATION_STATUS_PARTIAL
            confidence = 0.7
        else:
            status_value = NORMALIZATION_STATUS_NORMALIZED
            confidence = 0.97

        return NormalizedItem(
            source_record_id=source_record_id,
            record_category=NORMALIZED_CATEGORY_TDS_WORKING,
            normalized_data=normalized_data,
            normalization_status=status_value,
            normalization_confidence=confidence,
            normalization_errors=errors or None,
        )