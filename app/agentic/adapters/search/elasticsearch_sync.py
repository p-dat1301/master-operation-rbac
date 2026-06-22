"""Elasticsearch sync helpers for derived lexical chunk indexing."""
from __future__ import annotations

from typing import Any

from app.agentic.adapters.search.elasticsearch_client import create_elasticsearch_client, ensure_agentic_chunks_index
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.pipeline.indexing.core import ElasticsearchSyncAdapter, build_elasticsearch_chunk_document
from app.core.config import settings

try:  # pragma: no cover - exercised when optional ES deps are installed
    from elasticsearch.helpers import bulk
except ImportError:  # pragma: no cover
    bulk = None


class AgenticChunkElasticsearchSync(ElasticsearchSyncAdapter):
    def __init__(self, *, client: Any | None = None, index_name: str | None = None) -> None:
        self._client = client or create_elasticsearch_client()
        self._index_name = index_name or settings.ELASTICSEARCH_INDEX_NAME

    def ensure_index(self) -> None:
        ensure_agentic_chunks_index(self._client, index_name=self._index_name)

    def bulk_index_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None:
        if not chunks:
            return
        if bulk is None:
            raise RuntimeError("elasticsearch helpers are not installed")
        actions = (
            {
                "_op_type": "index",
                "_index": self._index_name,
                "_id": chunk.chunk_id,
                "_source": build_elasticsearch_chunk_document(chunk),
            }
            for chunk in chunks
        )
        bulk(self._client, actions)
