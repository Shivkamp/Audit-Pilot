from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    DbSession,
    risk_rule_config_access_dependency,
    workspace_access_dependency,
    workspace_role_dependency,
)
from app.core.config import settings
from app.core.constants import WORKSPACE_ADMIN_ROLES
from app.core.responses import success_response
from app.schemas.risk_rule_config import (
    RiskRuleConfigBulkUpdateRequest,
    RiskRuleConfigInitializeResponse,
    RiskRuleConfigListResponse,
    RiskRuleConfigResetResponse,
    RiskRuleConfigResponse,
    RiskRuleConfigUpdate,
)
from app.services.risk_rule_config_service import RiskRuleConfigService

router = APIRouter()


def _serialize_config(config: object) -> dict:
    return RiskRuleConfigResponse.model_validate(config).model_dump(mode="json")


@router.post("/workspaces/{workspace_id}/risk-rule-configs/initialize")
def initialize_workspace_risk_rule_configs(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    result = RiskRuleConfigService.initialize_defaults_for_workspace(db, workspace_id)
    response_data = RiskRuleConfigInitializeResponse(**result)

    return success_response(
        message="Workspace risk rule configs initialized successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/workspaces/{workspace_id}/risk-rule-configs")
def list_workspace_risk_rule_configs(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_access_dependency()),
    limit: int = Query(default=settings.risk_config_api_default_limit, ge=1),
    offset: int = Query(default=0, ge=0),
) -> dict:
    effective_limit = min(limit, settings.risk_config_api_max_limit)
    data = RiskRuleConfigService.list_workspace_configs(
        db,
        workspace_id,
        limit=effective_limit,
        offset=offset,
    )

    response_data = RiskRuleConfigListResponse(
        workspace_id=data["workspace_id"],
        total_records=data["total_records"],
        limit=data["limit"],
        offset=data["offset"],
        configs=[RiskRuleConfigResponse.model_validate(config) for config in data["configs"]],
    )

    return success_response(
        message="Workspace risk rule configs fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.get("/risk-rule-configs/{config_id}")
def get_risk_rule_config(
    config_id: UUID,
    db: DbSession,
    _: object = Depends(risk_rule_config_access_dependency()),
) -> dict:
    config = RiskRuleConfigService.get_config(db, config_id)
    response_data = RiskRuleConfigResponse.model_validate(config)

    return success_response(
        message="Risk rule config fetched successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.patch("/risk-rule-configs/{config_id}")
def update_risk_rule_config(
    config_id: UUID,
    payload: RiskRuleConfigUpdate,
    db: DbSession,
    _: object = Depends(risk_rule_config_access_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    updated_config = RiskRuleConfigService.update_config(db, config_id, payload)

    return success_response(
        message="Risk rule config updated successfully.",
        data=_serialize_config(updated_config),
    )


@router.patch("/workspaces/{workspace_id}/risk-rule-configs")
def bulk_update_workspace_risk_rule_configs(
    workspace_id: UUID,
    payload: RiskRuleConfigBulkUpdateRequest,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    data = RiskRuleConfigService.bulk_update_workspace_configs(db, workspace_id, payload)
    response_data = RiskRuleConfigListResponse(
        workspace_id=data["workspace_id"],
        total_records=data["total_records"],
        limit=data["limit"],
        offset=data["offset"],
        configs=[RiskRuleConfigResponse.model_validate(config) for config in data["configs"]],
    )

    return success_response(
        message="Workspace risk rule configs updated successfully.",
        data=response_data.model_dump(mode="json"),
    )


@router.post("/workspaces/{workspace_id}/risk-rule-configs/reset-defaults")
def reset_workspace_risk_rule_configs(
    workspace_id: UUID,
    db: DbSession,
    _: object = Depends(workspace_role_dependency(allowed_roles=WORKSPACE_ADMIN_ROLES)),
) -> dict:
    result = RiskRuleConfigService.reset_workspace_defaults(db, workspace_id)
    response_data = RiskRuleConfigResetResponse(**result)

    return success_response(
        message="Workspace risk rule configs reset to defaults successfully.",
        data=response_data.model_dump(mode="json"),
    )
