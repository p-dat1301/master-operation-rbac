"""Checkpoint adapter package."""
from app.agentic.adapters.checkpoint.base import Checkpointer
from app.agentic.adapters.checkpoint.inmemory_checkpointer import build_inmemory_checkpointer

__all__ = ["Checkpointer", "build_inmemory_checkpointer", "PostgresCheckpointerFactory"]


def __getattr__(name: str):
    if name == "PostgresCheckpointerFactory":
        from app.agentic.adapters.checkpoint.postgres_checkpointer import PostgresCheckpointerFactory

        return PostgresCheckpointerFactory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
