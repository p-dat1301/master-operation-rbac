"""Serializable graph state for LangGraph orchestration."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import UserAccessContext
from app.agentic.contracts.answer import AnswerResult
from app.agentic.contracts.retrieval import RetrievalRequest


class GraphState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=False)

    request: RetrievalRequest
    conversation_id: str | None = None
    thread_id: str | None = None
    user_id: int | None = None
    current_turn_id: str | None = None
    current_turn_index: int | None = None
    current_user_message: str | None = None
    recent_messages: list[dict[str, Any]] = Field(default_factory=list)
    memory_summary: str | None = None
    current_topic: str | None = None
    recent_cited_document_ids: tuple[str, ...] = Field(default_factory=tuple)
    recent_cited_chunk_ids: tuple[str, ...] = Field(default_factory=tuple)
    retrieval_candidate_count: int = 0
    retrieval_reason_code: str | None = None
    last_user_question: str | None = None
    last_answer_status: str | None = None
    last_cited_document_ids: tuple[str, ...] = Field(default_factory=tuple)
    last_cited_chunk_ids: tuple[str, ...] = Field(default_factory=tuple)
    last_citations: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    retrieval_hints: dict[str, Any] = Field(default_factory=dict)
    user_context: UserAccessContext | None = None
    answer: AnswerResult | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def langfuse_trace_id(self) -> str | None:
        value = self.metadata.get("langfuse_trace_id")
        return value if isinstance(value, str) else None

    @langfuse_trace_id.setter
    def langfuse_trace_id(self, value: str | None) -> None:
        if value is None:
            self.metadata.pop("langfuse_trace_id", None)
            return
        self.metadata["langfuse_trace_id"] = value

    @property
    def audit_events(self) -> list[dict[str, Any]]:
        value = self.metadata.get("audit_events")
        return list(value) if isinstance(value, list) else []

    @audit_events.setter
    def audit_events(self, value: list[dict[str, Any]]) -> None:
        self.metadata["audit_events"] = value

    @property
    def query_rewritten(self) -> str | None:
        value = self.metadata.get("query_rewritten")
        return value if isinstance(value, str) else None

    @query_rewritten.setter
    def query_rewritten(self, value: str | None) -> None:
        if value is None:
            self.metadata.pop("query_rewritten", None)
            return
        self.metadata["query_rewritten"] = value

    @property
    def policy_version(self) -> str | None:
        value = self.metadata.get("policy_version")
        return value if isinstance(value, str) else None

    @policy_version.setter
    def policy_version(self, value: str | None) -> None:
        if value is None:
            self.metadata.pop("policy_version", None)
            return
        self.metadata["policy_version"] = value

    @property
    def index_version(self) -> str | None:
        value = self.metadata.get("index_version")
        return value if isinstance(value, str) else None

    @index_version.setter
    def index_version(self, value: str | None) -> None:
        if value is None:
            self.metadata.pop("index_version", None)
            return
        self.metadata["index_version"] = value

    @property
    def expires_at(self) -> str | None:
        value = self.metadata.get("expires_at")
        return value if isinstance(value, str) else None

    @expires_at.setter
    def expires_at(self, value: str | None) -> None:
        if value is None:
            self.metadata.pop("expires_at", None)
            return
        self.metadata["expires_at"] = value
