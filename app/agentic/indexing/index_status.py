"""Indexing status contracts for Task 7."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IndexStatus(StrEnum):
    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"
    STALE = "stale"


class IndexRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1)
    chunk_id: str | None = Field(default=None, min_length=1)
    parser_version: str = Field(min_length=1)
    normalized_version: str = Field(min_length=1)
    chunker_version: str = Field(min_length=1)
    embedding_model: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    index_version: str = Field(default="index-v1", min_length=1)
    token_count: int | None = Field(default=None, ge=0)
    source_type: str = Field(min_length=1)
    mime_type: str = Field(min_length=1)
    status: IndexStatus = IndexStatus.PENDING
    failure_reason: str | None = Field(default=None, min_length=1)
    retry_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
