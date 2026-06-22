"""LangChain Elasticsearch lexical retriever helpers for agentic RAG."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from app.core.config import settings
from langchain_core.documents import Document

try:  # pragma: no cover - exercised in environments with optional ES deps installed
    from elasticsearch import Elasticsearch
    from langchain_elasticsearch import ElasticsearchRetriever
except ImportError:  # pragma: no cover
    Elasticsearch = Any  # type: ignore[misc, assignment]
    ElasticsearchRetriever = Any  # type: ignore[misc, assignment]


CHUNK_TEXT_FIELD = "text"
DEFAULT_TOP_K = 5

AGENTIC_CHUNKS_INDEX_BODY: dict[str, Any] = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "agentic_bm25_text": {
                    "type": "standard",
                    "stopwords": "_english_",
                }
            }
        },
        "similarity": {
            "agentic_bm25": {
                "type": "BM25",
                "k1": 1.2,
                "b": 0.75,
            }
        },
    },
    "mappings": {
        "dynamic": "false",
        "properties": {
            "text": {
                "type": "text",
                "analyzer": "agentic_bm25_text",
                "similarity": "agentic_bm25",
            },
            "chunk_id": {"type": "keyword"},
            "document_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "token_count": {"type": "integer"},
            "source_type": {"type": "keyword"},
            "mime_type": {"type": "keyword"},
            "source_uri": {"type": "keyword"},
            "filename": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "citation": {
                "properties": {
                    "page_number": {"type": "integer"},
                    "section_path": {"type": "keyword"},
                    "block_anchor": {"type": "keyword"},
                }
            },
            "access_policy": {
                "properties": {
                    "classification": {"type": "keyword"},
                    "visibility_scope": {"type": "keyword"},
                    "allowed_roles": {"type": "keyword"},
                    "department_id": {"type": "integer"},
                    "owner_id": {"type": "integer"},
                    "policy_version": {"type": "keyword"},
                }
            },
            "metadata": {"type": "object", "enabled": True},
            "created_at": {"type": "date"},
            "indexed_at": {"type": "date"},
        },
    },
}


def build_elasticsearch_url(host: str | None = None) -> str:
    """Build the HTTP URL expected by elasticsearch/langchain clients."""
    configured_host = (host or settings.ELASTICSEARCH_HOST).strip()
    if configured_host.startswith(("http://", "https://")):
        return configured_host
    return f"http://{configured_host}"


def build_agentic_chunks_index_body() -> dict[str, Any]:
    """Return a copy of the deterministic BM25 index settings/mapping."""
    return deepcopy(AGENTIC_CHUNKS_INDEX_BODY)


def create_elasticsearch_client(*, host: str | None = None) -> Elasticsearch:
    """Create the official Elasticsearch client from runtime settings."""
    _require_elasticsearch_dependencies()
    return Elasticsearch(build_elasticsearch_url(host))


def ensure_agentic_chunks_index(
    client: Elasticsearch | None = None,
    *,
    index_name: str | None = None,
) -> None:
    """Create or update the ES index Task 4 ingestion will sync chunks into."""
    _require_elasticsearch_dependencies()
    es_client = client or create_elasticsearch_client()
    target_index = index_name or settings.ELASTICSEARCH_INDEX_NAME
    index_body = build_agentic_chunks_index_body()

    if not es_client.indices.exists(index=target_index):
        es_client.indices.create(index=target_index, body=index_body)
        return

    es_client.indices.put_mapping(index=target_index, body=index_body["mappings"])


def build_bm25_query(search_query: str, *, top_k: int = DEFAULT_TOP_K) -> dict[str, Any]:
    """Build safe lexical/BM25 query DSL for LangChain ElasticsearchRetriever."""
    normalized_query = search_query.strip()
    if not normalized_query:
        return {"size": 0, "query": {"match_none": {}}}

    return {
        "size": top_k,
        "query": {
            "match": {
                CHUNK_TEXT_FIELD: {
                    "query": normalized_query,
                    "operator": "and",
                }
            }
        },
    }


def build_agentic_elasticsearch_retriever(
    *,
    client: Elasticsearch | None = None,
    index_name: str | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> ElasticsearchRetriever:
    """Build a LangChain ElasticsearchRetriever for lexical chunk search."""
    _require_elasticsearch_dependencies()
    target_index = index_name or settings.ELASTICSEARCH_INDEX_NAME

    def body_func(query: str) -> dict[str, Any]:
        return build_bm25_query(query, top_k=top_k)

    retriever_kwargs: dict[str, Any] = {
        "index_name": target_index,
        "body_func": body_func,
        "document_mapper": map_elasticsearch_hit_to_document,
    }
    if client is not None:
        retriever_kwargs["es_client"] = client
        return ElasticsearchRetriever(**retriever_kwargs)

    return ElasticsearchRetriever.from_es_params(
        index_name=target_index,
        body_func=body_func,
        document_mapper=map_elasticsearch_hit_to_document,
        url=build_elasticsearch_url(),
    )


def map_elasticsearch_hit_to_document(hit: Mapping[str, Any]) -> Document:
    """Map an Elasticsearch hit into a LangChain Document with chunk metadata."""
    source = dict(hit.get("_source") or {})
    page_content = str(source.pop(CHUNK_TEXT_FIELD, ""))
    metadata = {
        "_index": hit.get("_index"),
        "_id": hit.get("_id"),
        "_score": hit.get("_score"),
        **source,
    }
    return Document(page_content=page_content, metadata=metadata)


def _require_elasticsearch_dependencies() -> None:
    if Elasticsearch is Any or ElasticsearchRetriever is Any:  # type: ignore[comparison-overlap]
        raise RuntimeError("langchain-elasticsearch and elasticsearch must be installed")
