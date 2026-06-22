"""create rag conversations registry

Revision ID: e4f1b2c3d4a5
Revises: 9a4d1f6c2b73
Create Date: 2026-06-18 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e4f1b2c3d4a5"
down_revision = "9a4d1f6c2b73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rag_conversations",
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'active'")),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_reason", sa.String(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint("status IN ('active','ended','expired')", name="ck_rag_conversations_status"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_rag_conversations_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("conversation_id", name=op.f("pk_rag_conversations")),
        sa.UniqueConstraint("thread_id", name="uq_rag_conversations_thread_id"),
    )
    op.create_index("ix_rag_conversations_user_id", "rag_conversations", ["user_id"], unique=False)
    op.create_index("ix_rag_conversations_thread_id", "rag_conversations", ["thread_id"], unique=False)
    op.create_index("ix_rag_conversations_expires_at", "rag_conversations", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rag_conversations_expires_at", table_name="rag_conversations")
    op.drop_index("ix_rag_conversations_thread_id", table_name="rag_conversations")
    op.drop_index("ix_rag_conversations_user_id", table_name="rag_conversations")
    op.drop_table("rag_conversations")
