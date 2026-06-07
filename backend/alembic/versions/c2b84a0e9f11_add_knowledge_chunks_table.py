"""add knowledge chunks table

Revision ID: c2b84a0e9f11
Revises: 11b9b8f4d2a7
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2b84a0e9f11"
down_revision: Union[str, Sequence[str], None] = "11b9b8f4d2a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_chunks",
        sa.Column("workspace_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("chunk_type", sa.String(length=100), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("chunk_metadata", sa.JSON(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("embedding_model", sa.String(length=100), nullable=True),
        sa.Column("embedding_provider", sa.String(length=50), nullable=True),
        sa.Column("embedding_status", sa.String(length=20), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("embedding_error", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_knowledge_chunks_workspace_id"), "knowledge_chunks", ["workspace_id"], unique=False)
    op.create_index(op.f("ix_knowledge_chunks_document_id"), "knowledge_chunks", ["document_id"], unique=False)
    op.create_index(op.f("ix_knowledge_chunks_source_type"), "knowledge_chunks", ["source_type"], unique=False)
    op.create_index(op.f("ix_knowledge_chunks_source_id"), "knowledge_chunks", ["source_id"], unique=False)
    op.create_index(op.f("ix_knowledge_chunks_chunk_type"), "knowledge_chunks", ["chunk_type"], unique=False)
    op.create_index(op.f("ix_knowledge_chunks_embedding_status"), "knowledge_chunks", ["embedding_status"], unique=False)
    op.create_index("ix_knowledge_chunks_created_at", "knowledge_chunks", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_created_at", table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_embedding_status"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_chunk_type"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_source_id"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_source_type"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_document_id"), table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_workspace_id"), table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
