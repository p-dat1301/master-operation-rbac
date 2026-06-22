"""Tests for LangChain Elasticsearch lexical retrieval helpers."""
from __future__ import annotations

import pytest
from langchain_core.documents import Document

from app.agentic.adapters.search.elasticsearch_client import (
    build_agentic_chunks_index_body,
    build_agentic_elasticsearch_retriever,
    build_bm25_query,
    build_elasticsearch_url,
    create_elasticsearch_client,
    ensure_agentic_chunks_index,
    map_elasticsearch_hit_to_document,
)

try:
    from elasticsearch import ApiError, ConnectionError as ElasticsearchConnectionError
except ImportError:  # pragma: no cover
    ApiError = Exception  # type: ignore[misc, assignment]
    ElasticsearchConnectionError = Exception  # type: ignore[misc, assignment]


@pytest.mark.parametrize(
    ("query", "expected_size"),
    [
        ("leave policy", 3),
        ("   ", 0),
    ],
)
def test_build_bm25_query_handles_regular_and_empty_queries(query: str, expected_size: int) -> None:
    body = build_bm25_query(query, top_k=3)

    assert body["size"] == expected_size
    if expected_size == 0:
        assert body["query"] == {"match_none": {}}
    else:
        assert body["query"]["match"]["text"]["query"] == "leave policy"
        assert body["query"]["match"]["text"]["operator"] == "and"


def test_index_body_includes_chunk_metadata_fields() -> None:
    body = build_agentic_chunks_index_body()

    assert body["settings"]["similarity"]["agentic_bm25"]["type"] == "BM25"
    properties = body["mappings"]["properties"]
    assert properties["text"]["type"] == "text"
    assert properties["chunk_id"]["type"] == "keyword"
    assert properties["document_id"]["type"] == "keyword"
    assert properties["citation"]["properties"]["block_anchor"]["type"] == "keyword"
    assert properties["access_policy"]["properties"]["classification"]["type"] == "keyword"


def test_map_elasticsearch_hit_to_document_returns_langchain_document() -> None:
    doc = map_elasticsearch_hit_to_document(
        {
            "_index": "agentic_chunks",
            "_id": "chunk-1",
            "_score": 1.25,
            "_source": {
                "text": "Vacation policy details",
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "source_uri": "/tmp/policy.pdf",
                "filename": "policy.pdf",
                "citation": {"page_number": 2, "section_path": ["Policies"], "block_anchor": "p2"},
                "access_policy": {"classification": "internal"},
            },
        }
    )

    assert isinstance(doc, Document)
    assert doc.page_content == "Vacation policy details"
    assert doc.metadata["chunk_id"] == "chunk-1"
    assert doc.metadata["document_id"] == "doc-1"
    assert doc.metadata["_score"] == 1.25


def test_es_retriever_returns_documents_and_handles_no_hits() -> None:
    client = create_elasticsearch_client()
    index_name = "agentic_chunks_task3_test"

    try:
        ensure_agentic_chunks_index(client, index_name=index_name)
    except (RuntimeError, ElasticsearchConnectionError, ApiError) as exc:  # pragma: no cover
        pytest.skip(f"Elasticsearch unavailable for integration check: {exc}")

    client.index(
        index=index_name,
        id="chunk-happy-path",
        document={
            "text": "Vacation carryover policy allows employees to carry over five days.",
            "chunk_id": "chunk-happy-path",
            "document_id": "doc-vacation",
            "chunk_index": 0,
            "token_count": 10,
            "source_type": "uploaded_file",
            "mime_type": "application/pdf",
            "source_uri": "/tmp/vacation.pdf",
            "filename": "vacation.pdf",
            "citation": {"page_number": 3, "section_path": ["Leave Policy"], "block_anchor": "vacation-3"},
            "access_policy": {"classification": "internal", "visibility_scope": "global", "allowed_roles": [], "policy_version": "access-policy-v1"},
            "metadata": {"source": "hr-handbook", "citation_label": "Leave Policy p.3"},
        },
        refresh="wait_for",
    )

    retriever = build_agentic_elasticsearch_retriever(client=client, index_name=index_name, top_k=5)
    docs = retriever.invoke("carry over five days")

    assert docs
    assert isinstance(docs[0], Document)
    assert docs[0].metadata["chunk_id"] == "chunk-happy-path"
    assert docs[0].metadata["document_id"] == "doc-vacation"
    assert docs[0].metadata["metadata"]["citation_label"] == "Leave Policy p.3"

    empty_docs = retriever.invoke("__definitely_no_such_chunk_should_match__")
    assert empty_docs == []

    client.options(ignore_status=404).delete(index=index_name, id="chunk-happy-path")
    client.options(ignore_status=404).indices.delete(index=index_name)


def test_es_retriever_fails_cleanly_when_cluster_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agentic.adapters.search.elasticsearch_client.settings.ELASTICSEARCH_HOST", "127.0.0.1:1")

    with pytest.raises(Exception):
        build_agentic_elasticsearch_retriever(index_name="agentic_chunks_test", top_k=2)


def test_es_retriever_preserves_minimal_metadata_for_malformed_payloads() -> None:
    doc = map_elasticsearch_hit_to_document(
        {
            "_index": "agentic_chunks",
            "_id": "chunk-malformed",
            "_score": 0.5,
            "_source": {
                "text": "Malformed metadata should still map",
                "chunk_id": "chunk-malformed",
                "document_id": "doc-malformed",
                "citation": None,
                "access_policy": {"classification": "internal"},
                "metadata": None,
            },
        }
    )

    assert doc.metadata["chunk_id"] == "chunk-malformed"
    assert doc.metadata["metadata"] is None
    assert doc.metadata["citation"] is None


def test_build_agentic_elasticsearch_retriever_uses_runtime_url() -> None:
    retriever = build_agentic_elasticsearch_retriever(index_name="agentic_chunks_test", top_k=2)

    assert retriever.index_name == "agentic_chunks_test"
    assert retriever.body_func("policy")["size"] == 2
    assert build_elasticsearch_url().startswith("http://")
