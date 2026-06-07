from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, workspace_access_dependency, workspace_role_dependency
from app.core.config import settings
from app.core.constants import WORKSPACE_ADMIN_ROLES, WORKSPACE_WRITE_ROLES
from app.core.responses import success_response
from app.schemas.knowledge import (
    KnowledgeChunkListResponse,
    KnowledgeChunkResponse,
    KnowledgeIndexDeleteResponse,
    KnowledgeIndexRebuildResponse,
    KnowledgeIndexSummaryResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
)
from app.services.knowledge_index_service import KnowledgeIndexService
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/workspaces/{workspace_id}/knowledge-index/rebuild")
def rebuild_workspace_knowledge_index(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_WRITE_ROLES)),
) -> dict:
    result = KnowledgeIndexService.rebuild_workspace_index(db, workspace_id)
    response_data = KnowledgeIndexRebuildResponse(**result)

    return success_response(
        message="Workspace knowledge index rebuilt successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/knowledge-index/summary")
def get_workspace_knowledge_index_summary(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    result = KnowledgeIndexService.get_workspace_index_summary(db, workspace_id)
    response_data = KnowledgeIndexSummaryResponse(**result)

    return success_response(
        message="Workspace knowledge index summary fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/workspaces/{workspace_id}/knowledge-search")
def search_workspace_knowledge(
    workspace_id: UUID,
    payload: KnowledgeSearchRequest,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    effective_limit = min(payload.limit, settings.knowledge_search_max_limit)
    if payload.include_retrieval_debug:
        result = RetrievalService.search_workspace(
            db,
            workspace_id,
            payload.query,
            effective_limit,
            retrieval_options={
                "include_retrieval_debug": True,
            },
        )
    else:
        result = RetrievalService.search_workspace(
            db,
            workspace_id,
            payload.query,
            effective_limit,
        )

    response_data = KnowledgeSearchResponse(
        workspace_id=result["workspace_id"],
        query=result["query"],
        limit=result["limit"],
        results=[KnowledgeSearchResult(**item) for item in result["results"]],
    )

    return success_response(
        message="Workspace knowledge search completed successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/knowledge-chunks")
def list_workspace_knowledge_chunks(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
    source_type: str | None = Query(default=None),
    chunk_type: str | None = Query(default=None),
    embedding_status: str | None = Query(default=None),
    limit: int = Query(default=settings.knowledge_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
) -> dict:
    effective_limit = min(limit, settings.knowledge_api_max_limit)
    result = KnowledgeIndexService.list_workspace_chunks(
        db,
        workspace_id,
        source_type=source_type,
        chunk_type=chunk_type,
        embedding_status=embedding_status,
        limit=effective_limit,
        offset=offset,
    )

    response_data = KnowledgeChunkListResponse(
        workspace_id=result["workspace_id"],
        total_records=result["total_records"],
        limit=result["limit"],
        offset=result["offset"],
        chunks=[
            KnowledgeChunkResponse.model_validate(chunk)
            for chunk in result["chunks"]
        ],
    )

    return success_response(
        message="Workspace knowledge chunks fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.delete("/workspaces/{workspace_id}/knowledge-index")
def delete_workspace_knowledge_index(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    result = KnowledgeIndexService.delete_workspace_index(db, workspace_id)
    response_data = KnowledgeIndexDeleteResponse(**result)

    return success_response(
        message="Workspace knowledge index deleted successfully.",
        data=response_data.model_dump(mode="json"),
    )
