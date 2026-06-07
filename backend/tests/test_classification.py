from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.classifiers.document_classifier import ClassificationEvidence, DocumentClassifier
from app.core.constants import (
    DOCUMENT_TYPE_FORM_26AS,
    DOCUMENT_TYPE_INVOICE,
    DOCUMENT_TYPE_TDS_CHALLAN,
    DOCUMENT_TYPE_UNKNOWN,
    DOCUMENT_TYPE_VENDOR_MASTER,
)
from app.services.classification_service import ClassificationService


def test_classifier_vendor_master_from_filename_and_columns() -> None:
    classifier = DocumentClassifier(min_confidence=0.55, ambiguity_margin=3)

    result = classifier.classify(
        ClassificationEvidence(
            original_filename="vendor_master.csv",
            file_extension=".csv",
            content_type="text/csv",
            column_names=[
                "vendor_code",
                "vendor_name",
                "pan",
                "gstin",
                "vendor_type",
                "status",
            ],
            sample_raw_data=[
                {
                    "vendor_code": "V001",
                    "vendor_name": "Alpha Traders",
                    "pan": "ABCDE1234F",
                }
            ],
        )
    )

    assert result.document_type == DOCUMENT_TYPE_VENDOR_MASTER
    assert result.confidence >= 0.7
    assert result.method == "rule_based_v1"


def test_classifier_invoice_from_pdf_text_signals() -> None:
    classifier = DocumentClassifier(min_confidence=0.55, ambiguity_margin=3)

    result = classifier.classify(
        ClassificationEvidence(
            original_filename="scan_001.pdf",
            file_extension=".pdf",
            content_type="application/pdf",
            sample_text=(
                "Tax Invoice\n"
                "Invoice No: INV-001\n"
                "Invoice Date: 2026-04-01\n"
                "Supplier: ABC Pvt Ltd\n"
                "Customer: XYZ Ltd\n"
                "Gross Amount: 10000\n"
            ),
        )
    )

    assert result.document_type == DOCUMENT_TYPE_INVOICE
    assert result.confidence >= 0.6


def test_classifier_returns_unknown_for_low_confidence() -> None:
    classifier = DocumentClassifier(min_confidence=0.55, ambiguity_margin=3)

    result = classifier.classify(
        ClassificationEvidence(
            original_filename="random_document.pdf",
            file_extension=".pdf",
            content_type="application/pdf",
            sample_text="hello world",
        )
    )

    assert result.document_type == DOCUMENT_TYPE_UNKNOWN
    assert result.reason["unknown_reason"] in {
        "below_min_confidence",
        "ambiguous_scores",
        "no_positive_signals",
    }


def test_classifier_form_26as_from_pdf_text_signals() -> None:
    classifier = DocumentClassifier(min_confidence=0.55, ambiguity_margin=3)

    result = classifier.classify(
        ClassificationEvidence(
            original_filename="statement.pdf",
            file_extension=".pdf",
            content_type="application/pdf",
            sample_text=(
                "Form 26AS - Annual Tax Statement\n"
                "Assessee: ABC Pvt Ltd\n"
                "Deductor: XYZ Corp\n"
                "Tax Deposited: 50000\n"
            ),
        )
    )

    assert result.document_type == DOCUMENT_TYPE_FORM_26AS
    assert result.confidence >= 0.60


def test_classifier_tds_challan_from_pdf_text_signals() -> None:
    classifier = DocumentClassifier(min_confidence=0.55, ambiguity_margin=3)

    result = classifier.classify(
        ClassificationEvidence(
            original_filename="summary.pdf",
            file_extension=".pdf",
            content_type="application/pdf",
            sample_text=(
                "TDS Challan Summary\n"
                "Challan Serial No: CH001\n"
                "BSR Code: 0510100\n"
                "TAN: DELA12345B\n"
                "TDS Deposited: 25000\n"
            ),
        )
    )

    assert result.document_type == DOCUMENT_TYPE_TDS_CHALLAN
    assert result.confidence >= 0.60


def _mock_classification_payload(document_id):
    return {
        "document_id": document_id,
        "original_filename": "vendor_master.csv",
        "status": "processed",
        "document_type": "vendor_master",
        "classification_confidence": 0.92,
        "classification_method": "rule_based_v1",
        "classification_reason": {
            "matched_signals": [
                {
                    "document_type": "vendor_master",
                    "signal_type": "filename",
                    "signal": "vendor_master",
                    "points": 5,
                }
            ],
            "scores": {"vendor_master": 23, "vendor_ledger": 2},
            "winning_type": "vendor_master",
            "second_best_type": "vendor_ledger",
        },
        "classified_at": datetime.now(timezone.utc),
    }


def test_get_document_classification_route(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()

    monkeypatch.setattr(
        ClassificationService,
        "get_document_classification",
        lambda db, did: _mock_classification_payload(document_id),
    )

    response = client.get(f"/api/v1/documents/{document_id}/classification")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document classification fetched successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["document_type"] == "vendor_master"
    assert body["data"]["classification_method"] == "rule_based_v1"


def test_classify_document_route(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()

    monkeypatch.setattr(
        ClassificationService,
        "classify_document",
        lambda db, did: _mock_classification_payload(document_id),
    )

    response = client.post(f"/api/v1/documents/{document_id}/classify")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document classified successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["classification_confidence"] == 0.92


def test_workspace_classification_summary_route(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()

    monkeypatch.setattr(
        ClassificationService,
        "get_workspace_classification_summary",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "documents": [
                {
                    "document_id": document_id,
                    "original_filename": "ledger.csv",
                    "status": "processed",
                    "document_type": "vendor_ledger",
                    "classification_confidence": 0.88,
                    "classified_at": datetime.now(timezone.utc),
                }
            ],
            "counts_by_document_type": {"vendor_ledger": 1},
        },
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/classification-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace classification summary fetched successfully."
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["documents"][0]["document_id"] == str(document_id)
    assert body["data"]["counts_by_document_type"]["vendor_ledger"] == 1
