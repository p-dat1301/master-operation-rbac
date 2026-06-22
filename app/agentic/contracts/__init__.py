"""Core contracts for the agentic RAG pipeline."""
from app.agentic.contracts.access_policy import (
    AccessPolicyMetadata,
    Classification,
    UserAccessContext,
    VisibilityScope,
)
from app.agentic.contracts.answer import AnswerCitation, AnswerResult
from app.agentic.contracts.audit import AuditEvent
from app.agentic.contracts.chunk import DocumentChunk, RetrievalCandidate, RetrievalOutcome, RetrievalRequest
from app.agentic.contracts.document import (
    BlockKind,
    CitationMetadata,
    ContentBlock,
    DocumentRecord,
    NormalizedDocument,
    ParsedDocument,
    ParserStatus,
)
from app.agentic.contracts.embedding import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_VERSION,
    MAX_EMBEDDING_TOKENS,
)
from app.agentic.contracts.graph_state import GraphState
from app.agentic.contracts.retrieval import EvidenceBundle, RetrievalFilter
from app.agentic.contracts.source import SourceMetadata, SourceType

__all__ = [
    "AccessPolicyMetadata",
    "AnswerCitation",
    "AnswerResult",
    "AuditEvent",
    "BlockKind",
    "CitationMetadata",
    "Classification",
    "ContentBlock",
    "DocumentChunk",
    "DocumentRecord",
    "EMBEDDING_DIMENSION",
    "EMBEDDING_MODEL_NAME",
    "EMBEDDING_MODEL_VERSION",
    "EvidenceBundle",
    "GraphState",
    "MAX_EMBEDDING_TOKENS",
    "NormalizedDocument",
    "ParsedDocument",
    "ParserStatus",
    "RetrievalCandidate",
    "RetrievalFilter",
    "RetrievalOutcome",
    "RetrievalRequest",
    "SourceMetadata",
    "SourceType",
    "UserAccessContext",
    "VisibilityScope",
]
