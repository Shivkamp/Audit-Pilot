"""add risk findings table

Revision ID: 7d4f0a9b1c2e
Revises: 934f476aac3d
Create Date: 2026-06-01 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d4f0a9b1c2e"
down_revision: Union[str, Sequence[str], None] = "934f476aac3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_findings",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=True),
        sa.Column("primary_normalized_record_id", sa.UUID(), nullable=True),
        sa.Column("related_normalized_record_ids", sa.JSON(), nullable=True),
        sa.Column("risk_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("risk_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'open'"), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["primary_normalized_record_id"], ["normalized_records.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_findings_workspace_id"), "risk_findings", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_risk_findings_document_id"), "risk_findings", ["document_id"], unique=False)
    op.create_index(op.f("ix_risk_findings_risk_type"), "risk_findings", ["risk_type"], unique=False)
    op.create_index(op.f("ix_risk_findings_severity"), "risk_findings", ["severity"], unique=False)
    op.create_index(op.f("ix_risk_findings_status"), "risk_findings", ["status"], unique=False)
    op.create_index("ix_risk_findings_created_at", "risk_findings", ["created_at"], unique=False)
    op.create_index(
        op.f("ix_risk_findings_primary_normalized_record_id"),
        "risk_findings",
        ["primary_normalized_record_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_risk_findings_primary_normalized_record_id"), table_name="risk_findings")
    op.drop_index("ix_risk_findings_created_at", table_name="risk_findings")
    op.drop_index(op.f("ix_risk_findings_status"), table_name="risk_findings")
    op.drop_index(op.f("ix_risk_findings_severity"), table_name="risk_findings")
    op.drop_index(op.f("ix_risk_findings_risk_type"), table_name="risk_findings")
    op.drop_index(op.f("ix_risk_findings_document_id"), table_name="risk_findings")
    op.drop_index(op.f("ix_risk_findings_workspace_id"), table_name="risk_findings")
    op.drop_table("risk_findings")
