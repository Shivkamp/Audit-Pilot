from __future__ import annotations

from typing import Any

from app.core.constants import (
    EXTRACTION_RECORD_TYPE_METADATA,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_SKIPPED,
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
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
    parse_rate,
)
from app.normalizers.field_aliases import (
    GROSS_AMOUNT_ALIASES,
    INVOICE_DATE_ALIASES,
    INVOICE_NUMBER_ALIASES,
    TDS_DEDUCTED_ALIASES,
    TDS_RATE_ALIASES,
    TDS_SECTION_ALIASES,
    TRANSACTION_DATE_ALIASES,
    VENDOR_CODE_ALIASES,
    VENDOR_NAME_ALIASES,
    VENDOR_PAN_ALIASES,
)


class VendorLedgerNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_VENDOR_LEDGER,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        errors: list[dict[str, str]] = []
        if not raw_data:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_VENDOR_LEDGER,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_FAILED,
                normalization_confidence=0.0,
                normalization_errors=[build_error("raw_data", "Raw row data missing")],
            )

        transaction_date_raw = get_value(raw_data, TRANSACTION_DATE_ALIASES)
        transaction_date = parse_date(transaction_date_raw)

        vendor_code = clean_string(get_value(raw_data, VENDOR_CODE_ALIASES))
        vendor_name = clean_string(get_value(raw_data, VENDOR_NAME_ALIASES))
        vendor_pan = clean_string(get_value(raw_data, VENDOR_PAN_ALIASES))
        invoice_number = clean_string(get_value(raw_data, INVOICE_NUMBER_ALIASES))

        invoice_date_raw = get_value(raw_data, INVOICE_DATE_ALIASES)
        invoice_date = parse_date(invoice_date_raw)

        expense_nature = clean_string(
            get_value(raw_data, ("expense_nature", "expense_type", "nature_of_expense"))
        )

        gross_amount_raw = get_value(raw_data, GROSS_AMOUNT_ALIASES)
        gross_amount = parse_decimal(gross_amount_raw)

        tds_section = clean_string(get_value(raw_data, TDS_SECTION_ALIASES))

        tds_rate_raw = get_value(raw_data, TDS_RATE_ALIASES)
        tds_rate = parse_rate(tds_rate_raw)

        tds_deducted_raw = get_value(raw_data, TDS_DEDUCTED_ALIASES)
        tds_deducted = parse_decimal(tds_deducted_raw)

        payment_status = clean_string(get_value(raw_data, ("payment_status", "status")))

        if not vendor_name:
            errors.append(build_error("vendor_name", "Required field is missing"))

        if gross_amount is None:
            if gross_amount_raw is None:
                errors.append(build_error("gross_amount", "Required field is missing"))
            else:
                errors.append(build_error("gross_amount", "Unable to parse amount"))

        if transaction_date_raw is not None and transaction_date is None:
            errors.append(build_error("transaction_date", "Unable to parse date"))
        if invoice_date_raw is not None and invoice_date is None:
            errors.append(build_error("invoice_date", "Unable to parse date"))
        if tds_rate_raw is not None and tds_rate is None:
            errors.append(build_error("tds_rate", "Unable to parse rate"))
        if tds_deducted_raw is not None and tds_deducted is None:
            errors.append(build_error("tds_deducted", "Unable to parse amount"))

        for field_name, field_value in (
            ("transaction_date", transaction_date),
            ("invoice_number", invoice_number),
            ("tds_section", tds_section),
            ("tds_deducted", tds_deducted),
        ):
            if field_value is None:
                errors.append(build_error(field_name, "Preferred field is missing"))

        normalized_data = {
            "transaction_date": transaction_date,
            "vendor_code": vendor_code,
            "vendor_name": vendor_name,
            "vendor_pan": vendor_pan,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "expense_nature": expense_nature,
            "gross_amount": gross_amount,
            "tds_section": tds_section,
            "tds_rate": tds_rate,
            "tds_deducted": tds_deducted,
            "payment_status": payment_status,
        }

        required_missing = not vendor_name or gross_amount is None
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
            record_category=NORMALIZED_CATEGORY_VENDOR_LEDGER,
            normalized_data=normalized_data,
            normalization_status=status_value,
            normalization_confidence=confidence,
            normalization_errors=errors or None,
        )