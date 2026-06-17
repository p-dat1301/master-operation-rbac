"""Tests for the ingestion entrypoint."""
# pyright: reportCallIssue=false
from __future__ import annotations

import pytest
from app.agentic.contracts import (
    AccessPolicyMetadata,
    Classification,
    SourceMetadata,
    SourceType,
    VisibilityScope,
)
from app.agentic.ingestion.ingest_source import IngestSource, IngestionStatus


DEFAULT_POLICY = AccessPolicyMetadata(
    classification=Classification.INTERNAL,
    visibility_scope=VisibilityScope.GLOBAL,
)


def test_ingest_uploaded_pdf_returns_pending_parse_result() -> None:
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri="/tmp/policy.pdf",
        filename="policy.pdf",
        size_bytes=1024,
    )

    result = IngestSource().ingest(source, DEFAULT_POLICY)

    assert result.status is IngestionStatus.PENDING_PARSE
    assert result.source == source
    assert result.access_policy == DEFAULT_POLICY
    assert result.checksum.startswith("sha256:")
    assert result.parser_target == "uploaded-file-parser"
    assert result.document_id.startswith("doc-")
    assert result.ingestion_id.startswith("ing-")


def test_ingest_uploaded_docx_returns_pending_parse_result() -> None:
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        source_uri="/tmp/policy.docx",
    )

    result = IngestSource().ingest(source, DEFAULT_POLICY)

    assert result.status is IngestionStatus.PENDING_PARSE
    assert result.parser_target == "uploaded-file-parser"


def test_ingest_rejects_unsupported_mime_type() -> None:
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/vnd.ms-excel",
        source_uri="/tmp/report.xlsx",
    )

    with pytest.raises(ValueError, match="unsupported mime_type for v1"):
        IngestSource().ingest(source, DEFAULT_POLICY)


def test_ingest_rejects_external_uri_source_type_in_v1() -> None:
    source = SourceMetadata(
        source_type=SourceType.EXTERNAL_URI,
        mime_type="application/pdf",
        source_uri="https://example.com/policy.pdf",
    )

    with pytest.raises(ValueError, match="unsupported source_type for v1"):
        IngestSource().ingest(source, DEFAULT_POLICY)


def test_ingest_requires_access_policy_metadata() -> None:
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri="/tmp/policy.pdf",
    )

    with pytest.raises(TypeError, match="access_policy"):
        IngestSource().ingest(source)  # type: ignore[call-arg]
