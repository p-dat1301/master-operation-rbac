"""PDF parser adapter for text-based PDFs."""
from __future__ import annotations

from langchain_community.document_loaders import PyPDFLoader

from app.agentic.adapters.parsers.base import BaseParser, ParserError
from app.agentic.contracts.document import ParsedDocument, ParserStatus
from app.agentic.contracts.source import SourceMetadata


class PdfTextParser(BaseParser):
    name = "langchain-pypdf-loader"
    version = "langchain-pypdf-v1"

    def parse(self, source: SourceMetadata, document_id: str) -> ParsedDocument:
        try:
            loader = PyPDFLoader(source.source_uri)
            docs = loader.load()
        except Exception as exc:  # pragma: no cover - controlled failure mapping
            raise ParserError(f"failed to load pdf with langchain: {source.source_uri}") from exc

        page_meta: list[dict[str, object]] = []
        extracted_pages: list[str] = []
        blocks: list[dict[str, object]] = []
        block_index = 0
        for fallback_page_number, doc in enumerate(docs, start=1):
            text = (doc.page_content or "").strip()
            raw_page_number = doc.metadata.get("page", fallback_page_number)
            if isinstance(raw_page_number, int):
                page_number = raw_page_number + 1 if raw_page_number < 1 else raw_page_number
            else:
                page_number = fallback_page_number
            if text:
                extracted_pages.append(text)
                for line in text.splitlines():
                    if not line.strip():
                        continue
                    blocks.append(
                        {
                            "kind": "paragraph",
                            "text": line.strip(),
                            "page_number": page_number,
                            "section_path": (),
                            "block_anchor": f"pdf-block-{block_index}",
                            "metadata": {},
                        }
                    )
                    block_index += 1
            page_meta.append({"page_number": page_number, "text_length": len(text)})

        raw_text = "\n\n".join(extracted_pages).strip()
        if not raw_text:
            raise ParserError("ocr_not_supported_yet: pdf contains no extractable text")

        return ParsedDocument(
            document_id=document_id,
            source=source,
            parser_name=self.name,
            parser_version=self.version,
            status=ParserStatus.PARSED,
            raw_text=raw_text,
            extracted_metadata={"pages": page_meta, "blocks": blocks, "loader": "PyPDFLoader"},
        )
