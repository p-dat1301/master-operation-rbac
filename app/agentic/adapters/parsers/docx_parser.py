"""DOCX parser adapter for structured Word documents."""
from __future__ import annotations

from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree as ET

from app.agentic.adapters.parsers.base import BaseParser, ParserError
from app.agentic.contracts.document import ParsedDocument, ParserStatus
from app.agentic.contracts.source import SourceMetadata


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOC_LEGACY_MIME = "application/msword"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _read_document_xml(path: str) -> ET.Element:
    try:
        with ZipFile(path) as archive:
            data = archive.read("word/document.xml")
    except (BadZipFile, KeyError, OSError) as exc:  # pragma: no cover - controlled failure mapping
        raise ParserError(f"failed to read docx: {path}") from exc
    return ET.fromstring(data)


def _paragraph_text(paragraph: ET.Element) -> str:
    texts: list[str] = []
    for node in paragraph.iter():
        if node.tag == f"{W_NS}t" and node.text:
            texts.append(node.text)
    return "".join(texts).strip()


def _style_name(paragraph: ET.Element) -> str:
    style = paragraph.find(f"{W_NS}pPr/{W_NS}pStyle")
    if style is None:
        return ""
    value = str(style.attrib.get(f"{W_NS}val", ""))
    if value.startswith("Heading") and len(value) > len("Heading") and value[len("Heading") :].isdigit():
        return f"Heading {value[len('Heading') :]}"
    return value


class DocxParser(BaseParser):
    name = "docx-xml-parser"
    version = "docx-xml-v1"

    def parse(self, source: SourceMetadata, document_id: str) -> ParsedDocument:
        filename = (source.filename or source.source_uri).lower()
        if source.mime_type == DOC_LEGACY_MIME or filename.endswith(".doc"):
            raise ParserError("unsupported_doc_legacy: .doc is not supported in v1")
        if source.mime_type != DOCX_MIME:
            raise ParserError(f"unsupported docx mime_type: {source.mime_type}")

        root = _read_document_xml(source.source_uri)

        blocks: list[dict[str, object]] = []
        raw_parts: list[str] = []
        section_path: list[str] = []
        block_index = 0

        body = root.find(f"{W_NS}body")
        if body is None:
            raise ParserError(f"failed to read docx body: {source.source_uri}")

        table_index = 0
        for child in body:
            if child.tag == f"{W_NS}p":
                text = _paragraph_text(child)
                if not text:
                    continue
                style_name = _style_name(child)
                heading_level: int | None = None
                kind = "paragraph"
                if style_name.startswith("Heading"):
                    kind = "heading"
                    try:
                        heading_level = int(style_name.split()[-1])
                    except (TypeError, ValueError):
                        heading_level = None
                    if heading_level is not None:
                        section_path = section_path[: max(heading_level - 1, 0)]
                    section_path.append(text)
                raw_parts.append(text)
                blocks.append(
                    {
                        "kind": kind,
                        "text": text,
                        "heading_level": heading_level,
                        "section_path": tuple(section_path),
                        "block_anchor": f"docx-block-{block_index}",
                        "metadata": {"style_name": style_name},
                    }
                )
                block_index += 1
            elif child.tag == f"{W_NS}tbl":
                row_texts: list[str] = []
                for paragraph in child.findall(f".//{W_NS}p"):
                    text = _paragraph_text(paragraph)
                    if text:
                        row_texts.append(text)
                if not row_texts:
                    continue
                table_text = " | ".join(row_texts)
                raw_parts.append(table_text)
                blocks.append(
                    {
                        "kind": "paragraph",
                        "text": table_text,
                        "heading_level": None,
                        "section_path": tuple(section_path),
                        "block_anchor": f"docx-table-{block_index}",
                        "metadata": {"source_kind": "table", "row_index": table_index},
                    }
                )
                block_index += 1
                table_index += 1

        raw_text = "\n\n".join(raw_parts).strip()
        if not raw_text:
            raise ParserError("docx contains no extractable text")

        return ParsedDocument(
            document_id=document_id,
            source=source,
            parser_name=self.name,
            parser_version=self.version,
            status=ParserStatus.PARSED,
            raw_text=raw_text,
            extracted_metadata={"blocks": blocks, "loader": "docx-xml"},
        )
