"""Core source contracts for source-agnostic ingestion."""
from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceType(StrEnum):
    """Supported source families without binding to a parser implementation."""

    UPLOADED_FILE = "uploaded_file"
    EXTERNAL_URI = "external_uri"


class SourceMetadata(BaseModel):
    """Input metadata captured before parsing starts."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: SourceType
    mime_type: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    filename: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_uri")
    @classmethod
    def source_uri_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("source_uri must not be blank")
        return str(Path(value)) if value.startswith("/") else value
