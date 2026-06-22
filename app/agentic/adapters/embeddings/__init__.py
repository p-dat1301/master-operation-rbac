"""Embedding adapter boundary for agentic indexing."""
from app.agentic.adapters.embeddings.default_embeddings import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_VERSION,
    HuggingFaceEmbeddingProvider,
    MAX_EMBEDDING_TOKENS,
    get_embedding_provider,
)
from app.agentic.pipeline.indexing import EmbeddingProvider

__all__ = [
    "EMBEDDING_DIMENSION",
    "EMBEDDING_MODEL_NAME",
    "EMBEDDING_MODEL_VERSION",
    "EmbeddingProvider",
    "HuggingFaceEmbeddingProvider",
    "MAX_EMBEDDING_TOKENS",
    "get_embedding_provider",
]
