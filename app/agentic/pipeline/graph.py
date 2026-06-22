"""Pipeline graph assembly helpers for the agentic RAG workflow."""
from __future__ import annotations

PIPELINE_STAGES: tuple[str, ...] = (
    "ingestion",
    "parsing",
    "chunking",
    "access_control",
    "indexing",
    "retrieval",
    "generation",
    "audit",
)


def build_pipeline_graph() -> tuple[str, ...]:
    return PIPELINE_STAGES
