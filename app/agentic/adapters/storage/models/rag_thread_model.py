"""ORM model for app-level RAG turn history."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class RagTurnModel(Base):
    """Metadata and lightweight history for one user/assistant RAG turn."""

    __tablename__ = "rag_turns"
    __table_args__ = (
        CheckConstraint(
            "assistant_status IN ('pending','answered','denied','insufficient_evidence','unsupported_scope','error')",
            name="ck_rag_turns_assistant_status",
        ),
        UniqueConstraint("conversation_id", "turn_index", name="uq_rag_turns_conversation_turn_index"),
        Index("ix_rag_turns_conversation_id", "conversation_id"),
        Index("ix_rag_turns_created_at", "created_at"),
        Index("ix_rag_turns_langfuse_trace_id", "langfuse_trace_id"),
    )

    turn_id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("rag_conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
    )
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    assistant_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    query_rewritten: Mapped[str | None] = mapped_column(Text, nullable=True)
    cited_chunk_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    cited_document_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    answer_citations: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    langfuse_trace_id: Mapped[str | None] = mapped_column(String, nullable=True)
    langfuse_observation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    turn_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
