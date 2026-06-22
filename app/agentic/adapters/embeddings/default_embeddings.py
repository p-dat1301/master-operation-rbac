"""Default embedding provider for the multilingual-e5 MVP."""
from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from app.agentic.contracts.embedding import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_VERSION,
    MAX_EMBEDDING_TOKENS,
)
from app.agentic.pipeline.chunking.tokenizer import get_tokenizer_adapter
from app.agentic.pipeline.indexing import EmbeddingProvider


class EmbeddingBackend(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Embed queries/chunks with a local Hugging Face multilingual-e5 model."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, *, max_tokens: int = MAX_EMBEDDING_TOKENS) -> None:
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._tokenizer = get_tokenizer_adapter()
        self._model = self._load_model(model_name)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        validated = [self._validate_text(text) for text in texts]
        return [self._model.embed(text) for text in validated]

    def _validate_text(self, text: str) -> str:
        normalized = self._normalize_input(text)
        tokens = self._tokenizer.encode(normalized)
        if len(tokens) > self._max_tokens:
            raise ValueError(f"embedding input exceeds token budget: {len(tokens)} > {self._max_tokens}")
        return normalized

    def _load_model(self, model_name: str) -> EmbeddingBackend:
        try:
            from transformers import AutoModel, AutoTokenizer
        except Exception as exc:  # pragma: no cover - dependency resolution failure path
            raise RuntimeError("transformers is required for the default embedding provider") from exc

        return _TransformersEmbeddingBackend(model_name, AutoTokenizer, AutoModel)

    @staticmethod
    def _normalize_input(text: str) -> str:
        return text.strip()


class _TransformersEmbeddingBackend:
    def __init__(self, model_name: str, auto_tokenizer, auto_model) -> None:
        self._model_name = model_name
        self._auto_tokenizer = auto_tokenizer
        self._auto_model = auto_model
        self._tokenizer = None
        self._model = None

    def _ensure_loaded(self):
        if self._tokenizer is None:
            self._tokenizer = self._auto_tokenizer.from_pretrained(self._model_name)
        if self._model is None:
            self._model = self._auto_model.from_pretrained(self._model_name)
        return self._tokenizer, self._model

    def embed(self, text: str) -> list[float]:
        tokenizer, model = self._ensure_loaded()
        encoded = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        output = model(**encoded)
        vector = output.last_hidden_state.mean(dim=1).squeeze(0)
        values = vector.detach().cpu().tolist()
        if len(values) != EMBEDDING_DIMENSION:
            raise ValueError(f"embedding dimension mismatch: expected {EMBEDDING_DIMENSION}, got {len(values)}")
        return [float(value) for value in values]


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    return HuggingFaceEmbeddingProvider()


__all__ = [
    "EMBEDDING_DIMENSION",
    "EMBEDDING_MODEL_NAME",
    "EMBEDDING_MODEL_VERSION",
    "HuggingFaceEmbeddingProvider",
    "MAX_EMBEDDING_TOKENS",
    "get_embedding_provider",
]
