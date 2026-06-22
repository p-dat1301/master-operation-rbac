"""Local in-memory storage adapters for development and unit tests."""
from __future__ import annotations

from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord
from app.agentic.pipeline.indexing import ChunkStorageAdapter, DocumentStorageAdapter


class LocalDocumentStorageAdapter(DocumentStorageAdapter):
    def __init__(self) -> None:
        self.records: dict[str, DocumentRecord] = {}

    async def get(self, document_id: str) -> DocumentRecord | None:
        return self.records.get(document_id)

    async def upsert(self, record: DocumentRecord) -> DocumentRecord:
        self.records[record.document_id] = record
        return record

    async def delete(self, document_id: str) -> None:
        self.records.pop(document_id, None)


class LocalChunkStorageAdapter(ChunkStorageAdapter):
    def __init__(self) -> None:
        self.records: dict[str, DocumentChunk] = {}

    async def get_many_by_chunk_ids(self, chunk_ids: tuple[str, ...]) -> list[DocumentChunk]:
        return [self.records[chunk_id] for chunk_id in chunk_ids if chunk_id in self.records]

    async def list_by_document(self, document_id: str) -> list[DocumentChunk]:
        return [chunk for chunk in self.records.values() if chunk.document_id == document_id]

    async def upsert_many(self, chunks: tuple[DocumentChunk, ...]) -> tuple[DocumentChunk, ...]:
        for chunk in chunks:
            self.records[chunk.chunk_id] = chunk
        return chunks

    async def delete_by_document(self, document_id: str) -> None:
        for chunk_id, chunk in list(self.records.items()):
            if chunk.document_id == document_id:
                del self.records[chunk_id]
