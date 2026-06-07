from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.exceptions import AppException
from app.services.agent_chat_service import AgentChatService


def test_workspace_agent_chat_success(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    def _mock_chat_workspace(self, request_workspace_id, payload):
        assert request_workspace_id == workspace_id
        assert payload.message == "What are the risks in my data?"
        return {
            "workspace_id": str(workspace_id),
            "message": payload.message,
            "intent": "risk_summary",
            "answer": "Based on processed workspace data, 3 risk findings were identified.",
            "citations": [{"source_type": "risk_finding", "source_id": str(uuid4())}],
            "evidence": [],
            "source_traces": [],
            "warnings": [],
            "confidence": "high",
            "provider": "mock",
            "model": "mock-grounded-v1",
        }

    monkeypatch.setattr(AgentChatService, "chat_workspace", _mock_chat_workspace)

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/agent-chat",
        json={
            "message": "What are the risks in my data?",
            "include_evidence": True,
            "include_source_trace": True,
            "max_evidence": 6,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace agent chat response generated successfully."
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["intent"] == "risk_summary"
    assert body["data"]["provider"] == "mock"


def test_workspace_agent_chat_controlled_error(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    def _mock_chat_workspace(self, request_workspace_id, payload):
        _ = (request_workspace_id, payload)
        raise AppException(
            message="Message cannot be blank.",
            status_code=400,
            error_code="AGENT_CHAT_MESSAGE_REQUIRED",
        )

    monkeypatch.setattr(AgentChatService, "chat_workspace", _mock_chat_workspace)

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/agent-chat",
        json={
            "message": "   ",
            "include_evidence": True,
            "include_source_trace": True,
            "max_evidence": 6,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Message cannot be blank."
    assert body["errors"]["code"] == "AGENT_CHAT_MESSAGE_REQUIRED"
