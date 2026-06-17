"""Base parser adapter contract."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.agentic.contracts.document import ParsedDocument
from app.agentic.contracts.source import SourceMetadata


class ParserError(ValueError):
    """Controlled parser failure for unsupported or unreadable inputs."""


class BaseParser(ABC):
    name: str
    version: str

    @abstractmethod
    def parse(self, source: SourceMetadata, document_id: str) -> ParsedDocument:
        raise NotImplementedError
