from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import (
    CurrentUser,
    DbSession,
    workspace_access_dependency,
    workspace_role_dependency,
)
from app.core.constants import WORKSPACE_ADMIN_ROLES
from app.core.responses import success_response
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.services.workspace_service import WorkspaceService

router = APIRouter()


def _serialize_workspace(workspace: object) -> dict:
    return WorkspaceResponse.model_validate(workspace).model_dump(mode="json")


@router.post("/clients/{client_id}/workspaces")
def create_workspace(
    client_id: UUID,
    payload: WorkspaceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    workspace = WorkspaceService.create_workspace(
        db,
        client_id,
        payload,
        owner_user_id=current_user.id,
    )
    return success_response(
        message="Workspace created successfully.",
        data=_serialize_workspace(workspace),
    )


@router.get("/clients/{client_id}/workspaces")
def list_client_workspaces(client_id: UUID, db: DbSession, current_user: CurrentUser) -> dict:
    workspaces = WorkspaceService.list_client_workspaces(
        db,
        client_id,
        user_id=current_user.id,
        is_superuser=current_user.is_superuser,
    )
    return success_response(
        message="Workspaces fetched successfully.",
        data=[_serialize_workspace(workspace) for workspace in workspaces],
    )


@router.get("/workspaces/{workspace_id}")
def get_workspace(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    workspace = WorkspaceService.get_workspace(db, workspace_id)
    return success_response(
        message="Workspace fetched successfully.",
        data=_serialize_workspace(workspace),
    )


@router.patch("/workspaces/{workspace_id}")
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    workspace = WorkspaceService.update_workspace(db, workspace_id, payload)
    return success_response(
        message="Workspace updated successfully.",
        data=_serialize_workspace(workspace),
    )


@router.delete("/workspaces/{workspace_id}")
def archive_workspace(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    workspace = WorkspaceService.archive_workspace(db, workspace_id)
    return success_response(
        message="Workspace archived successfully.",
        data=_serialize_workspace(workspace),
    )
