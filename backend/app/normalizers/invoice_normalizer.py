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
    NORMALIZED_CATEGORY_INVOICE,
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
)
from app.normalizers.field_aliases import (
    CUSTOMER_NAME_ALIASES,
    INVOICE_DATE_ALIASES,
    INVOICE_NUMBER_ALIASES,
    SUPPLIER_NAME_ALIASES,
    TDS_SECTION_ALIASES,
    VENDOR_PAN_ALIASES,
)

_TEXT_PATTERNS = {
    "supplier_name": r"(?im)^\s*supplier\s*[:\-]\s*(.+)$",
    "supplier_pan": r"(?im)^\s*supplier\s*pan\s*[:\-]?\s*([A-Z0-9]+)",
    "customer_name": r"(?im)^\s*customer\s*[:\-]\s*(.+)$",
    "invoice_number": r"(?im)^\s*invoice\s*(?:no\.?|number)\s*[:\-]?\s*([A-Z0-9\-/]+)",
    "invoice_date": r"(?im)^\s*invoice\s*date\s*[:\-]?\s*([\d]{1,4}[/-][\d]{1,2}[/-][\d]{1,4})",
    "gross_amount": r"(?im)^\s*gross\s*amount\s*[:\-]?\s*([\(\)\d,\.₹ \tA-Za-z-]+)$",
    "tds_section_hint": (
        r"(?im)^\s*(?:suggested\s*tds\s*section|tds\s*section\s*hint|tds\s*section)\s*[:\-]?\s*([A-Za-z0-9]+)"
    ),
}


class InvoiceNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)
        raw_text = get_record_raw_text(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA and not raw_text:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_INVOICE,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        text_values: dict[str, str | None] = {}
        text_mode = False
        if raw_text and record_type == EXTRACTION_RECORD_TYPE_TEXT:
            text_mode = True
            text_values = self._extract_from_text(raw_text)

        supplier_name = clean_string(get_value(raw_data, SUPPLIER_NAME_ALIASES))
        supplier_pan = clean_string(get_value(raw_data, VENDOR_PAN_ALIASES))
        customer_name = clean_string(get_value(raw_data, CUSTOMER_NAME_ALIASES))
        invoice_number = clean_string(get_value(raw_data, INVOICE_NUMBER_ALIASES))

        invoice_date_raw = get_value(raw_data, INVOICE_DATE_ALIASES)
        invoice_date = parse_date(invoice_date_raw)

        gross_amount_raw = get_value(raw_data, ("gross_amount", "amount", "invoice_amount"))
        gross_amount = parse_decimal(gross_amount_raw)

        tds_section_hint = clean_string(
            get_value(
                raw_data,
                ("suggested_tds_section", "tds_section_hint", *TDS_SECTION_ALIASES),
            )
        )

        if text_values:
            supplier_name = supplier_name or clean_string(text_values.get("supplier_name"))
            supplier_pan = supplier_pan or clean_string(text_values.get("supplier_pan"))
            customer_name = customer_name or clean_string(text_values.get("customer_name"))
            invoice_number = invoice_number or clean_string(text_values.get("invoice_number"))

            if invoice_date is None:
                invoice_date_raw = text_values.get("invoice_date")
                invoice_date = parse_date(invoice_date_raw)

            if gross_amount is None:
                gross_amount_raw = text_values.get("gross_amount")
                gross_amount = parse_decimal(gross_amount_raw)

            tds_section_hint = tds_section_hint or clean_string(text_values.get("tds_section_hint"))

        normalized_data = {
            "supplier_name": supplier_name,
            "supplier_pan": supplier_pan,
            "customer_name": customer_name,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "gross_amount": gross_amount,
            "tds_section_hint": tds_section_hint,
        }

        errors: list[dict[str, str]] = []
        if invoice_date_raw is not None and invoice_date is None:
            errors.append(build_error("invoice_date", "Unable to parse date"))
        if gross_amount_raw is not None and gross_amount is None:
            errors.append(build_error("gross_amount", "Unable to parse amount"))

        has_required_signal = bool(invoice_number or supplier_name or gross_amount is not None)
        if not has_required_signal:
            if text_mode or record_type == EXTRACTION_RECORD_TYPE_METADATA:
                return NormalizedItem(
                    source_record_id=source_record_id,
                    record_category=NORMALIZED_CATEGORY_INVOICE,
                    normalized_data={},
                    normalization_status=NORMALIZATION_STATUS_SKIPPED,
                    normalization_confidence=0.0,
                    normalization_errors=None,
                )

            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_INVOICE,
                normalized_data=normalized_data,
                normalization_status=NORMALIZATION_STATUS_FAILED,
                normalization_confidence=0.0,
                normalization_errors=[
                    build_error(
                        "record",
                        "At least one of invoice_number, supplier_name, or gross_amount is required",
                    )
                ],
            )

        if invoice_number and gross_amount is not None and not errors:
            status_value = NORMALIZATION_STATUS_NORMALIZED
            confidence = 0.95
        else:
            status_value = NORMALIZATION_STATUS_PARTIAL
            confidence = 0.65

        return NormalizedItem(
            source_record_id=source_record_id,
            record_category=NORMALIZED_CATEGORY_INVOICE,
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