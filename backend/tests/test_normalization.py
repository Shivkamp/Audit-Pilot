from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.normalization_service import NormalizationService


def _mock_normalized_record(document_id, workspace_id, source_record_id=None):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        workspace_id=workspace_id,
        document_id=document_id,
        source_record_id=source_record_id or uuid4(),
        record_category="vendor_ledger",
        normalized_data={
            "vendor_name": "BluePeak Consulting Pvt Ltd",
            "invoice_number": "INV-1001",
            "gross_amount": 250000.0,
        },
        normalization_status="normalized",
        normalization_confidence=0.97,
        normalization_errors=None,
        created_at=now,
        updated_at=now,
    )


def test_get_document_normalized_records(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()
    workspace_id = uuid4()
    mock_record = _mock_normalized_record(document_id, workspace_id)

    monkeypatch.setattr(
        NormalizationService,
        "get_document_normalized_records",
        lambda db, document_id, limit, offset, record_category, normalization_status: {
            "document_id": document_id,
            "total_records": 1,
            "limit": limit,
            "offset": offset,
            "records": [mock_record],
        },
    )

    response = client.get(
        f"/api/v1/documents/{document_id}/normalized-records?limit=5&offset=0"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Normalized records fetched successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["total_records"] == 1
    assert body["data"]["records"][0]["source_record_id"] == str(mock_record.source_record_id)
    assert body["data"]["records"][0]["normalized_data"]["vendor_name"] == "BluePeak Consulting Pvt Ltd"


def test_get_document_normalized_records_limit_is_clamped(
    client: TestClient,
    monkeypatch,
) -> None:
    document_id = uuid4()
    captured: dict[str, int] = {}

    def _mock_service(db, document_id, limit, offset, record_category, normalization_status):
        captured["limit"] = limit
        return {
            "document_id": document_id,
            "total_records": 0,
            "limit": limit,
            "offset": offset,
            "records": [],
        }

    monkeypatch.setattr(NormalizationService, "get_document_normalized_records", _mock_service)

    response = client.get(
        f"/api/v1/documents/{document_id}/normalized-records"
        f"?limit={settings.normalization_api_max_limit + 1000}&offset=0"
    )

    assert response.status_code == 200
    assert captured["limit"] == settings.normalization_api_max_limit


def test_get_document_normalization_summary(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()

    monkeypatch.setattr(
        NormalizationService,
        "get_document_normalization_summary",
        lambda db, doc_id: {
            "document_id": document_id,
            "document_type": "vendor_ledger",
            "total_records": 37,
            "normalized": 35,
            "partial": 1,
            "failed": 1,
            "skipped": 0,
        },
    )

    response = client.get(f"/api/v1/documents/{document_id}/normalization-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["document_type"] == "vendor_ledger"
    assert body["data"]["total_records"] == 37
    assert body["data"]["normalized"] == 35


def test_normalize_document_route(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()

    monkeypatch.setattr(
        NormalizationService,
        "normalize_document",
        lambda db, doc_id: {
            "document_id": document_id,
            "document_type": "tds_working",
            "total_processed": 37,
            "normalized": 36,
            "partial": 1,
            "failed": 0,
            "skipped": 0,
        },
    )

    response = client.post(f"/api/v1/documents/{document_id}/normalize")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document normalized successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["total_processed"] == 37


def test_get_workspace_normalization_summary(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()

    monkeypatch.setattr(
        NormalizationService,
        "get_workspace_normalization_summary",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "documents": [
                {
                    "document_id": document_id,
                    "original_filename": "vendor_ledger.csv",
                    "document_status": "processed",
                    "document_type": "vendor_ledger",
                    "total_records": 37,
                    "normalized": 35,
                    "partial": 1,
                    "failed": 1,
                    "skipped": 0,
                }
            ],
        },
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/normalization-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["documents"][0]["document_id"] == str(document_id)
    assert body["data"]["documents"][0]["normalized"] == 35