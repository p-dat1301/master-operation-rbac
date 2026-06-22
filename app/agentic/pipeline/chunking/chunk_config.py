"""Chunking configuration for retrieval-ready document chunks."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChunkConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    chunker_version: str = Field(default="token-window-v1", min_length=1)
    max_chunk_tokens: int = Field(default=180, ge=1)
    overlap_tokens: int = Field(default=30, ge=0)
    tokenizer_policy: str = Field(default="hf-auto-tokenizer-intfloat-multilingual-e5-large-v1", min_length=1)

    @model_validator(mode="after")
    def validate_overlap_budget(self) -> "ChunkConfig":
        if self.overlap_tokens >= self.max_chunk_tokens:
            raise ValueError("overlap_tokens must be smaller than max_chunk_tokens")
        return self
