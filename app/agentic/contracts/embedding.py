"""Embedding configuration constants - single source of truth."""
from __future__ import annotations

EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"
EMBEDDING_MODEL_VERSION = "hf-multilingual-e5-large-v1"
EMBEDDING_DIMENSION = 1024
MAX_EMBEDDING_TOKENS = 512

__all__ = [
    "EMBEDDING_DIMENSION",
    "EMBEDDING_MODEL_NAME",
    "EMBEDDING_MODEL_VERSION",
    "MAX_EMBEDDING_TOKENS",
]
