"""Role-aware retrieval stage for agentic RAG."""
from .core import (
    RetrievalStore,
    RetrievalConfig,
    retrieve_evidence,
)
from .evidence_bundle import build_evidence_bundle
from .rerank import rerank_candidates

__all__ = [
    "RetrievalConfig",
    "RetrievalStore",
    "build_evidence_bundle",
    "rerank_candidates",
    "retrieve_evidence",
]
