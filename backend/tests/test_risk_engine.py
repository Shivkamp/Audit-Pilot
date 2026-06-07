from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID, uuid4

from app.core.constants import (
    NORMALIZED_CATEGORY_TDS_CHALLAN,
    NORMALIZED_CATEGORY_TDS_WORKING,
    NORMALIZED_CATEGORY_VENDOR_LEDGER,
    NORMALIZED_CATEGORY_VENDOR_MASTER,
    RISK_SEVERITY_CRITICAL,
    RISK_TYPE_DUPLICATE_INVOICE,
    RISK_TYPE_MISSING_PAN,
    RISK_TYPE_SHORT_DEPOSIT,
    RISK_TYPE_TDS_MISMATCH,
    RISK_TYPE_VENDOR_NAME_MISMATCH,
)
from app.risk_engine.engine import RiskEngine


def _record(
    category: str,
    normalized_data: dict,
    document_id: UUID | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        document_id=document_id or uuid4(),
        record_category=category,
        normalized_data=normalized_data,
    )


def test_risk_engine_v1_detects_core_findings() -> None:
    workspace_doc_id = uuid4()

    missing_pan_vendor_master = _record(
        NORMALIZED_CATEGORY_VENDOR_MASTER,
        {
            "vendor_code": "V005",
            "vendor_name": "Prakash Logistics",
            "vendor_pan": "",
        },
        workspace_doc_id,
    )

    duplicate_ledger_1 = _record(
        NORMALIZED_CATEGORY_VENDOR_LEDGER,
        {
            "vendor_code": "V004",
            "vendor_name": "Zenith Advertising Co",
            "invoice_number": "INV-1004",
            "invoice_date": "2024-07-14",
            "gross_amount": 90000,
            "vendor_pan": "AAAFZ5678F",
        },
        workspace_doc_id,
    )
    duplicate_ledger_2 = _record(
        NORMALIZED_CATEGORY_VENDOR_LEDGER,
        {
            "vendor_code": "V004",
            "vendor_name": "Zenith Advertising Co",
            "invoice_number": "INV-1004",
            "invoice_date": "2024-07-14",
            "gross_amount": 90000,
            "vendor_pan": "AAAFZ5678F",
        },
        workspace_doc_id,
    )

    vendor_name_variant_master = _record(
        NORMALIZED_CATEGORY_VENDOR_MASTER,
        {
            "vendor_code": "V010",
            "vendor_name": "Zenith Advertising Co",
            "vendor_pan": "ABCDE1234F",
        },
        workspace_doc_id,
    )
    vendor_name_variant_ledger = _record(
        NORMALIZED_CATEGORY_VENDOR_LEDGER,
        {
            "vendor_code": "V010",
            "vendor_name": "Zenith Ads Company",
            "invoice_number": "INV-5555",
            "invoice_date": "2024-11-20",
            "gross_amount": 15000,
            "vendor_pan": "ABCDE1234F",
        },
        workspace_doc_id,
    )

    tds_working_mismatch = _record(
        NORMALIZED_CATEGORY_TDS_WORKING,
        {
            "deduction_month": "2024-09",
            "vendor_code": "V006",
            "vendor_name": "Sundar IT Solutions",
            "invoice_number": "INV-1006",
            "tds_section": "194J",
            "tds_required": 30000,
            "tds_deducted": 25000,
        },
        workspace_doc_id,
    )
    tds_working_regular = _record(
        NORMALIZED_CATEGORY_TDS_WORKING,
        {
            "deduction_month": "2024-09",
            "vendor_code": "V006",
            "vendor_name": "Sundar IT Solutions",
            "invoice_number": "INV-1030",
            "tds_section": "194J",
            "tds_required": 32000,
            "tds_deducted": 32000,
        },
        workspace_doc_id,
    )

    challan_row = _record(
        NORMALIZED_CATEGORY_TDS_CHALLAN,
        {
            "deduction_month": "2024-09",
            "tds_section": "194J",
            "tds_deposited": 52000,
        },
        workspace_doc_id,
    )

    engine = RiskEngine(short_deposit_critical_threshold=5000)
    findings = engine.run(
        {
            NORMALIZED_CATEGORY_VENDOR_MASTER: [
                missing_pan_vendor_master,
                vendor_name_variant_master,
            ],
            NORMALIZED_CATEGORY_VENDOR_LEDGER: [
                duplicate_ledger_1,
                duplicate_ledger_2,
                vendor_name_variant_ledger,
            ],
            NORMALIZED_CATEGORY_TDS_WORKING: [
                tds_working_mismatch,
                tds_working_regular,
            ],
            NORMALIZED_CATEGORY_TDS_CHALLAN: [challan_row],
        }
    )

    findings_by_type: dict[str, list] = {}
    for finding in findings:
        findings_by_type.setdefault(finding.risk_type, []).append(finding)

    assert RISK_TYPE_MISSING_PAN in findings_by_type
    assert RISK_TYPE_DUPLICATE_INVOICE in findings_by_type
    assert RISK_TYPE_TDS_MISMATCH in findings_by_type
    assert RISK_TYPE_SHORT_DEPOSIT in findings_by_type
    assert RISK_TYPE_VENDOR_NAME_MISMATCH in findings_by_type

    missing_pan_finding = findings_by_type[RISK_TYPE_MISSING_PAN][0]
    assert missing_pan_finding.primary_normalized_record_id is not None
    assert missing_pan_finding.related_normalized_record_ids

    duplicate_finding = findings_by_type[RISK_TYPE_DUPLICATE_INVOICE][0]
    assert duplicate_finding.related_normalized_record_ids is not None
    assert len(duplicate_finding.related_normalized_record_ids) > 1

    mismatch_finding = findings_by_type[RISK_TYPE_TDS_MISMATCH][0]
    assert mismatch_finding.risk_data is not None
    assert mismatch_finding.risk_data["shortfall"] > 0

    short_deposit_finding = findings_by_type[RISK_TYPE_SHORT_DEPOSIT][0]
    assert short_deposit_finding.severity == RISK_SEVERITY_CRITICAL
    assert short_deposit_finding.risk_data is not None
    assert short_deposit_finding.risk_data["deduction_month"] == "2024-09"
    assert short_deposit_finding.risk_data["tds_section"] == "194J"
    assert short_deposit_finding.risk_data["shortfall"] == 5000
