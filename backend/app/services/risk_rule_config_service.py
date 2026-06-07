from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    ALLOWED_RISK_SEVERITIES,
    RISK_RULE_CONFIG_DEFAULTS,
    RISK_RULE_CONFIG_IMMUTABLE_FIELD,
    RISK_RULE_CONFIG_INVALID_CONFIG_DATA,
    RISK_RULE_CONFIG_INVALID_RULE_KEY,
    RISK_RULE_CONFIG_INVALID_SEVERITY,
    RISK_RULE_CONFIG_INVALID_THRESHOLD,
    RISK_RULE_CONFIG_MUTABLE_FIELDS,
    RISK_RULE_CONFIG_NOT_FOUND,
    RISK_RULE_KEY_HIGH_VALUE_TRANSACTION_V1,
    RISK_RULE_KEY_SHORT_DEPOSIT_V1,
)
from app.core.exceptions import AppException
from app.models.risk_rule_config import RiskRuleConfig
from app.repositories.risk_rule_config_repository import RiskRuleConfigRepository
from app.schemas.risk_rule_config import (
    RiskRuleConfigBulkUpdateRequest,
    RiskRuleConfigUpdate,
)
from app.services.workspace_service import WorkspaceService


class RiskRuleConfigService:
    @staticmethod
    def initialize_defaults_for_workspace(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        default_payloads = RiskRuleConfigService._build_default_payloads()
        init_result = RiskRuleConfigRepository.create_missing_defaults(
            db,
            workspace.id,
            default_payloads,
        )

        return {
            "workspace_id": workspace.id,
            "created_count": init_result["created_count"],
            "existing_count": init_result["existing_count"],
            "total_configs": init_result["total_configs"],
        }

    @staticmethod
    def list_workspace_configs(
        db: Session,
        workspace_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        safe_limit = max(1, min(limit, settings.risk_config_api_max_limit))
        safe_offset = max(0, offset)

        configs = RiskRuleConfigRepository.get_by_workspace_id(
            db,
            workspace.id,
            limit=safe_limit,
            offset=safe_offset,
        )
        total_records = RiskRuleConfigRepository.count_by_workspace(db, workspace.id)

        return {
            "workspace_id": workspace.id,
            "total_records": total_records,
            "limit": safe_limit,
            "offset": safe_offset,
            "configs": configs,
        }

    @staticmethod
    def get_config(db: Session, config_id: UUID) -> RiskRuleConfig:
        config = RiskRuleConfigRepository.get_by_id(db, config_id)
        if config is None:
            raise AppException(
                message="Risk rule config not found.",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=RISK_RULE_CONFIG_NOT_FOUND,
            )
        return config

    @staticmethod
    def update_config(
        db: Session,
        config_id: UUID,
        payload: RiskRuleConfigUpdate,
    ) -> RiskRuleConfig:
        config = RiskRuleConfigService.get_config(db, config_id)

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return config

        RiskRuleConfigService._validate_update_payload(update_data)
        return RiskRuleConfigRepository.update(db, config, update_data)

    @staticmethod
    def bulk_update_workspace_configs(
        db: Session,
        workspace_id: UUID,
        payload: RiskRuleConfigBulkUpdateRequest,
    ) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)
        RiskRuleConfigService.initialize_defaults_for_workspace(db, workspace.id)

        existing_config_map = RiskRuleConfigRepository.get_configs_by_workspace_as_map(
            db,
            workspace.id,
        )

        updates_by_rule_key: dict[str, dict] = {}
        for item in payload.configs:
            item_data = item.model_dump(exclude_unset=True)
            rule_key = item_data.pop("rule_key")

            if rule_key not in existing_config_map:
                raise AppException(
                    message=f"Risk rule key '{rule_key}' is not configured for this workspace.",
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_code=RISK_RULE_CONFIG_INVALID_RULE_KEY,
                )

            if not item_data:
                continue

            RiskRuleConfigService._validate_update_payload(item_data)
            updates_by_rule_key[rule_key] = item_data

        if updates_by_rule_key:
            RiskRuleConfigRepository.bulk_update_by_rule_key(
                db,
                workspace.id,
                updates_by_rule_key,
            )

        return RiskRuleConfigService.list_workspace_configs(
            db,
            workspace.id,
            limit=settings.risk_config_api_max_limit,
            offset=0,
        )

    @staticmethod
    def reset_workspace_defaults(db: Session, workspace_id: UUID) -> dict:
        workspace = WorkspaceService.get_workspace(db, workspace_id)

        RiskRuleConfigRepository.delete_by_workspace_id(db, workspace.id)
        RiskRuleConfigService.initialize_defaults_for_workspace(db, workspace.id)

        total_configs = RiskRuleConfigRepository.count_by_workspace(db, workspace.id)
        return {
            "workspace_id": workspace.id,
            "total_configs": total_configs,
        }

    @staticmethod
    def get_config_map_for_workspace(db: Session, workspace_id: UUID) -> dict[str, dict]:
        WorkspaceService.get_workspace(db, workspace_id)
        config_map = RiskRuleConfigRepository.get_configs_by_workspace_as_map(db, workspace_id)
        return {
            rule_key: RiskRuleConfigService._serialize_config_for_runtime(config)
            for rule_key, config in config_map.items()
        }

    @staticmethod
    def _validate_update_payload(update_data: dict) -> None:
        immutable_fields = {"rule_key", "risk_type"}
        provided_immutable = immutable_fields.intersection(update_data.keys())
        if provided_immutable:
            raise AppException(
                message="rule_key and risk_type cannot be modified.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=RISK_RULE_CONFIG_IMMUTABLE_FIELD,
            )

        unknown_fields = set(update_data.keys()) - RISK_RULE_CONFIG_MUTABLE_FIELDS
        if unknown_fields:
            raise AppException(
                message="Unsupported fields in risk rule config update payload.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=RISK_RULE_CONFIG_IMMUTABLE_FIELD,
            )

        severity = update_data.get("severity")
        if severity is not None and severity not in ALLOWED_RISK_SEVERITIES:
            raise AppException(
                message="Invalid risk severity.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=RISK_RULE_CONFIG_INVALID_SEVERITY,
            )

        for field_name in ("threshold_amount", "threshold_percent"):
            field_value = update_data.get(field_name)
            if field_value is not None and field_value < 0:
                raise AppException(
                    message=f"{field_name} must be non-negative.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_code=RISK_RULE_CONFIG_INVALID_THRESHOLD,
                )

        config_data = update_data.get("config_data")
        if config_data is not None and not isinstance(config_data, dict):
            raise AppException(
                message="config_data must be an object.",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=RISK_RULE_CONFIG_INVALID_CONFIG_DATA,
            )

    @staticmethod
    def _build_default_payloads() -> list[dict]:
        payloads = deepcopy(list(RISK_RULE_CONFIG_DEFAULTS))

        for payload in payloads:
            if payload["rule_key"] == RISK_RULE_KEY_SHORT_DEPOSIT_V1:
                threshold = float(settings.default_short_deposit_critical_threshold)
                payload["threshold_amount"] = threshold
                payload["config_data"] = {
                    **(payload.get("config_data") or {}),
                    "critical_threshold_amount": threshold,
                }

            if payload["rule_key"] == RISK_RULE_KEY_HIGH_VALUE_TRANSACTION_V1:
                payload["threshold_amount"] = float(settings.default_high_value_transaction_threshold)

        return payloads

    @staticmethod
    def _serialize_config_for_runtime(config: RiskRuleConfig) -> dict:
        return {
            "id": config.id,
            "workspace_id": config.workspace_id,
            "rule_key": config.rule_key,
            "risk_type": config.risk_type,
            "is_enabled": config.is_enabled,
            "severity": config.severity,
            "threshold_amount": config.threshold_amount,
            "threshold_percent": config.threshold_percent,
            "config_data": config.config_data or {},
        }
