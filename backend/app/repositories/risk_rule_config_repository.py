from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.risk_rule_config import RiskRuleConfig


class RiskRuleConfigRepository:
    @staticmethod
    def create(db: Session, payload: dict) -> RiskRuleConfig:
        config = RiskRuleConfig(**payload)
        db.add(config)
        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def bulk_create(db: Session, payloads: Sequence[dict]) -> int:
        if not payloads:
            return 0

        configs = [RiskRuleConfig(**payload) for payload in payloads]
        db.add_all(configs)
        db.commit()
        return len(configs)

    @staticmethod
    def get_by_id(db: Session, config_id: UUID) -> RiskRuleConfig | None:
        return db.scalar(select(RiskRuleConfig).where(RiskRuleConfig.id == config_id))

    @staticmethod
    def get_by_workspace_id(
        db: Session,
        workspace_id: UUID,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[RiskRuleConfig]:
        statement = (
            select(RiskRuleConfig)
            .where(RiskRuleConfig.workspace_id == workspace_id)
            .order_by(RiskRuleConfig.rule_key.asc(), RiskRuleConfig.id.asc())
        )

        if offset is not None:
            statement = statement.offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        return list(db.scalars(statement))

    @staticmethod
    def get_by_workspace_and_rule_key(
        db: Session,
        workspace_id: UUID,
        rule_key: str,
    ) -> RiskRuleConfig | None:
        return db.scalar(
            select(RiskRuleConfig).where(
                RiskRuleConfig.workspace_id == workspace_id,
                RiskRuleConfig.rule_key == rule_key,
            )
        )

    @staticmethod
    def get_configs_by_workspace_as_map(
        db: Session,
        workspace_id: UUID,
    ) -> dict[str, RiskRuleConfig]:
        configs = RiskRuleConfigRepository.get_by_workspace_id(db, workspace_id)
        return {config.rule_key: config for config in configs}

    @staticmethod
    def update(db: Session, config: RiskRuleConfig, payload: dict) -> RiskRuleConfig:
        for field, value in payload.items():
            setattr(config, field, value)

        db.commit()
        db.refresh(config)
        return config

    @staticmethod
    def bulk_update_by_rule_key(
        db: Session,
        workspace_id: UUID,
        payload_by_rule_key: dict[str, dict],
    ) -> int:
        if not payload_by_rule_key:
            return 0

        configs = RiskRuleConfigRepository.get_by_workspace_id(db, workspace_id)
        updated_count = 0

        for config in configs:
            update_payload = payload_by_rule_key.get(config.rule_key)
            if update_payload is None:
                continue

            for field, value in update_payload.items():
                setattr(config, field, value)
            updated_count += 1

        if updated_count > 0:
            db.commit()

        return updated_count

    @staticmethod
    def delete_by_workspace_id(db: Session, workspace_id: UUID) -> int:
        result = db.execute(
            delete(RiskRuleConfig).where(RiskRuleConfig.workspace_id == workspace_id)
        )
        db.commit()
        return int(result.rowcount or 0)

    @staticmethod
    def count_by_workspace(db: Session, workspace_id: UUID) -> int:
        statement = select(func.count(RiskRuleConfig.id)).where(
            RiskRuleConfig.workspace_id == workspace_id
        )
        return int(db.scalar(statement) or 0)

    @staticmethod
    def create_missing_defaults(
        db: Session,
        workspace_id: UUID,
        default_payloads: Sequence[dict],
    ) -> dict[str, int]:
        existing_configs = RiskRuleConfigRepository.get_by_workspace_id(db, workspace_id)
        existing_rule_keys = {config.rule_key for config in existing_configs}

        payloads_to_create: list[dict] = []
        for default_payload in default_payloads:
            rule_key = str(default_payload.get("rule_key") or "")
            if rule_key in existing_rule_keys:
                continue

            payload = {
                **default_payload,
                "workspace_id": workspace_id,
            }
            payloads_to_create.append(payload)

        created_count = 0
        if payloads_to_create:
            try:
                created_count = RiskRuleConfigRepository.bulk_create(db, payloads_to_create)
            except IntegrityError:
                db.rollback()
                created_count = 0

        total_configs = RiskRuleConfigRepository.count_by_workspace(db, workspace_id)
        existing_count = max(total_configs - created_count, 0)

        return {
            "created_count": created_count,
            "existing_count": existing_count,
            "total_configs": total_configs,
        }
