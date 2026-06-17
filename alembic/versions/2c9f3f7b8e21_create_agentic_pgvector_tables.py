"""create agentic pgvector tables

Revision ID: 2c9f3f7b8e21
Revises: f7a9c2d4e6b8
Create Date: 2026-06-17 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "2c9f3f7b8e21"
down_revision = "f7a9c2d4e6b8"
branch_labels = None
depends_on = None


EMBEDDING_DIMENSION = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "agentic_documents",
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("source", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("access_policy", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("parser_name", sa.String(), nullable=True),
        sa.Column("parser_version", sa.String(), nullable=True),
        sa.Column("chunker_version", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "status IN ('ingested','parsed','chunked','indexed','failed')",
            name="ck_agentic_documents_status",
        ),
        sa.PrimaryKeyConstraint("document_id", name=op.f("pk_agentic_documents")),
    )

    op.create_table(
        "agentic_chunks",
        sa.Column("chunk_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunker_version", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=False),
        sa.Column("citation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("access_policy", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("chunk_index >= 0", name="ck_agentic_chunks_chunk_index_non_negative"),
        sa.CheckConstraint("token_count IS NULL OR token_count >= 0", name="ck_agentic_chunks_token_count_non_negative"),
        sa.ForeignKeyConstraint(["document_id"], ["agentic_documents.document_id"], name=op.f("fk_agentic_chunks_document_id_agentic_documents"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("chunk_id", name=op.f("pk_agentic_chunks")),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_agentic_chunks_document_index"),
    )
    op.create_index("ix_agentic_chunks_document_id", "agentic_chunks", ["document_id"], unique=False)
    op.create_index("ix_agentic_chunks_document_order", "agentic_chunks", ["document_id", "chunk_index"], unique=False)
    op.create_index("ix_agentic_chunks_access_policy_gin", "agentic_chunks", ["access_policy"], postgresql_using="gin")
    op.create_index("ix_agentic_chunks_visibility_scope", "agentic_chunks", [sa.text("(access_policy ->> 'visibility_scope')")], unique=False)
    op.create_index("ix_agentic_chunks_department_id", "agentic_chunks", [sa.text("((access_policy ->> 'department_id')::int)")], unique=False)

    op.create_table(
        "agentic_chunk_embeddings",
        sa.Column("chunk_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIMENSION), nullable=False),
        sa.Column("embedding_model", sa.String(), nullable=False),
        sa.Column("index_version", sa.String(), nullable=False, server_default=sa.text("'index-v1'")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["chunk_id"], ["agentic_chunks.chunk_id"], name=op.f("fk_agentic_chunk_embeddings_chunk_id_agentic_chunks"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["agentic_documents.document_id"], name=op.f("fk_agentic_chunk_embeddings_document_id_agentic_documents"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("chunk_id", name=op.f("pk_agentic_chunk_embeddings")),
        sa.UniqueConstraint("chunk_id", name="uq_agentic_chunk_embeddings_chunk_id"),
    )
    op.create_index("ix_agentic_chunk_embeddings_document_id", "agentic_chunk_embeddings", ["document_id"], unique=False)
    op.execute(
        "CREATE INDEX ix_agentic_chunk_embeddings_embedding_hnsw "
        "ON agentic_chunk_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_agentic_chunk_embeddings_embedding_hnsw")
    op.drop_index("ix_agentic_chunk_embeddings_document_id", table_name="agentic_chunk_embeddings")
    op.drop_table("agentic_chunk_embeddings")
    op.drop_index("ix_agentic_chunks_department_id", table_name="agentic_chunks")
    op.drop_index("ix_agentic_chunks_visibility_scope", table_name="agentic_chunks")
    op.drop_index("ix_agentic_chunks_access_policy_gin", table_name="agentic_chunks")
    op.drop_index("ix_agentic_chunks_document_order", table_name="agentic_chunks")
    op.drop_index("ix_agentic_chunks_document_id", table_name="agentic_chunks")
    op.drop_table("agentic_chunks")
    op.drop_table("agentic_documents")
