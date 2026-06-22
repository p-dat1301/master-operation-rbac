"""create rag turns registry

Revision ID: b6f2c8d9e1a0
Revises: e4f1b2c3d4a5
Create Date: 2026-06-19 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b6f2c8d9e1a0"
down_revision = "e4f1b2c3d4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rag_turns",
        sa.Column("turn_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("turn_index", sa.Integer(), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("assistant_message", sa.Text(), nullable=True),
        sa.Column("assistant_status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("query_rewritten", sa.Text(), nullable=True),
        sa.Column("cited_chunk_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("cited_document_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("answer_citations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("langfuse_trace_id", sa.String(), nullable=True),
        sa.Column("langfuse_observation_id", sa.String(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint(
            "assistant_status IN ('pending','answered','denied','insufficient_evidence','unsupported_scope','error')",
            name="ck_rag_turns_assistant_status",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["rag_conversations.conversation_id"],
            name=op.f("fk_rag_turns_conversation_id_rag_conversations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("turn_id", name=op.f("pk_rag_turns")),
        sa.UniqueConstraint("conversation_id", "turn_index", name="uq_rag_turns_conversation_turn_index"),
    )
    op.create_index("ix_rag_turns_conversation_id", "rag_turns", ["conversation_id"], unique=False)
    op.create_index("ix_rag_turns_created_at", "rag_turns", ["created_at"], unique=False)
    op.create_index("ix_rag_turns_langfuse_trace_id", "rag_turns", ["langfuse_trace_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_rag_turns_langfuse_trace_id", table_name="rag_turns")
    op.drop_index("ix_rag_turns_created_at", table_name="rag_turns")
    op.drop_index("ix_rag_turns_conversation_id", table_name="rag_turns")
    op.drop_table("rag_turns")
