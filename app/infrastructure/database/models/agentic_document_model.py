"""ORM model for persisted agentic document metadata."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class AgenticDocumentModel(Base):
    """Persisted document-level metadata for the agentic RAG index."""

    __tablename__ = "agentic_documents"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ingested','parsed','chunked','indexed','failed')",
            name="ck_agentic_documents_status",
        ),
    )

    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    access_policy: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    parser_name: Mapped[str | None] = mapped_column(String, nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String, nullable=True)
    chunker_version: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    document_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    chunks = relationship(
        "AgenticChunkModel",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
