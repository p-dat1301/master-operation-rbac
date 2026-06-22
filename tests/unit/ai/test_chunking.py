"""Unit tests for token-aware chunking."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from unittest.mock import patch

from app.agentic.pipeline.chunking import ChunkConfig, chunk_document
from app.agentic.pipeline.chunking.tokenizer import (
    FALLBACK_TOKENIZER_POLICY,
    TOKENIZER_POLICY,
    WhitespaceTokenizerAdapter,
    get_tokenizer_adapter,
)
from app.agentic.contracts import (
    AccessPolicyMetadata,
    Classification,
    SourceMetadata,
    SourceType,
    VisibilityScope,
)
from app.agentic.pipeline.parsing import normalize_document, parse_document


PDF_BYTES = b'''%PDF-1.4
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
<< /Length 93 >>
stream
BT
/F1 12 Tf
72 100 Td
(Chunk alpha beta gamma delta) Tj
0 -20 Td
(Epsilon zeta eta theta iota) Tj
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
0000000397 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
470
%%EOF
'''


def _policy() -> AccessPolicyMetadata:
    return AccessPolicyMetadata(
        classification=Classification.INTERNAL,
        visibility_scope=VisibilityScope.GLOBAL,
    )


def _pdf_source(path: Path) -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri=str(path),
        filename=path.name,
        metadata={"access_policy": _policy()},
    )


def _write_docx_fixture(path: Path) -> None:
    document_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>
  <w:body>
    <w:p><w:pPr><w:pStyle w:val='Heading1'/></w:pPr><w:r><w:t>Chunk Title</w:t></w:r></w:p>
    <w:p><w:r><w:t>Docx paragraph one</w:t></w:r></w:p>
    <w:p><w:r><w:t>Docx paragraph two</w:t></w:r></w:p>
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
    with ZipFile(path, 'w') as archive:
        archive.writestr('[Content_Types].xml', content_types)
        archive.writestr('_rels/.rels', rels)
        archive.writestr('word/_rels/document.xml.rels', rels)
        archive.writestr('word/document.xml', document_xml)


def test_chunk_document_preserves_pdf_provenance_and_token_budget(tmp_path: Path) -> None:
    pdf_path = tmp_path / "chunkable.pdf"
    pdf_path.write_bytes(PDF_BYTES)
    normalized = normalize_document(parse_document(_pdf_source(pdf_path), "doc-chunk-pdf"))

    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=4, overlap_tokens=1))

    assert chunks
    assert all(chunk.document_id == normalized.document_id for chunk in chunks)
    assert all(chunk.chunker_version == "token-window-v1" for chunk in chunks)
    assert all(chunk.token_count is not None and chunk.token_count <= 4 for chunk in chunks)
    assert all(chunk.citation.page_number == 1 for chunk in chunks)
    assert chunks[0].metadata["block_ids"]
    assert chunks[0].metadata["parser_name"] == normalized.parser_name
    assert ChunkConfig().tokenizer_policy == TOKENIZER_POLICY
    assert chunks[0].metadata["embedding_model"] == "intfloat/multilingual-e5-large"
    assert chunks[0].metadata["tokenizer_policy"] in {TOKENIZER_POLICY, FALLBACK_TOKENIZER_POLICY}


def test_chunk_document_preserves_docx_section_provenance(tmp_path: Path) -> None:
    docx_path = tmp_path / "chunkable.docx"
    _write_docx_fixture(docx_path)
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        source_uri=str(docx_path),
        filename=docx_path.name,
        metadata={"access_policy": _policy()},
    )
    normalized = normalize_document(parse_document(source, "doc-chunk-docx"))

    chunks = chunk_document(normalized, ChunkConfig(max_chunk_tokens=50, overlap_tokens=5))

    assert len(chunks) == 1
    assert chunks[0].citation.section_path == ("Chunk Title",)
    assert chunks[0].metadata["title"] == "chunkable.docx"
    assert chunks[0].metadata["page_numbers"] == []


def test_tokenizer_adapter_falls_back_to_whitespace_when_transformers_is_unavailable() -> None:
    get_tokenizer_adapter.cache_clear()
    with patch("builtins.__import__", side_effect=ImportError("transformers unavailable")):
        adapter = get_tokenizer_adapter()

    assert isinstance(adapter, WhitespaceTokenizerAdapter)
    assert adapter.policy == FALLBACK_TOKENIZER_POLICY
    assert adapter.encode("alpha beta gamma") == ["alpha", "beta", "gamma"]
    get_tokenizer_adapter.cache_clear()
