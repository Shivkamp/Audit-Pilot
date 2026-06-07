from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.extraction_service import ExtractionService


def _mock_extracted_record(document_id, workspace_id):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        document_id=document_id,
        workspace_id=workspace_id,
        record_type="excel_row",
        page_number=None,
        sheet_name="Sheet1",
        row_number=2,
        column_name=None,
        raw_text=None,
        raw_data={"invoice_no": "INV-001", "amount": "1000"},
        created_at=now,
        updated_at=now,
    )


def test_get_document_extracted_records(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()
    workspace_id = uuid4()
    mock_record = _mock_extracted_record(document_id, workspace_id)

    monkeypatch.setattr(
        ExtractionService,
        "get_document_extracted_records",
        lambda db, document_id, limit, offset, record_type: {
            "document_id": document_id,
            "total_records": 1,
            "limit": limit,
            "offset": offset,
            "records": [mock_record],
        },
    )

    response = client.get(
        f"/api/v1/documents/{document_id}/extracted-records?limit=5&offset=0"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Extracted records fetched successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["total_records"] == 1
    assert body["data"]["records"][0]["sheet_name"] == "Sheet1"
    assert body["data"]["records"][0]["row_number"] == 2
    assert body["data"]["records"][0]["raw_data"]["invoice_no"] == "INV-001"


def test_get_document_extracted_records_limit_is_clamped(
    client: TestClient,
    monkeypatch,
) -> None:
    document_id = uuid4()
    captured: dict[str, int] = {}

    def _mock_service(db, document_id, limit, offset, record_type):
        captured["limit"] = limit
        return {
            "document_id": document_id,
            "total_records": 0,
            "limit": limit,
            "offset": offset,
            "records": [],
        }

    monkeypatch.setattr(ExtractionService, "get_document_extracted_records", _mock_service)

    response = client.get(
        f"/api/v1/documents/{document_id}/extracted-records"
        f"?limit={settings.extraction_api_max_limit + 500}&offset=0"
    )

    assert response.status_code == 200
    assert captured["limit"] == settings.extraction_api_max_limit


def test_get_document_extraction_summary(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()

    monkeypatch.setattr(
        ExtractionService,
        "get_document_extraction_summary",
        lambda db, doc_id: {
            "document_id": document_id,
            "total_records": 3,
            "text_records": 0,
            "excel_rows": 3,
            "csv_rows": 0,
            "table_rows": 0,
            "metadata_records": 0,
            "pages_detected": [],
            "sheets_detected": ["Sheet1"],
        },
    )

    response = client.get(f"/api/v1/documents/{document_id}/extraction-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["excel_rows"] == 3
    assert body["data"]["sheets_detected"] == ["Sheet1"]


def test_get_workspace_extraction_summary(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()

    monkeypatch.setattr(
        ExtractionService,
        "get_workspace_extraction_summary",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "documents": [
                {
                    "document_id": document_id,
                    "original_filename": "ledger.xlsx",
                    "document_status": "processed",
                    "total_extracted_records": 120,
                    "text_records": 0,
                    "excel_rows": 120,
                    "csv_rows": 0,
                    "table_rows": 0,
                    "metadata_records": 0,
                }
            ],
        },
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/extraction-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["documents"][0]["document_id"] == str(document_id)
    assert body["data"]["documents"][0]["excel_rows"] == 120
