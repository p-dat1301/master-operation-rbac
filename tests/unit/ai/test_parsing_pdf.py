"""Unit tests for PDF parsing and normalization."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.agentic.adapters.parsers.base import ParserError
from app.agentic.contracts import (
    AccessPolicyMetadata,
    Classification,
    SourceMetadata,
    SourceType,
    VisibilityScope,
)
from app.agentic.pipeline.parsing import normalize_document, parse_document


PDF_TEXT_BYTES = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 82 >>
stream
BT
/F1 12 Tf
72 100 Td
(Hello PDF parser) Tj
0 -20 Td
(Second line) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000061 00000 n 
0000000118 00000 n 
0000000253 00000 n 
0000000385 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
458
%%EOF
'''

PDF_EMPTY_BYTES = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << >> >>
endobj
4 0 obj
<< /Length 0 >>
stream

endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000061 00000 n 
0000000118 00000 n 
0000000240 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
285
%%EOF
'''


def _source(path: Path) -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri=str(path),
        filename=path.name,
        metadata={
            "access_policy": AccessPolicyMetadata(
                classification=Classification.INTERNAL,
                visibility_scope=VisibilityScope.GLOBAL,
            )
        },
    )


def test_parse_pdf_text_based_to_parsed_document(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample_text.pdf"
    pdf_path.write_bytes(PDF_TEXT_BYTES)

    parsed = parse_document(_source(pdf_path), "doc-pdf-1")

    assert parsed.document_id == "doc-pdf-1"
    assert parsed.parser_name == "langchain-pypdf-loader"
    assert parsed.parser_version == "langchain-pypdf-v1"
    assert "Hello PDF parser" in parsed.raw_text
    assert parsed.extracted_metadata["pages"][0]["page_number"] == 1


def test_normalize_pdf_parsed_document_to_blocks(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample_text.pdf"
    pdf_path.write_bytes(PDF_TEXT_BYTES)

    parsed = parse_document(_source(pdf_path), "doc-pdf-2")
    normalized = normalize_document(parsed)

    assert normalized.document_id == parsed.document_id
    assert normalized.parser_name == parsed.parser_name
    assert normalized.blocks[0].text == "Hello PDF parser"
    assert normalized.blocks[1].text == "Second line"
    assert normalized.blocks[0].citation.page_number == 1
    assert normalized.blocks[1].citation.page_number == 1


def test_parse_pdf_without_text_fails_closed(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample_scanned.pdf"
    pdf_path.write_bytes(PDF_EMPTY_BYTES)

    with pytest.raises(ParserError, match="ocr_not_supported_yet"):
        parse_document(_source(pdf_path), "doc-pdf-3")
