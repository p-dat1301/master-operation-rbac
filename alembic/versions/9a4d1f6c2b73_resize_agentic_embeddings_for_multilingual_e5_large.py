"""resize agentic embeddings for multilingual e5 large

Revision ID: 9a4d1f6c2b73
Revises: 7d3e2a1b9c40
Create Date: 2026-06-18 00:00:00.000000
"""
from __future__ import annotations

from alembic import op


revision = "9a4d1f6c2b73"
down_revision = "7d3e2a1b9c40"
branch_labels = None
depends_on = None


OLD_EMBEDDING_DIMENSION = 384
NEW_EMBEDDING_DIMENSION = 1024


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_agentic_chunk_embeddings_embedding_hnsw")
    op.execute("DELETE FROM agentic_chunk_embeddings")
    op.execute(
        "ALTER TABLE agentic_chunk_embeddings "
        f"ALTER COLUMN embedding TYPE vector({NEW_EMBEDDING_DIMENSION}) "
        "USING NULL::vector"
    )
    op.execute(
        "CREATE INDEX ix_agentic_chunk_embeddings_embedding_hnsw "
        "ON agentic_chunk_embeddings USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_agentic_chunk_embeddings_embedding_hnsw")
    op.execute("DELETE FROM agentic_chunk_embeddings")
    op.execute(
        "ALTER TABLE agentic_chunk_embeddings "
        f"ALTER COLUMN embedding TYPE vector({OLD_EMBEDDING_DIMENSION}) "
        "USING NULL::vector"
    )
    op.execute(
        "CREATE INDEX ix_agentic_chunk_embeddings_embedding_hnsw "
        "ON agentic_chunk_embeddings USING hnsw (embedding vector_cosine_ops)"
    )
