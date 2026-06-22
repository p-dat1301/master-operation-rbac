"""Storage adapter interfaces for documents and chunks."""
from app.agentic.pipeline.indexing import ChunkStorageAdapter, DocumentStorageAdapter

__all__ = ["ChunkStorageAdapter", "DocumentStorageAdapter"]
