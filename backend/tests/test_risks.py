from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.risk_engine_service import RiskEngineService


def _mock_risk_finding(
    workspace_id: UUID,
    document_id: UUID,
    finding_id: UUID | None = None,
    risk_type: str = "missing_pan",
    severity: str = "HIGH",
    status: str = "open",
) -> SimpleNamespace:
    now = datetime.now(timezone.utc)
    primary_record_id = uuid4()

    return SimpleNamespace(
        id=finding_id or uuid4(),
        workspace_id=workspace_id,
        document_id=document_id,
        primary_normalized_record_id=primary_record_id,
        related_normalized_record_ids=[str(primary_record_id)],
        risk_type=risk_type,
        severity=severity,
        title="Sample risk finding",
        description="Sample risk finding description",
        risk_data={"sample": True},
        status=status,
        created_at=now,
        updated_at=now,
    )


def test_run_workspace_risk_checks(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    monkeypatch.setattr(
        RiskEngineService,
        "run_workspace_risks",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "total_findings": 4,
            "summary": {
                "workspace_id": workspace_id,
                "total_findings": 4,
                "counts_by_status": {"open": 4},
                "counts_by_severity": {"HIGH": 3, "CRITICAL": 1},
                "counts_by_risk_type": {
                    "missing_pan": 1,
                    "duplicate_invoice": 1,
                    "tds_mismatch": 1,
                    "short_deposit": 1,
                },
            },
        },
    )

    response = client.post(f"/api/v1/workspaces/{workspace_id}/risk-checks/run")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace risk checks completed successfully."
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["total_findings"] == 4


def test_list_workspace_risk_findings_limit_is_clamped(
    client: TestClient,
    monkeypatch,
) -> None:
    workspace_id = uuid4()
    captured: dict[str, int] = {}

    def _mock_service(db, workspace_id, risk_type, severity, status_filter, limit, offset):
        captured["limit"] = limit
        return {
            "workspace_id": workspace_id,
            "total_records": 0,
            "limit": limit,
            "offset": offset,
            "findings": [],
        }

    monkeypatch.setattr(RiskEngineService, "list_workspace_findings", _mock_service)

    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/risk-findings"
        f"?limit={settings.risk_api_max_limit + 1000}&offset=0"
    )

    assert response.status_code == 200
    assert captured["limit"] == settings.risk_api_max_limit


def test_list_document_risk_findings(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    finding = _mock_risk_finding(workspace_id, document_id)

    monkeypatch.setattr(
        RiskEngineService,
        "list_document_findings",
        lambda db, document_id, risk_type, severity, status_filter, limit, offset: {
            "document_id": document_id,
            "total_records": 1,
            "limit": limit,
            "offset": offset,
            "findings": [finding],
        },
    )

    response = client.get(f"/api/v1/documents/{document_id}/risk-findings")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Document risk findings fetched successfully."
    assert body["data"]["document_id"] == str(document_id)
    assert body["data"]["total_records"] == 1
    assert body["data"]["findings"][0]["risk_type"] == "missing_pan"


def test_get_workspace_risk_summary(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    monkeypatch.setattr(
        RiskEngineService,
        "get_workspace_summary",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "total_findings": 3,
            "counts_by_status": {"open": 2, "reviewed": 1},
            "counts_by_severity": {"HIGH": 2, "CRITICAL": 1},
            "counts_by_risk_type": {"missing_pan": 1, "short_deposit": 1, "tds_mismatch": 1},
        },
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/risk-summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace risk summary fetched successfully."
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["counts_by_status"]["reviewed"] == 1


def test_update_risk_finding_status(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    document_id = uuid4()
    finding_id = uuid4()

    updated_finding = _mock_risk_finding(
        workspace_id=workspace_id,
        document_id=document_id,
        finding_id=finding_id,
        status="reviewed",
    )

    monkeypatch.setattr(
        RiskEngineService,
        "update_finding_status",
        lambda db, fid, status: updated_finding,
    )

    response = client.patch(
        f"/api/v1/risk-findings/{finding_id}/status",
        json={"status": "reviewed"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Risk finding status updated successfully."
    assert body["data"]["id"] == str(finding_id)
    assert body["data"]["status"] == "reviewed"
