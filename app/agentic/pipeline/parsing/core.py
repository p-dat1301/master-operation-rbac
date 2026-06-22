"""Canonical parsing stage for agentic pipeline."""
from __future__ import annotations

from app.agentic.adapters.parsers.base import BaseParser, ParserError
from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.document import (
    BlockKind,
    CitationMetadata,
    ContentBlock,
    NormalizedDocument,
    ParsedDocument,
)
from app.agentic.contracts.source import SourceMetadata
from app.agentic.pipeline.parsing.parser_registry import parser_registry


def build_parser_registry() -> dict[str, BaseParser]:
    return parser_registry()


def parse_document(source: SourceMetadata, document_id: str, parser_registry: dict[str, BaseParser] | None = None) -> ParsedDocument:
    registry = parser_registry or build_parser_registry()
    try:
        parser = registry[source.mime_type]
    except KeyError as exc:
        raise ParserError(f"unsupported mime_type for parsing: {source.mime_type}") from exc
    return parser.parse(source, document_id)


def normalize_document(parsed: ParsedDocument) -> NormalizedDocument:
    access_policy = parsed.source.metadata.get("access_policy")
    if not isinstance(access_policy, AccessPolicyMetadata):
        raise ParserError("normalization requires access_policy metadata")
    extracted_blocks = parsed.extracted_metadata.get("blocks", [])
    blocks: list[ContentBlock] = []
    for order, block in enumerate(extracted_blocks):
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        kind_name = block.get("kind", "paragraph")
        try:
            kind = BlockKind(kind_name)
        except ValueError:
            kind = BlockKind.PARAGRAPH
        page_number = block.get("page_number") if isinstance(block.get("page_number"), int) else None
        section_path = block.get("section_path") if isinstance(block.get("section_path"), tuple) else tuple(block.get("section_path", ()))
        block_anchor = block.get("block_anchor") if isinstance(block.get("block_anchor"), str) else None
        heading_level = block.get("heading_level") if isinstance(block.get("heading_level"), int) else None
        metadata = block.get("metadata") if isinstance(block.get("metadata"), dict) else {}
        blocks.append(ContentBlock(kind=kind, text=text.strip(), order=order, heading_level=heading_level, metadata=metadata, citation=CitationMetadata(page_number=page_number, section_path=section_path, block_anchor=block_anchor)))
    if not blocks:
        raise ParserError("normalized document must contain at least one block")
    return NormalizedDocument(document_id=parsed.document_id, source=parsed.source, access_policy=access_policy, parser_name=parsed.parser_name, parser_version=parsed.parser_version, title=parsed.source.filename, blocks=tuple(blocks), metadata={"parsed_status": parsed.status.value, "loader": parsed.extracted_metadata.get("loader")})
