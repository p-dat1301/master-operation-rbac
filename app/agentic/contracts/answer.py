"""Answer contracts for citation-enforced responses."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.retrieval import EvidenceBundle


class AnswerCitation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    page_number: int | None = Field(default=None, ge=1)
    section_path: tuple[str, ...] = Field(default_factory=tuple)


class AnswerResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, protected_namespaces=())

    status: Literal["answered", "insufficient_evidence", "insufficient_permission", "unsupported_scope"]
    answer: str
    citations: tuple[AnswerCitation, ...] = Field(default_factory=tuple)
    evidence_bundle: EvidenceBundle | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_name: str | None = None
    model_version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
