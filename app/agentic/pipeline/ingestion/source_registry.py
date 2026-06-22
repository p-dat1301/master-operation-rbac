"""Source registry for source-agnostic ingestion dispatch."""
from __future__ import annotations

from dataclasses import dataclass

from app.agentic.contracts.source import SourceMetadata, SourceType


@dataclass(frozen=True, slots=True)
class SourceDispatch:
    parser_target: str
    supported_mime_types: frozenset[str]


class SourceRegistry:
    def __init__(self, mapping: dict[SourceType, SourceDispatch] | None = None) -> None:
        self._mapping = mapping or {
            SourceType.UPLOADED_FILE: SourceDispatch(
                parser_target="uploaded-file-parser",
                supported_mime_types=frozenset(
                    {
                        "application/pdf",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    }
                ),
            ),
        }

    def resolve(self, source: SourceMetadata) -> SourceDispatch:
        try:
            dispatch = self._mapping[source.source_type]
        except KeyError as exc:
            raise ValueError(f"unsupported source_type for v1: {source.source_type}") from exc
        if source.mime_type not in dispatch.supported_mime_types:
            raise ValueError(f"unsupported mime_type for v1: {source.mime_type}")
        return dispatch
