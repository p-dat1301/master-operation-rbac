"""Normalization helpers for parsed documents."""
from __future__ import annotations

from app.agentic.contracts.document import NormalizedDocument, ParsedDocument
from app.agentic.parsing.parse_document import normalize_document as _normalize_document


def normalize_document(parsed: ParsedDocument) -> NormalizedDocument:
    return _normalize_document(parsed)
