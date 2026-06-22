"""Unit tests for indexing/storage abstraction."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.agentic.adapters.storage.local_storage import LocalChunkStorageAdapter, LocalDocumentStorageAdapter
from app.agentic.contracts import AccessPolicyMetadata, Classification, SourceMetadata, SourceType, VisibilityScope
from app.agentic.pipeline.chunking import ChunkConfig, chunk_document
from app.agentic.pipeline.indexing import (
    EmbeddingPersistenceError,
    IndexStatus,
    build_elasticsearch_chunk_document,
    embed_and_persist_chunks,
    index_document,
    reindex_chunks_to_elasticsearch,
)
from app.agentic.pipeline.parsing import normalize_document, parse_document



class _RecordingEmbeddingProvider:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.texts = texts
        return [[float(index)] for index, _ in enumerate(texts)]


class _FailingEmbeddingProvider:
    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("embedding provider unavailable")


class _RecordingVectorStore:
    async def upsert(self, chunks, embeddings, metadata):
        self.chunks = chunks
        self.embeddings = embeddings
        self.metadata = metadata

    async def delete_by_document(self, document_id: str) -> None:
        self.deleted_document_id = document_id


class _RecordingElasticsearchSync:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.ensure_calls = 0
        self.indexed_batches = []

    def ensure_index(self) -> None:
        self.ensure_calls += 1
        if self.fail:
            raise RuntimeError("elasticsearch unavailable")

    def bulk_index_chunks(self, chunks) -> None:
        if self.fail:
            raise RuntimeError("bulk write failed")
        self.indexed_batches.append(chunks)


class _BackfillChunks:
    def __init__(self, chunks) -> None:
        self.chunks = chunks
        self.calls = []

    async def list_chunks(self, *, limit: int, offset: int):
        self.calls.append({"limit": limit, "offset": offset})
        return tuple(self.chunks[offset : offset + limit])


PDF_BYTES = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 78 >>
stream
BT
/F1 12 Tf
72 100 Td
(Index document chunk one) Tj
0 -20 Td
(Index document chunk two) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000061 00000 n 
0000000118 00000 n 
0000000253 00000 n 
0000000381 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
454
%%EOF
'''


def _source(path: Path) -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri=str(path),
        filename=path.name,
        metadata={
            "access_policy": AccessPolicyMetadata(
                classification=Classification.INTERNAL,
                visibility_scope=VisibilityScope.GLOBAL,
            )
        },
    )


@pytest.mark.asyncio
async def test_embed_and_persist_chunks_produces_embeddings_and_upserts(tmp_path: Path) -> None:
    pdf_path = tmp_path / "embedable.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-embed-1"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    provider = _RecordingEmbeddingProvider()
    vector_store = _RecordingVectorStore()
    embeddings = await embed_and_persist_chunks(
        chunks,
        embedding_provider=provider,
        vector_store=vector_store,
        metadata={"embedding_model": "test-embedder", "index_version": "index-v1"},
    )

    assert provider.texts == [chunk.text for chunk in chunks]
    assert embeddings == [[float(index)] for index in range(len(chunks))]
    assert vector_store.chunks == chunks
    assert vector_store.embeddings == embeddings
    assert vector_store.metadata["embedding_model"] == "test-embedder"


@pytest.mark.asyncio
async def test_embed_and_persist_chunks_surfaces_embedding_failure(tmp_path: Path) -> None:
    pdf_path = tmp_path / "embed-failure.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-embed-2"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    with pytest.raises(EmbeddingPersistenceError, match="embedding provider unavailable"):
        await embed_and_persist_chunks(
            chunks,
            embedding_provider=_FailingEmbeddingProvider(),
            vector_store=_RecordingVectorStore(),
            metadata={"embedding_model": "test-embedder", "index_version": "index-v1"},
        )


@pytest.mark.asyncio
async def test_index_document_persists_stable_document_and_chunk_identity(tmp_path: Path) -> None:
    pdf_path = tmp_path / "indexable.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-index-1"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))
    result = index_document(normalized, chunks)

    document_store = LocalDocumentStorageAdapter()
    chunk_store = LocalChunkStorageAdapter()
    saved_document = await document_store.upsert(result.document_record)
    saved_chunks = await chunk_store.upsert_many(result.chunks)

    assert saved_document.document_id == "doc-index-1"
    assert result.index_record.status is IndexStatus.INDEXED
    assert result.index_record.metadata["chunk_ids"] == [chunk.chunk_id for chunk in chunks]
    assert [chunk.chunk_id for chunk in saved_chunks] == [chunk.chunk_id for chunk in chunks]


@pytest.mark.asyncio
async def test_retry_indexing_does_not_duplicate_chunk_records(tmp_path: Path) -> None:
    pdf_path = tmp_path / "indexable-retry.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-index-2"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    chunk_store = LocalChunkStorageAdapter()
    await chunk_store.upsert_many(chunks)
    await chunk_store.upsert_many(chunks)

    stored_chunks = await chunk_store.list_by_document("doc-index-2")

    assert len(stored_chunks) == len(chunks)
    assert {chunk.chunk_id for chunk in stored_chunks} == {chunk.chunk_id for chunk in chunks}


def test_index_document_marks_embedding_failures_distinctly(tmp_path: Path) -> None:
    pdf_path = tmp_path / "index-embedding-failure.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-index-fail"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    result = index_document(normalized, chunks, embedding_error="embedding provider unavailable")

    assert result.status is IndexStatus.FAILED
    assert result.document_record.status == "failed"
    assert result.document_record.metadata["embedding_error"] == "embedding provider unavailable"
    assert result.index_record.failure_reason == "embedding provider unavailable"
    assert result.index_record.metadata["embedding_failed"] == "true"


@pytest.mark.asyncio
async def test_embed_and_persist_chunks_syncs_to_elasticsearch_after_pgvector_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agentic.pipeline.indexing.core.settings.RAG_USE_ELASTICSEARCH", True)
    pdf_path = tmp_path / "embed-es-success.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-embed-es-1"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    provider = _RecordingEmbeddingProvider()
    vector_store = _RecordingVectorStore()
    es_sync = _RecordingElasticsearchSync()

    await embed_and_persist_chunks(
        chunks,
        embedding_provider=provider,
        vector_store=vector_store,
        elasticsearch_sync=es_sync,
        metadata={"embedding_model": "test-embedder", "index_version": "index-v1"},
    )

    assert vector_store.chunks == chunks
    assert es_sync.ensure_calls == 1
    assert es_sync.indexed_batches == [chunks]
    es_doc = build_elasticsearch_chunk_document(chunks[0])
    assert es_doc["chunk_id"] == chunks[0].chunk_id
    assert es_doc["document_id"] == chunks[0].document_id
    assert es_doc["text"] == chunks[0].text


@pytest.mark.asyncio
async def test_embed_and_persist_chunks_logs_warning_when_elasticsearch_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr("app.agentic.pipeline.indexing.core.settings.RAG_USE_ELASTICSEARCH", True)
    pdf_path = tmp_path / "embed-es-failure.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-embed-es-2"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    vector_store = _RecordingVectorStore()
    with caplog.at_level("WARNING"):
        embeddings = await embed_and_persist_chunks(
            chunks,
            embedding_provider=_RecordingEmbeddingProvider(),
            vector_store=vector_store,
            elasticsearch_sync=_RecordingElasticsearchSync(fail=True),
            metadata={"embedding_model": "test-embedder", "index_version": "index-v1"},
        )

    assert embeddings == [[float(index)] for index in range(len(chunks))]
    assert vector_store.chunks == chunks
    assert "Elasticsearch chunk sync failed; continuing with pgvector as source of truth" in caplog.text
    assert "elasticsearch unavailable" in caplog.text


@pytest.mark.asyncio
async def test_reindex_chunks_to_elasticsearch_backfills_from_pgvector(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agentic.pipeline.indexing.core.settings.RAG_USE_ELASTICSEARCH", True)
    pdf_path = tmp_path / "embed-es-backfill.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_source(pdf_path), "doc-embed-es-3"))
    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=8, overlap_tokens=2))

    backfill = _BackfillChunks(list(chunks))
    es_sync = _RecordingElasticsearchSync()
    indexed_count = await reindex_chunks_to_elasticsearch(
        backfill_adapter=backfill,
        elasticsearch_sync=es_sync,
        batch_size=1,
    )

    assert indexed_count == len(chunks)
    assert es_sync.ensure_calls == 1
    assert es_sync.indexed_batches == [tuple([chunk]) for chunk in chunks]
    assert backfill.calls[-1]["offset"] == len(chunks)
