"""Unit tests for Task 9 LangGraph orchestration state hygiene."""
from __future__ import annotations

import pytest

from app.agentic.contracts.access_policy import (
    AccessPolicyMetadata,
    Classification,
    UserAccessContext,
    VisibilityScope,
)
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalRequest
from app.agentic.contracts.document import CitationMetadata
from app.agentic.contracts.graph_state import GraphState
from app.agentic.orchestration.rag_graph import build_rag_graph, invoke_rag_graph, load_checkpointed_state
from app.agentic.adapters.checkpoint.inmemory_checkpointer import build_inmemory_checkpointer


class FakeAnswerLLM:
    async def generate(self, *, query: str, evidence_text: str, citations, system_context: str | None = None) -> dict:
        return {
            "status": "answered",
            "answer": f"Answered: {query}",
            "citations": citations,
            "model_name": "fake-gateway-model",
            "model_version": "fake-v1",
            "metadata": {"gateway": "test"},
        }


class FakeRetrievalStore:
    async def search(self, request: RetrievalRequest, retrieval_filter, *, top_k: int) -> list[RetrievalCandidate]:
        chunk = DocumentChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            text="authorized evidence",
            token_count=10,
            chunk_index=0,
            chunker_version="chunker-v1",
            source_type="pdf",
            mime_type="application/pdf",
            citation=CitationMetadata(page_number=1, section_path=("Section",), block_anchor="anchor-1"),
            access_policy=AccessPolicyMetadata(
                classification=Classification.PUBLIC,
                visibility_scope=VisibilityScope.GLOBAL,
            ),
        )
        return [RetrievalCandidate(chunk=chunk, score=1.0, rank=1)]

    async def fetch_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return []

    async def fetch_by_document_ids(self, document_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return []


class FakeLangfuseLogger:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    async def log_retrieved_chunks(self, *, trace_id, request, candidates, reason_code) -> None:
        self.payloads.append(
            {
                "trace_id": trace_id,
                "query": request.query,
                "reason_code": reason_code,
                "chunks": [candidate.chunk.model_dump(mode="json") for candidate in candidates],
            }
        )


@pytest.mark.asyncio
async def test_inmemory_graph_returns_citations_without_persisting_raw_evidence() -> None:
    logger = FakeLangfuseLogger()
    graph = build_rag_graph(
        checkpointer=build_inmemory_checkpointer(),
        retrieval_store=FakeRetrievalStore(),
        answer_llm=FakeAnswerLLM(),
        langfuse_logger=logger,
    )
    state = GraphState(
        request=RetrievalRequest(query="hello", top_k=3),
        user_context=UserAccessContext(user_id=1),
        conversation_id="conv-1",
        metadata={"langfuse_trace_id": "trace-1"},
    )

    result = await invoke_rag_graph(graph, state, thread_id="thr-test")

    assert result.last_answer_status == "answered"
    assert len(result.last_citations) == 1
    assert result.last_cited_chunk_ids == ("chunk-1",)
    assert result.last_cited_document_ids == ("doc-1",)
    assert result.answer is not None
    assert result.answer.evidence_bundle is None
    assert len(logger.payloads) == 1
    assert logger.payloads[0]["trace_id"] == "trace-1"
    assert logger.payloads[0]["query"] == "hello"
    assert logger.payloads[0]["reason_code"] == "ok"
    assert logger.payloads[0]["chunks"][0]["chunk_id"] == "chunk-1"
    assert logger.payloads[0]["chunks"][0]["text"] == "authorized evidence"

    checkpointed_state = await load_checkpointed_state(graph, "thr-test")

    assert checkpointed_state is not None
    assert checkpointed_state.thread_id == "thr-test"
    assert checkpointed_state.last_answer_status == "answered"
    assert checkpointed_state.last_cited_chunk_ids == ("chunk-1",)
    assert await load_checkpointed_state(graph, "thr-other") is None
