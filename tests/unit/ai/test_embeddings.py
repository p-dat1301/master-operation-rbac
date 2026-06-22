"""Unit tests for embedding provider boundary."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from app.agentic.adapters.embeddings.default_embeddings import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    HuggingFaceEmbeddingProvider,
    MAX_EMBEDDING_TOKENS,
)
from app.agentic.pipeline.chunking.tokenizer import FALLBACK_TOKENIZER_POLICY, WhitespaceTokenizerAdapter


def test_default_embedding_provider_exports_model_identity() -> None:
    assert EMBEDDING_MODEL_NAME == "intfloat/multilingual-e5-large"
    assert EMBEDDING_DIMENSION == 1024


@pytest.mark.asyncio
async def test_embedding_provider_validates_token_budget() -> None:
    fake_backend = type("_FakeBackend", (), {"embed": staticmethod(lambda text: [0.0] * EMBEDDING_DIMENSION)})()
    with patch.object(HuggingFaceEmbeddingProvider, "_load_model", return_value=fake_backend):
        provider = HuggingFaceEmbeddingProvider(max_tokens=1)

    with pytest.raises(ValueError, match="embedding input exceeds token budget"):
        await provider.embed(["too many tokens"])


@pytest.mark.asyncio
async def test_embedding_provider_returns_1024_dimension_vectors() -> None:
    fake_backend = type("_FakeBackend", (), {"embed": staticmethod(lambda text: [0.5] * EMBEDDING_DIMENSION)})()
    with patch.object(HuggingFaceEmbeddingProvider, "_load_model", return_value=fake_backend):
        provider = HuggingFaceEmbeddingProvider(max_tokens=MAX_EMBEDDING_TOKENS)

    vectors = await provider.embed(["hello world"])

    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIMENSION
    assert all(isinstance(value, float) for value in vectors[0])


@pytest.mark.asyncio
async def test_embedding_provider_surfaces_backend_load_failure() -> None:
    with patch.object(HuggingFaceEmbeddingProvider, "_load_model", side_effect=RuntimeError("model unavailable")):
        with pytest.raises(RuntimeError, match="model unavailable"):
            HuggingFaceEmbeddingProvider(max_tokens=MAX_EMBEDDING_TOKENS)


def test_fallback_tokenizer_remains_supported_for_embedding_seam() -> None:
    adapter = WhitespaceTokenizerAdapter()

    assert adapter.policy == FALLBACK_TOKENIZER_POLICY
