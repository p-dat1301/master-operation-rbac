"""Checkpoint adapter boundary for LangGraph savers."""
from __future__ import annotations

from typing import Protocol


class Checkpointer(Protocol):
    def get_tuple(self, config): ...
    def put(self, config, checkpoint, metadata, new_versions): ...


__all__ = ["Checkpointer"]
