"""Unit tests for indexing/storage abstraction."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.agentic.adapters.storage.local_storage import LocalChunkStorageAdapter, LocalDocumentStorageAdapter
from app.agentic.chunking.chunk_config import ChunkConfig
from app.agentic.chunking.chunk_document import chunk_document
from app.agentic.contracts import AccessPolicyMetadata, Classification, SourceMetadata, SourceType, VisibilityScope
from app.agentic.indexing import IndexStatus, index_document
from app.agentic.parsing.parse_document import normalize_document, parse_document


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
