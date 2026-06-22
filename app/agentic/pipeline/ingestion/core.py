"""Canonical ingestion stage for agentic pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.source import SourceMetadata
from app.agentic.pipeline.ingestion.checksum import checksum_text
from app.agentic.pipeline.ingestion.source_registry import SourceRegistry


class IngestionStatus(StrEnum):
    ACCEPTED = "accepted"
    PENDING_PARSE = "pending_parse"
    REJECTED = "rejected"


class IngestionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ingestion_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    source: SourceMetadata
    access_policy: AccessPolicyMetadata
    status: IngestionStatus
    checksum: str
    parser_target: str
    accepted_at: datetime
    metadata: dict[str, str] = Field(default_factory=dict)


@dataclass(slots=True)
class IngestSource:
    registry: SourceRegistry = field(default_factory=SourceRegistry)

    def ingest(self, source: SourceMetadata, access_policy: AccessPolicyMetadata) -> IngestionResult:
        dispatch = self.registry.resolve(source)
        checksum = source.checksum or checksum_text(source.source_type.value, source.mime_type, source.source_uri)
        document_id = f"doc-{uuid4().hex}"
        return IngestionResult(
            ingestion_id=f"ing-{uuid4().hex}",
            document_id=document_id,
            source=source,
            access_policy=access_policy,
            status=IngestionStatus.PENDING_PARSE,
            checksum=checksum,
            parser_target=dispatch.parser_target,
            accepted_at=datetime.now(timezone.utc),
            metadata={"source_type": source.source_type.value, "filename": source.filename or ""},
        )
