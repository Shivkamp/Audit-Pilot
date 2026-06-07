from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api import deps as api_deps
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def bypass_auth_and_workspace_checks_for_legacy_route_tests(request, monkeypatch) -> None:
    app.dependency_overrides.clear()

    if request.node.get_closest_marker("strict_auth"):
        yield
        app.dependency_overrides.clear()
        return

    now = datetime.now(timezone.utc)
    fake_user = SimpleNamespace(
        id=uuid4(),
        email="tester@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        created_at=now,
        updated_at=now,
    )

    app.dependency_overrides[api_deps.get_current_user] = lambda: fake_user
    app.dependency_overrides[api_deps.require_active_user] = lambda: fake_user

    monkeypatch.setattr(
        api_deps,
        "require_workspace_access",
        lambda workspace_id, *, db, current_user, allowed_roles=None: None,
    )
    monkeypatch.setattr(
        api_deps,
        "require_workspace_role",
        lambda workspace_id, *, db, current_user, allowed_roles: None,
    )
    monkeypatch.setattr(
        api_deps,
        "_get_document_for_access",
        lambda db, document_id, include_deleted=False: SimpleNamespace(
            id=document_id,
            workspace_id=uuid4(),
            status="uploaded",
        ),
    )
    monkeypatch.setattr(
        api_deps,
        "_get_job_for_access",
        lambda db, job_id: SimpleNamespace(
            id=job_id,
            workspace_id=uuid4(),
        ),
    )
    monkeypatch.setattr(
        api_deps,
        "_get_risk_finding_for_access",
        lambda db, finding_id: SimpleNamespace(
            id=finding_id,
            workspace_id=uuid4(),
        ),
    )
    monkeypatch.setattr(
        api_deps,
        "_get_risk_rule_config_for_access",
        lambda db, config_id: SimpleNamespace(
            id=config_id,
            workspace_id=uuid4(),
        ),
    )

    yield
    app.dependency_overrides.clear()
