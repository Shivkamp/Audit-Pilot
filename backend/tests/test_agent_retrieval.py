from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.agent_retrieval_service import AgentRetrievalService



def _mock_evidence_item() -> dict:
    return {
        "content": "Risk finding: TDS short deposit detected.",
        "score": 0.91,
        "source_type": "risk_finding",
        "source_id": str(uuid4()),
        "chunk_type": "risk_short_deposit",
        "facts": {"risk_type": "short_deposit"},
        "citation": {"source_type": "risk_finding"},
        "source_trace": {"source_type": "risk_finding", "document_ids": [str(uuid4())]},
    }



def test_retrieve_workspace_agent_evidence(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    monkeypatch.setattr(
        AgentRetrievalService,
        "retrieve_workspace_evidence",
        lambda db, workspace_id, query, limit, include_source_trace: {
            "workspace_id": workspace_id,
            "query": query,
            "limit": limit,
            "evidence": [_mock_evidence_item()],
        },
    )

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/agent-retrieval/evidence",
        json={
            "query": "Why was short deposit flagged for September 194J?",
            "limit": 5,
            "include_source_trace": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert len(body["data"]["evidence"]) == 1



def test_retrieve_workspace_risk_evidence_limit_is_clamped(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    captured: dict[str, int] = {}

    def _mock_risk_evidence(db, workspace_id, risk_type, query, limit, include_source_trace):
        captured["limit"] = limit
        return {
            "workspace_id": workspace_id,
            "risk_type": risk_type,
            "query": query,
            "limit": limit,
            "evidence": [_mock_evidence_item()],
        }

    monkeypatch.setattr(AgentRetrievalService, "retrieve_risk_evidence", _mock_risk_evidence)

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/agent-retrieval/risk-evidence",
        json={
            "risk_type": "short_deposit",
            "query": "September 194J",
            "limit": settings.agent_retrieval_max_limit + 100,
            "include_source_trace": True,
        },
    )

    assert response.status_code == 200
    assert captured["limit"] == settings.agent_retrieval_max_limit



def test_get_risk_finding_context(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    finding_id = uuid4()

    monkeypatch.setattr(
        AgentRetrievalService,
        "get_finding_context",
        lambda db, wid, rid: {
            "workspace_id": wid,
            "risk_finding": {"id": str(rid), "risk_type": "short_deposit"},
            "related_normalized_records": [],
            "source_trace": {"source_type": "risk_finding", "source_id": str(rid)},
        },
    )

    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/agent-retrieval/risk-findings/{finding_id}/context"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["risk_finding"]["id"] == str(finding_id)



def test_get_workspace_source_trace(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    source_id = str(uuid4())

    monkeypatch.setattr(
        AgentRetrievalService,
        "get_source_trace",
        lambda db, workspace_id, source_type, source_id: {
            "source_type": source_type,
            "source_id": source_id,
            "document_ids": [str(uuid4())],
            "source_locations": [{"sheet_name": "tds_working", "row_number": 18}],
        },
    )

    response = client.get(
        f"/api/v1/workspaces/{workspace_id}/source-trace/risk_finding/{source_id}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["source_type"] == "risk_finding"
    assert body["data"]["source_id"] == source_id
