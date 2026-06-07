from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.retrieval_service import RetrievalService



def _mock_chunk(workspace_id):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=uuid4(),
        workspace_id=workspace_id,
        document_id=uuid4(),
        source_type="risk_finding",
        source_id=str(uuid4()),
        chunk_type="risk_short_deposit",
        chunk_text="Risk finding: TDS short deposit detected.",
        chunk_metadata={"risk_type": "short_deposit"},
        embedding=[0.1, 0.2],
        embedding_model="local-hash-v1",
        embedding_provider="local_hash",
        embedding_status="embedded",
        embedding_error=None,
        created_at=now,
        updated_at=now,
    )



def test_rebuild_workspace_knowledge_index(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    monkeypatch.setattr(
        KnowledgeIndexService,
        "rebuild_workspace_index",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "total_chunks": 10,
            "normalized_record_chunks": 6,
            "risk_finding_chunks": 4,
            "embedded_chunks": 10,
            "failed_chunks": 0,
        },
    )

    response = client.post(f"/api/v1/workspaces/{workspace_id}/knowledge-index/rebuild")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace knowledge index rebuilt successfully."
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["embedded_chunks"] == 10



def test_workspace_knowledge_search_limit_is_clamped(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    captured: dict[str, int] = {}

    def _mock_search(db, wid, query, limit):
        captured["limit"] = limit
        return {
            "workspace_id": wid,
            "query": query,
            "limit": limit,
            "results": [],
        }

    monkeypatch.setattr(RetrievalService, "search_workspace", _mock_search)

    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/knowledge-search",
        json={
            "query": "September 194J short deposit",
            "limit": settings.knowledge_search_max_limit + 10,
        },
    )

    assert response.status_code == 200
    assert captured["limit"] == settings.knowledge_search_max_limit



def test_list_workspace_knowledge_chunks(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()
    mock_chunk = _mock_chunk(workspace_id)

    monkeypatch.setattr(
        KnowledgeIndexService,
        "list_workspace_chunks",
        lambda db, wid, source_type, chunk_type, embedding_status, limit, offset: {
            "workspace_id": wid,
            "total_records": 1,
            "limit": limit,
            "offset": offset,
            "chunks": [mock_chunk],
        },
    )

    response = client.get(f"/api/v1/workspaces/{workspace_id}/knowledge-chunks?limit=5&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["workspace_id"] == str(workspace_id)
    assert body["data"]["total_records"] == 1
    assert body["data"]["chunks"][0]["chunk_type"] == "risk_short_deposit"



def test_delete_workspace_knowledge_index(client: TestClient, monkeypatch) -> None:
    workspace_id = uuid4()

    monkeypatch.setattr(
        KnowledgeIndexService,
        "delete_workspace_index",
        lambda db, wid: {
            "workspace_id": workspace_id,
            "deleted_chunks": 12,
        },
    )

    response = client.delete(f"/api/v1/workspaces/{workspace_id}/knowledge-index")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Workspace knowledge index deleted successfully."
    assert body["data"]["deleted_chunks"] == 12
