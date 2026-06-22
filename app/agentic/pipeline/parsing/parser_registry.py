"""Parser registry helpers."""
from app.agentic.adapters.parsers.base import BaseParser
from app.agentic.adapters.parsers.docx_parser import DOCX_MIME, DocxParser
from app.agentic.adapters.parsers.pdf_parser import PdfTextParser


def parser_registry() -> dict[str, BaseParser]:
    docx_parser = DocxParser()
    return {
        "application/pdf": PdfTextParser(),
        DOCX_MIME: docx_parser,
        "application/msword": docx_parser,
    }
