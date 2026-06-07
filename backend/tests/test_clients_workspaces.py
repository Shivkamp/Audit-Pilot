from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.exceptions import AppException
from app.services.client_service import ClientService
from app.services.workspace_service import WorkspaceService


def _mock_client(client_id: UUID | None = None) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=client_id or uuid4(),
        name="ACME Corp",
        pan="ABCDE1234F",
        gstin=None,
        tan=None,
        email="accounts@acme.test",
        phone="9999999999",
        address="Mumbai",
        industry="Manufacturing",
        status="active",
        created_at=now,
        updated_at=now,
    )


def _mock_workspace(
    client_id: UUID,
    workspace_id: UUID | None = None,
    name: str = "FY24 Audit",
) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=workspace_id or uuid4(),
        client_id=client_id,
        name=name,
        description="Primary workspace",
        financial_year="2024-25",
        status="active",
        created_at=now,
        updated_at=now,
    )


def test_create_client(client: TestClient, monkeypatch) -> None:
    mock_client = _mock_client()
    monkeypatch.setattr(ClientService, "create_client", lambda db, payload: mock_client)

    response = client.post(
        "/api/v1/clients",
        json={"name": "ACME Corp", "email": "accounts@acme.test"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(mock_client.id)
    assert body["data"]["name"] == "ACME Corp"


def test_get_client(client: TestClient, monkeypatch) -> None:
    client_id = uuid4()
    monkeypatch.setattr(ClientService, "get_client", lambda db, cid: _mock_client(cid))

    response = client.get(f"/api/v1/clients/{client_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(client_id)


def test_create_workspace_under_client(client: TestClient, monkeypatch) -> None:
    client_id = uuid4()
    mock_workspace = _mock_workspace(client_id=client_id)
    monkeypatch.setattr(
        WorkspaceService,
        "create_workspace",
        lambda db, cid, payload, **kwargs: mock_workspace,
    )

    response = client.post(
        f"/api/v1/clients/{client_id}/workspaces",
        json={
            "name": "FY24 Audit",
            "description": "Primary workspace",
            "financial_year": "2024-25",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["client_id"] == str(client_id)
    assert body["data"]["name"] == "FY24 Audit"


def test_list_workspaces_under_client(client: TestClient, monkeypatch) -> None:
    client_id = uuid4()
    workspaces = [
        _mock_workspace(client_id=client_id, name="FY24 Audit"),
        _mock_workspace(client_id=client_id, name="FY25 Audit"),
    ]
    monkeypatch.setattr(
        WorkspaceService,
        "list_client_workspaces",
        lambda db, cid, **kwargs: workspaces,
    )

    response = client.get(f"/api/v1/clients/{client_id}/workspaces")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["data"][0]["client_id"] == str(client_id)


def test_missing_client_returns_controlled_error(client: TestClient, monkeypatch) -> None:
    def _raise_missing_client(db, cid, payload, **kwargs):
        raise AppException(
            message="Client not found.",
            status_code=404,
            error_code="CLIENT_NOT_FOUND",
        )

    monkeypatch.setattr(WorkspaceService, "create_workspace", _raise_missing_client)

    response = client.post(
        f"/api/v1/clients/{uuid4()}/workspaces",
        json={"name": "FY24", "financial_year": "2024-25"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["errors"]["code"] == "CLIENT_NOT_FOUND"
