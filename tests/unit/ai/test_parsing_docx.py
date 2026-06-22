"""Unit tests for DOCX parsing and normalization."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from app.agentic.adapters.parsers.base import ParserError
from app.agentic.adapters.parsers.docx_parser import DOCX_MIME, DOC_LEGACY_MIME
from app.agentic.contracts import (
    AccessPolicyMetadata,
    BlockKind,
    Classification,
    SourceMetadata,
    SourceType,
    VisibilityScope,
)
from app.agentic.pipeline.parsing import normalize_document, parse_document


DEFAULT_POLICY = AccessPolicyMetadata(
    classification=Classification.INTERNAL,
    visibility_scope=VisibilityScope.GLOBAL,
)


def _source(path: Path, mime_type: str = DOCX_MIME) -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type=mime_type,
        source_uri=str(path),
        filename=path.name,
        metadata={"access_policy": DEFAULT_POLICY},
    )


def _write_docx_fixture(path: Path) -> None:
    document_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>
  <w:body>
    <w:p><w:pPr><w:pStyle w:val='Heading1'/></w:pPr><w:r><w:t>HR Policy</w:t></w:r></w:p>
    <w:p><w:r><w:t>Employees can request annual leave.</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Policy</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>Annual leave</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
    <w:sectPr/>
  </w:body>
</w:document>
"""
    content_types = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>
  <Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/>
  <Default Extension='xml' ContentType='application/xml'/>
  <Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/>
</Types>
"""
    rels = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>
"""
    doc_rels = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>
"""
    with ZipFile(path, 'w') as archive:
        archive.writestr('[Content_Types].xml', content_types)
        archive.writestr('_rels/.rels', rels)
        archive.writestr('word/_rels/document.xml.rels', doc_rels)
        archive.writestr('word/document.xml', document_xml)


def test_parse_docx_to_normalized_heading_paragraph_and_table(tmp_path: Path) -> None:
    docx_path = tmp_path / "sample.docx"
    _write_docx_fixture(docx_path)

    parsed = parse_document(_source(docx_path), "doc-docx-1")
    normalized = normalize_document(parsed)

    assert parsed.parser_name == "docx-xml-parser"
    assert parsed.parser_version == "docx-xml-v1"
    assert "HR Policy" in parsed.raw_text
    assert normalized.blocks[0].kind is BlockKind.HEADING
    assert normalized.blocks[0].heading_level == 1
    assert normalized.blocks[0].citation.section_path == ("HR Policy",)
    assert normalized.blocks[1].kind is BlockKind.PARAGRAPH
    assert normalized.blocks[1].text == "Employees can request annual leave."
    assert normalized.blocks[2].metadata["source_kind"] == "table"
    assert normalized.blocks[2].text == "Policy | Annual leave"


def test_rejects_doc_legacy_in_v1(tmp_path: Path) -> None:
    legacy_path = tmp_path / "legacy.doc"
    legacy_path.write_bytes(b"not a docx")

    with pytest.raises(ParserError, match="unsupported_doc_legacy"):
        parse_document(_source(legacy_path, DOC_LEGACY_MIME), "doc-legacy-1")
