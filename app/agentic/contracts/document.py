"""Document and normalized-content contracts for the RAG pipeline."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.source import SourceMetadata


class ParserStatus(StrEnum):
    PENDING = "pending"
    PARSED = "parsed"
    FAILED = "failed"


class BlockKind(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"


class CitationMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    page_number: int | None = Field(default=None, ge=1)
    section_path: tuple[str, ...] = Field(default_factory=tuple)
    block_anchor: str | None = Field(default=None, min_length=1)


class ContentBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    block_id: str = Field(default_factory=lambda: f"block-{uuid4().hex}")
    kind: BlockKind
    text: str = Field(min_length=1)
    order: int = Field(ge=0)
    heading_level: int | None = Field(default=None, ge=1, le=6)
    metadata: dict[str, Any] = Field(default_factory=dict)
    citation: CitationMetadata


class ParsedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1)
    source: SourceMetadata
    parser_name: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    status: ParserStatus = ParserStatus.PARSED
    raw_text: str = Field(min_length=1)
    extracted_metadata: dict[str, Any] = Field(default_factory=dict)
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NormalizedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1)
    source: SourceMetadata
    access_policy: AccessPolicyMetadata
    parser_name: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    normalized_version: str = Field(default="normalized-document-v1", min_length=1)
    title: str | None = None
    language: str | None = None
    blocks: tuple[ContentBlock, ...] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentRecord(BaseModel):
    """Indexed document-level metadata reused across pipeline stages."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    document_id: str = Field(min_length=1)
    source: SourceMetadata
    access_policy: AccessPolicyMetadata
    parser_name: str | None = None
    parser_version: str | None = None
    chunker_version: str | None = None
    title: str | None = None
    status: Literal["ingested", "parsed", "chunked", "indexed", "failed"] = "ingested"
    metadata: dict[str, Any] = Field(default_factory=dict)
