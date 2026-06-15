"""Shared retrieval payload contracts."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.chunk import RetrievalCandidate, RetrievalRequest


class RetrievalFilter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    clauses: dict[str, Any] = Field(default_factory=dict)


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    request: RetrievalRequest
    evidence: tuple[RetrievalCandidate, ...] = Field(default_factory=tuple)
    reason_code: str
