"""Audit event contracts for compliance and security tracing."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_type: Literal[
        "ingest_started",
        "ingest_completed",
        "parse_completed",
        "chunk_created",
        "retrieval_allowed",
        "retrieval_denied",
        "answer_generated",
        "answer_denied",
    ]
    actor_id: int | None = Field(default=None, ge=1)
    document_id: str | None = None
    chunk_id: str | None = None
    reason_code: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
