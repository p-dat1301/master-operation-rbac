"""Vector store adapter boundary for agentic indexing."""
from app.agentic.adapters.vector_store.base import VectorStoreAdapter
from app.agentic.adapters.vector_store.pgvector_store import PGVectorStoreAdapter

__all__ = ["VectorStoreAdapter", "PGVectorStoreAdapter"]
