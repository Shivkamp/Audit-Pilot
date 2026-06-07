from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, workspace_access_dependency
from app.core.responses import success_response
from app.schemas.agent_chat import AgentChatRequest, AgentChatResponse
from app.services.agent_chat_service import AgentChatService

router = APIRouter()


@router.post("/workspaces/{workspace_id}/agent-chat")
def workspace_agent_chat(
    workspace_id: UUID,
    payload: AgentChatRequest,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    result = AgentChatService(db).chat_workspace(workspace_id, payload)
    response_data = AgentChatResponse(**result)

    return success_response(
        message="Workspace agent chat response generated successfully.",
        data=response_data.model_dump(mode="json"),
    )
