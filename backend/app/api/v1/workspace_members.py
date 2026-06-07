from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession, workspace_access_dependency, workspace_role_dependency
from app.core.constants import (
    WORKSPACE_ACCESS_DENIED,
    WORKSPACE_ADMIN_ROLES,
    WORKSPACE_ROLE_ADMIN,
    WORKSPACE_ROLE_EDITOR,
    WORKSPACE_ROLE_OWNER,
    WORKSPACE_ROLE_VIEWER,
)
from app.core.exceptions import AppException
from app.core.responses import success_response
from app.schemas.workspace_member import (
    WorkspaceMemberCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceMemberUpdateRequest,
    WorkspaceMyMembershipResponse,
)
from app.services.workspace_access_service import WorkspaceAccessService
from app.services.workspace_member_service import WorkspaceMemberService

router = APIRouter()

_ROLE_PERMISSIONS: dict[str, dict[str, bool]] = {
    WORKSPACE_ROLE_OWNER: {
        "can_upload_documents": True,
        "can_delete_documents": True,
        "can_retry_jobs": True,
        "can_run_risk_check": True,
        "can_update_risk_finding": True,
        "can_configure_risk_rules": True,
        "can_manage_members": True,
        "can_rebuild_knowledge_index": True,
        "can_delete_knowledge_index": True,
        "can_use_agent": True,
    },
    WORKSPACE_ROLE_ADMIN: {
        "can_upload_documents": True,
        "can_delete_documents": True,
        "can_retry_jobs": True,
        "can_run_risk_check": True,
        "can_update_risk_finding": True,
        "can_configure_risk_rules": True,
        "can_manage_members": True,
        "can_rebuild_knowledge_index": True,
        "can_delete_knowledge_index": True,
        "can_use_agent": True,
    },
    WORKSPACE_ROLE_EDITOR: {
        "can_upload_documents": True,
        "can_delete_documents": False,
        "can_retry_jobs": True,
        "can_run_risk_check": True,
        "can_update_risk_finding": True,
        "can_configure_risk_rules": False,
        "can_manage_members": False,
        "can_rebuild_knowledge_index": True,
        "can_delete_knowledge_index": False,
        "can_use_agent": True,
    },
    WORKSPACE_ROLE_VIEWER: {
        "can_upload_documents": False,
        "can_delete_documents": False,
        "can_retry_jobs": False,
        "can_run_risk_check": False,
        "can_update_risk_finding": False,
        "can_configure_risk_rules": False,
        "can_manage_members": False,
        "can_rebuild_knowledge_index": False,
        "can_delete_knowledge_index": False,
        "can_use_agent": True,
    },
}


def _serialize_member(member: object) -> dict:
    return WorkspaceMemberResponse.model_validate(member).model_dump(mode="json")


@router.get("/workspaces/{workspace_id}/my-membership")
def get_my_workspace_membership(
    workspace_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    membership = WorkspaceAccessService.get_membership(db, workspace_id, current_user.id)
    if membership is None:
        raise AppException(
            message="You do not have access to this workspace.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=WORKSPACE_ACCESS_DENIED,
        )
    permissions = _ROLE_PERMISSIONS.get(membership.role, {})
    return success_response(
        message="Workspace membership fetched successfully.",
        data=WorkspaceMyMembershipResponse(
            workspace_id=membership.workspace_id,
            user_id=membership.user_id,
            role=membership.role,
            permissions=permissions,
        ).model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/members")
def list_workspace_members(
    workspace_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: object = Depends(workspace_access_dependency()),
) -> dict:
    members = WorkspaceMemberService.list_workspace_members(db, workspace_id, current_user)
    return success_response(
        message="Workspace members fetched successfully.",
        data=[_serialize_member(member) for member in members],
    )


@router.post("/workspaces/{workspace_id}/members")
def add_workspace_member(
    workspace_id: UUID,
    payload: WorkspaceMemberCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    member = WorkspaceMemberService.add_workspace_member(
        db,
        workspace_id,
        current_user,
        email=payload.email,
        role=payload.role,
    )
    return success_response(
        message="Workspace member added successfully.",
        data=_serialize_member(member),
    )


@router.patch("/workspaces/{workspace_id}/members/{member_id}")
def update_workspace_member_role(
    workspace_id: UUID,
    member_id: UUID,
    payload: WorkspaceMemberUpdateRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    member = WorkspaceMemberService.update_workspace_member_role(
        db,
        workspace_id,
        member_id,
        current_user,
        role=payload.role,
    )
    return success_response(
        message="Workspace member role updated successfully.",
        data=_serialize_member(member),
    )


@router.delete("/workspaces/{workspace_id}/members/{member_id}")
def remove_workspace_member(
    workspace_id: UUID,
    member_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    member = WorkspaceMemberService.remove_workspace_member(
        db,
        workspace_id,
        member_id,
        current_user,
    )
    return success_response(
        message="Workspace member removed successfully.",
        data=_serialize_member(member),
    )
