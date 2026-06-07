"""add risk rule configs table

Revision ID: 11b9b8f4d2a7
Revises: 7d4f0a9b1c2e
Create Date: 2026-06-01 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11b9b8f4d2a7"
down_revision: Union[str, Sequence[str], None] = "7d4f0a9b1c2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_rule_configs",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("rule_key", sa.String(length=64), nullable=False),
        sa.Column("risk_type", sa.String(length=64), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("threshold_amount", sa.Float(), nullable=True),
        sa.Column("threshold_percent", sa.Float(), nullable=True),
        sa.Column("config_data", sa.JSON(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workspace_id",
            "rule_key",
            name="uq_risk_rule_configs_workspace_rule_key",
        ),
    )
    op.create_index(
        op.f("ix_risk_rule_configs_workspace_id"),
        "risk_rule_configs",
        ["workspace_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_risk_rule_configs_rule_key"),
        "risk_rule_configs",
        ["rule_key"],
        unique=False,
    )
    op.create_index(
        op.f("ix_risk_rule_configs_risk_type"),
        "risk_rule_configs",
        ["risk_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_risk_rule_configs_is_enabled"),
        "risk_rule_configs",
        ["is_enabled"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_rule_configs_is_enabled"), table_name="risk_rule_configs")
    op.drop_index(op.f("ix_risk_rule_configs_risk_type"), table_name="risk_rule_configs")
    op.drop_index(op.f("ix_risk_rule_configs_rule_key"), table_name="risk_rule_configs")
    op.drop_index(op.f("ix_risk_rule_configs_workspace_id"), table_name="risk_rule_configs")
    op.drop_table("risk_rule_configs")
