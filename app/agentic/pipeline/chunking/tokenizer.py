"""Tokenizer adapters used by the chunking stage."""
from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache

MODEL_NAME = "intfloat/multilingual-e5-large"
TOKENIZER_POLICY = "hf-auto-tokenizer-intfloat-multilingual-e5-large-v1"
FALLBACK_TOKENIZER_POLICY = "whitespace-token-v1"


class TokenizerAdapter(ABC):
    policy: str

    @abstractmethod
    def encode(self, text: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def decode(self, tokens: list[str]) -> str:
        raise NotImplementedError


class WhitespaceTokenizerAdapter(TokenizerAdapter):
    policy = FALLBACK_TOKENIZER_POLICY

    def encode(self, text: str) -> list[str]:
        return text.split()

    def decode(self, tokens: list[str]) -> str:
        return " ".join(token for token in tokens if token)


class HuggingFaceTokenizerAdapter(TokenizerAdapter):
    policy = TOKENIZER_POLICY

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        from transformers import AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(model_name)

    def encode(self, text: str) -> list[str]:
        return self._tokenizer.tokenize(text, add_special_tokens=False)

    def decode(self, tokens: list[str]) -> str:
        return self._tokenizer.convert_tokens_to_string(tokens).strip()


@lru_cache(maxsize=1)
def get_tokenizer_adapter() -> TokenizerAdapter:
    try:
        return HuggingFaceTokenizerAdapter()
    except Exception:
        return WhitespaceTokenizerAdapter()
