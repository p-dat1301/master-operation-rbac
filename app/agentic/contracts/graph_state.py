"""Serializable graph state for LangGraph orchestration."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import UserAccessContext
from app.agentic.contracts.answer import AnswerResult
from app.agentic.contracts.retrieval import EvidenceBundle, RetrievalRequest


class GraphState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False)

    request: RetrievalRequest
    user_context: UserAccessContext | None = None
    evidence_bundle: EvidenceBundle | None = None
    answer: AnswerResult | None = None
    audit_events: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
