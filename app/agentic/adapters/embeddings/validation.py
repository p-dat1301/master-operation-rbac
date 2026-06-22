"""Embedding validation utilities."""
from __future__ import annotations

from app.agentic.contracts.embedding import EMBEDDING_DIMENSION


def validate_embedding_dimension(embedding: list[float]) -> None:
    """Validate embedding vector dimension matches schema.

    Raises:
        ValueError: If dimension mismatch detected.
    """
    actual_dim = len(embedding)
    if actual_dim != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {actual_dim}"
        )


def validate_embeddings_batch(embeddings: list[list[float]]) -> None:
    """Validate a batch of embeddings.

    Raises:
        ValueError: If any embedding has dimension mismatch.
    """
    for idx, embedding in enumerate(embeddings):
        try:
            validate_embedding_dimension(embedding)
        except ValueError as exc:
            raise ValueError(f"Embedding at index {idx} failed validation: {exc}") from exc


__all__ = [
    "validate_embedding_dimension",
    "validate_embeddings_batch",
]
