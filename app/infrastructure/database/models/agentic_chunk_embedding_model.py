"""ORM model for pgvector-backed agentic chunk embeddings."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

EMBEDDING_DIMENSION = 384


class AgenticChunkEmbeddingModel(Base):
    """Persisted embedding vector for a single chunk."""

    __tablename__ = "agentic_chunk_embeddings"
    __table_args__ = (
        UniqueConstraint("chunk_id", name="uq_agentic_chunk_embeddings_chunk_id"),
        Index("ix_agentic_chunk_embeddings_document_id", "document_id"),
    )

    chunk_id: Mapped[str] = mapped_column(
        ForeignKey("agentic_chunks.chunk_id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id: Mapped[str] = mapped_column(
        ForeignKey("agentic_documents.document_id", ondelete="CASCADE"),
        nullable=False,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String, nullable=False)
    index_version: Mapped[str] = mapped_column(String, nullable=False, default="index-v1")
    embedding_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    chunk = relationship("AgenticChunkModel", back_populates="embedding", lazy="joined")
