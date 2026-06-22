"""Postgres LangGraph checkpointer factory."""
from __future__ import annotations

from dataclasses import dataclass

from langgraph.checkpoint.postgres import PostgresSaver


@dataclass(frozen=True)
class PostgresCheckpointerFactory:
    database_url: str

    def build(self) -> PostgresSaver:
        saver = PostgresSaver.from_conn_string(self.database_url)
        saver.setup()
        return saver
