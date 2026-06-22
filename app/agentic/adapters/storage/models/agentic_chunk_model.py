"""ORM model for persisted agentic document chunks."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class AgenticChunkModel(Base):
    """Persisted chunk text, citation, and access metadata."""

    __tablename__ = "agentic_chunks"
    __table_args__ = (
        CheckConstraint("chunk_index >= 0", name="ck_agentic_chunks_chunk_index_non_negative"),
        CheckConstraint("token_count IS NULL OR token_count >= 0", name="ck_agentic_chunks_token_count_non_negative"),
        UniqueConstraint("document_id", "chunk_index", name="uq_agentic_chunks_document_index"),
        Index("ix_agentic_chunks_document_id", "document_id"),
        Index("ix_agentic_chunks_document_order", "document_id", "chunk_index"),
        Index("ix_agentic_chunks_access_policy_gin", "access_policy", postgresql_using="gin"),
        Index("ix_agentic_chunks_visibility_scope", text("(access_policy ->> 'visibility_scope')")),
        Index("ix_agentic_chunks_department_id", text("((access_policy ->> 'department_id')::int)")),
    )

    chunk_id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("agentic_documents.document_id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunker_version: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    citation: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    access_policy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    chunk_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    document = relationship("AgenticDocumentModel", back_populates="chunks", lazy="joined")
    embedding = relationship(
        "AgenticChunkEmbeddingModel",
        back_populates="chunk",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
