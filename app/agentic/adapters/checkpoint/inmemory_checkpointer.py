"""In-memory LangGraph checkpointer factory."""
from langgraph.checkpoint.memory import InMemorySaver


def build_inmemory_checkpointer() -> InMemorySaver:
    return InMemorySaver()
