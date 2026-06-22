"""Gateway-backed answer LLM adapter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.agentic.adapters.llm.base import AnswerLLM
from app.core.config import settings


@dataclass(frozen=True)
class GatewayAnswerLLM(AnswerLLM):
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float = 30.0

    async def generate(self, *, query: str, evidence_text: str, citations, system_context: str | None = None) -> dict:
        if not self.base_url:
            raise RuntimeError("RAG_LLM_GATEWAY_BASE_URL is required")
        if not self.api_key:
            raise RuntimeError("RAG_LLM_GATEWAY_API_KEY is required")
        if not self.model:
            raise RuntimeError("RAG_ANSWER_MODEL is required")

        messages: list[dict[str, str]] = []
        if system_context:
            messages.append({"role": "system", "content": system_context})
        messages.append(
            {
                "role": "user",
                "content": _build_prompt(query=query, evidence_text=evidence_text, citations=citations),
            }
        )
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": 0.2}

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = (message.get("content") or "").strip()
        model_name = data.get("model") or self.model
        return {
            "status": "answered" if content else "insufficient_evidence",
            "answer": content or "Insufficient evidence.",
            "citations": citations,
            "model_name": model_name,
            "model_version": data.get("id"),
            "metadata": {
                "provider": data.get("provider"),
                "usage": data.get("usage", {}),
                "gateway_model": self.model,
            },
        }



def _build_prompt(*, query: str, evidence_text: str, citations) -> str:
    citation_lines = "\n".join(
        f"- {citation.chunk_id} | {citation.document_id} | page={citation.page_number} | sections={'.'.join(citation.section_path) if citation.section_path else '-'}"
        for citation in citations
    )
    return (
        "Answer only from the authorized evidence.\n"
        f"Question: {query}\n\n"
        f"Evidence:\n{evidence_text or 'No evidence provided.'}\n\n"
        f"Allowed citations:\n{citation_lines or '- none'}\n\n"
        "Return a grounded answer with no unsupported claims."
    )



def build_default_answer_llm() -> GatewayAnswerLLM:
    return GatewayAnswerLLM(
        base_url=settings.RAG_LLM_GATEWAY_BASE_URL,
        api_key=settings.RAG_LLM_GATEWAY_API_KEY,
        model=settings.RAG_ANSWER_MODEL,
        timeout_seconds=settings.RAG_ANSWER_TIMEOUT_SECONDS,
    )
