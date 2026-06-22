"""Answer LLM adapter boundary."""
from __future__ import annotations

from typing import Protocol

from app.agentic.contracts.answer import AnswerCitation


class AnswerLLMResponse(Protocol):
    status: str
    answer: str
    citations: tuple[AnswerCitation, ...]
    model_name: str | None
    model_version: str | None
    metadata: dict[str, object]


class AnswerLLM(Protocol):
    async def generate(self, *, query: str, evidence_text: str, citations: tuple[AnswerCitation, ...], system_context: str | None = None) -> dict:
        ...
