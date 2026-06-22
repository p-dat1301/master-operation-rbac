"""Ingestion stage package."""
from .checksum import checksum_text
from .core import IngestSource, IngestionResult, IngestionStatus
from .source_registry import SourceDispatch, SourceRegistry

__all__ = [
    "IngestSource",
    "IngestionResult",
    "IngestionStatus",
    "SourceDispatch",
    "SourceRegistry",
    "checksum_text",
]
