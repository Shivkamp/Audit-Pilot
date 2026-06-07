from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.constants import DOCUMENT_STATUS_DELETED, DOCUMENT_STATUS_UPLOADED, STORAGE_BACKEND_S3
from app.core.exceptions import AppException
from app.schemas.document import DocumentDownloadUrlResponse
from app.services.document_service import DocumentService


def _mock_document(
    workspace_id: UUID,
    document_id: UUID | None = None,
    *,
    status: str = DOCUMENT_STATUS_UPLOADED,
) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=document_id or uuid4(),
        workspace_id=workspace_id,
        original_filename="Form26AS.pdf",
        stored_filename="form26as.pdf",
        file_extension=".pdf",
        content_type="application/pdf",
        file_size_bytes=1234,
        storage_backend=STORAGE_BACKEND_S3,
        storage_bucket="taxaudit-ai-uploads",
        storage_key=(
            f"workspaces/{workspace_id}/documents/{document_id or uuid4()}/form26as.pdf"
        ),
        document_type="unknown",
        status=status,
        upload_source="manual",
        created_at=now,
        updated_at=now,
    )


def _mock_processing_job(
    document_id: UUID,
    workspace_id: UUID,
    job_id: UUID | None = None,
) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=job_id or uuid4(),
        document_id=document_id,
        workspace_id=workspace_id,
        job_type="document_processing",
        status="pending",
        celery_task_id="celery-task-id",
        progress_percent=0,
        current_step="Awaiting document processing",
        error_message=None,
        started_at=None,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


def test_upload_document(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    mock_document = _mock_document(workspace_id=workspace_id)
    mock_job = _mock_processing_job(
        document_id=mock_document.id,
        workspace_id=workspace_id,
    )

    monkeypatch.setattr(
        DocumentService,
        "upload_document",
        lambda db, wid, file: (mock_document, mock_job),
    )

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/documents/upload",
        files={"file": ("Form26AS.pdf", b"dummy content", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document uploaded successfully"
    assert body["data"]["document"]["workspace_id"] == str(workspace_id)
    assert body["data"]["document"]["file_extension"] == ".pdf"
    assert body["data"]["processing_job"]["document_id"] == str(mock_document.id)


def test_list_workspace_documents(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    mock_documents = [
        _mock_document(workspace_id=workspace_id),
        _mock_document(workspace_id=workspace_id),
    ]

    monkeypatch.setattr(
        DocumentService,
        "list_workspace_documents",
        lambda db, wid: mock_documents,
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/documents")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert all(item["workspace_id"] == str(workspace_id) for item in body["data"])


def test_get_document(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    mock_document = _mock_document(workspace_id=workspace_id, document_id=document_id)

    monkeypatch.setattr(
        DocumentService,
        "get_document",
        lambda db, did: mock_document,
    )

    response = client.get(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(document_id)


def test_delete_document(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    mock_document = _mock_document(
        workspace_id=workspace_id,
        document_id=document_id,
        status=DOCUMENT_STATUS_DELETED,
    )

    monkeypatch.setattr(
        DocumentService,
        "delete_document",
        lambda db, did: mock_document,
    )

    response = client.delete(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == DOCUMENT_STATUS_DELETED


def test_generate_download_url(client: TestClient, monkeypatch) -> None:
    document_id = uuid4()
    download_response = DocumentDownloadUrlResponse(
        document_id=document_id,
        download_url="https://example.com/presigned",
        expires_in_seconds=900,
    )

    monkeypatch.setattr(
        DocumentService,
        "generate_download_url",
        lambda db, did: download_response,
    )

    response = client.get(f"/api/v1/documents/{document_id}/download-url")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Download URL generated successfully"
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["expires_in_seconds"] == 900


def test_download_url_local_storage_returns_controlled_error(
    client: TestClient,
    monkeypatch,
) -> None:
    document_id = uuid4()

    def _raise_not_supported(db, did):
        raise AppException(
            message="Presigned download URLs are only supported for S3-backed documents for now.",
            status_code=400,
            error_code="PRESIGNED_URL_NOT_SUPPORTED",
        )

    monkeypatch.setattr(DocumentService, "generate_download_url", _raise_not_supported)

    response = client.get(f"/api/v1/documents/{document_id}/download-url")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["errors"]["code"] == "PRESIGNED_URL_NOT_SUPPORTED"
