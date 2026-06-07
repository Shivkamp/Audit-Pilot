from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.services.processing_job_service import ProcessingJobService


def _mock_job(
    document_id: UUID,
    workspace_id: UUID,
    job_id: UUID | None = None,
    status: str = "pending",
) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=job_id or uuid4(),
        document_id=document_id,
        workspace_id=workspace_id,
        job_type="document_processing",
        status=status,
        celery_task_id="celery-task-id",
        progress_percent=10,
        current_step="Document processing started",
        error_message=None,
        started_at=now,
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


def test_get_job(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    job_id = uuid4()
    mock_job = _mock_job(document_id=document_id, workspace_id=workspace_id, job_id=job_id)

    monkeypatch.setattr(ProcessingJobService, "get_job", lambda db, jid: mock_job)

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Job fetched successfully"
    assert body["data"]["id"] == str(job_id)


def test_list_document_jobs(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    jobs = [
        _mock_job(document_id=document_id, workspace_id=workspace_id),
        _mock_job(document_id=document_id, workspace_id=workspace_id),
    ]

    monkeypatch.setattr(ProcessingJobService, "list_document_jobs", lambda db, did: jobs)

    response = client.get(f"/api/v1/documents/{document_id}/jobs")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document jobs fetched successfully"
    assert len(body["data"]) == 2
    assert all(item["document_id"] == str(document_id) for item in body["data"])


def test_list_workspace_jobs(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    jobs = [
        _mock_job(document_id=document_id, workspace_id=workspace_id),
        _mock_job(document_id=document_id, workspace_id=workspace_id),
    ]

    monkeypatch.setattr(ProcessingJobService, "list_workspace_jobs", lambda db, wid: jobs)

    response = client.get(f"/api/v1/workspaces/{workspace_id}/jobs")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace jobs fetched successfully"
    assert len(body["data"]) == 2
    assert all(item["workspace_id"] == str(workspace_id) for item in body["data"])


def test_retry_job(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    original_job_id = uuid4()
    retried_job = _mock_job(document_id=document_id, workspace_id=workspace_id, status="pending")

    monkeypatch.setattr(ProcessingJobService, "retry_job", lambda db, jid: retried_job)

    response = client.post(f"/api/v1/jobs/{original_job_id}/retry")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Job retried successfully"
    assert body["data"]["document_id"] == str(document_id)
