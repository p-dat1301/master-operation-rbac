"""Chunk and retrieval-oriented contracts."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.document import CitationMetadata


class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    token_count: int | None = Field(default=None, ge=0)
    chunk_index: int = Field(ge=0)
    chunker_version: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    citation: CitationMetadata
    access_policy: AccessPolicyMetadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunk: DocumentChunk
    score: float
    rank: int = Field(ge=1)


class RetrievalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: dict[str, Any] = Field(default_factory=dict)


class RetrievalOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["ok", "no_evidence", "denied"]
    candidates: tuple[RetrievalCandidate, ...] = Field(default_factory=tuple)
    reason_code: str
