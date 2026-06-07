from __future__ import annotations

from typing import Any

from app.core.constants import (
    EXTRACTION_RECORD_TYPE_METADATA,
    NORMALIZATION_STATUS_FAILED,
    NORMALIZATION_STATUS_NORMALIZED,
    NORMALIZATION_STATUS_PARTIAL,
    NORMALIZATION_STATUS_SKIPPED,
    NORMALIZED_CATEGORY_VENDOR_MASTER,
)
from app.normalizers.base import BaseNormalizer, NormalizedItem
from app.normalizers.common import (
    build_error,
    clean_string,
    get_record_raw_data,
    get_record_value,
    get_value,
    parse_rate,
)
from app.normalizers.field_aliases import (
    TDS_RATE_ALIASES,
    TDS_SECTION_ALIASES,
    VENDOR_CODE_ALIASES,
    VENDOR_GSTIN_ALIASES,
    VENDOR_NAME_ALIASES,
    VENDOR_PAN_ALIASES,
)


class VendorMasterNormalizer(BaseNormalizer):
    def normalize_record(self, extracted_record: Any) -> NormalizedItem:
        source_record_id = get_record_value(extracted_record, "id")
        record_type = clean_string(get_record_value(extracted_record, "record_type"))
        raw_data = get_record_raw_data(extracted_record)

        if record_type == EXTRACTION_RECORD_TYPE_METADATA:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_VENDOR_MASTER,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_SKIPPED,
                normalization_confidence=0.0,
                normalization_errors=None,
            )

        errors: list[dict[str, str]] = []

        if not raw_data:
            return NormalizedItem(
                source_record_id=source_record_id,
                record_category=NORMALIZED_CATEGORY_VENDOR_MASTER,
                normalized_data={},
                normalization_status=NORMALIZATION_STATUS_FAILED,
                normalization_confidence=0.0,
                normalization_errors=[build_error("raw_data", "Raw row data missing")],
            )

        vendor_code = clean_string(get_value(raw_data, VENDOR_CODE_ALIASES))
        vendor_name = clean_string(get_value(raw_data, VENDOR_NAME_ALIASES))
        vendor_pan = clean_string(get_value(raw_data, VENDOR_PAN_ALIASES))
        vendor_gstin = clean_string(get_value(raw_data, VENDOR_GSTIN_ALIASES))
        tds_section = clean_string(get_value(raw_data, TDS_SECTION_ALIASES))
        tds_rate_raw = get_value(raw_data, TDS_RATE_ALIASES)
        tds_rate = parse_rate(tds_rate_raw)
        vendor_type = clean_string(get_value(raw_data, ("vendor_type", "supplier_type", "type")))
        status = clean_string(get_value(raw_data, ("status", "vendor_status")))

        if not vendor_name:
            errors.append(build_error("vendor_name", "Required field is missing"))

        if tds_rate_raw is not None and tds_rate is None:
            errors.append(build_error("tds_rate", "Unable to parse rate"))

        for field_name, field_value in (
            ("vendor_code", vendor_code),
            ("vendor_pan", vendor_pan),
            ("tds_section", tds_section),
            ("tds_rate", tds_rate),
        ):
            if field_value is None:
                errors.append(build_error(field_name, "Preferred field is missing"))

        normalized_data = {
            "vendor_code": vendor_code,
            "vendor_name": vendor_name,
            "vendor_pan": vendor_pan,
            "vendor_gstin": vendor_gstin,
            "tds_section": tds_section,
            "tds_rate": tds_rate,
            "vendor_type": vendor_type,
            "status": status,
        }

        if not vendor_name:
            status_value = NORMALIZATION_STATUS_FAILED
            confidence = 0.0
        elif errors:
            status_value = NORMALIZATION_STATUS_PARTIAL
            confidence = 0.65
        else:
            status_value = NORMALIZATION_STATUS_NORMALIZED
            confidence = 0.98

        return NormalizedItem(
            source_record_id=source_record_id,
            record_category=NORMALIZED_CATEGORY_VENDOR_MASTER,
            normalized_data=normalized_data,
            normalization_status=status_value,
            normalization_confidence=confidence,
            normalization_errors=errors or None,
        )