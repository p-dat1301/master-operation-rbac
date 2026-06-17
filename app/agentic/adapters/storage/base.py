"""Storage adapter interfaces for documents and chunks."""
from app.agentic.indexing.index_document import ChunkStorageAdapter, DocumentStorageAdapter

__all__ = ["ChunkStorageAdapter", "DocumentStorageAdapter"]
