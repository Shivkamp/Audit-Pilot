from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.services.auth_service import AuthService


def _mock_user() -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        email="owner@example.com",
        full_name="Owner User",
        is_active=True,
        is_superuser=False,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.strict_auth
def test_register_route_returns_token_and_user(client: TestClient, monkeypatch) -> None:
    mock_user = _mock_user()

    monkeypatch.setattr(AuthService, "register_user", lambda db, **kwargs: mock_user)
    monkeypatch.setattr(AuthService, "create_access_token", lambda user: "test-token")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "password": "supersecret123",
            "full_name": "Owner User",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "test-token"
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["email"] == "owner@example.com"


@pytest.mark.strict_auth
def test_login_route_returns_token_and_user(client: TestClient, monkeypatch) -> None:
    mock_user = _mock_user()

    monkeypatch.setattr(AuthService, "authenticate_user", lambda db, **kwargs: mock_user)
    monkeypatch.setattr(AuthService, "create_access_token", lambda user: "login-token")

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "owner@example.com",
            "password": "supersecret123",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "login-token"
    assert body["data"]["user"]["email"] == "owner@example.com"


@pytest.mark.strict_auth
def test_me_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["errors"]["code"] == "AUTH_TOKEN_INVALID"


@pytest.mark.strict_auth
def test_protected_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/clients")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["errors"]["code"] == "AUTH_TOKEN_INVALID"
