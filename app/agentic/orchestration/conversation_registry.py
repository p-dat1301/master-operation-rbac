"""Conversation registry for RAG conversation ownership."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class ConversationAccessDenied(PermissionError):
    pass


@dataclass(frozen=True)
class ConversationRecord:
    conversation_id: str
    user_id: int
    thread_id: str
    status: str = "active"
    title: str | None = None
    expires_at: datetime = datetime.now(timezone.utc)


@dataclass(frozen=True)
class TurnRecord:
    turn_id: str
    conversation_id: str
    turn_index: int
    user_message: str
    assistant_message: str | None = None
    assistant_status: str = "pending"
    langfuse_trace_id: str | None = None


class ConversationRegistry:
    """Minimal in-memory conversation registry boundary.

    The persisted implementation lives in the database models/adapters layer;
    this package-level registry is a thin orchestration-facing contract.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, ConversationRecord] = {}
        self._turns: dict[str, TurnRecord] = {}

    def register(
        self,
        *,
        conversation_id: str,
        user_id: int,
        thread_id: str,
        title: str | None = None,
    ) -> ConversationRecord:
        record = ConversationRecord(
            conversation_id=conversation_id,
            user_id=user_id,
            thread_id=thread_id,
            title=title,
        )
        self._conversations[conversation_id] = record
        return record

    def register_turn(
        self,
        *,
        conversation_id: str,
        turn_id: str,
        turn_index: int,
        user_message: str,
        assistant_message: str | None = None,
        assistant_status: str = "pending",
        langfuse_trace_id: str | None = None,
    ) -> TurnRecord:
        self.get(conversation_id)
        turn_record = TurnRecord(
            turn_id=turn_id,
            conversation_id=conversation_id,
            turn_index=turn_index,
            user_message=user_message,
            assistant_message=assistant_message,
            assistant_status=assistant_status,
            langfuse_trace_id=langfuse_trace_id,
        )
        self._turns[turn_id] = turn_record
        return turn_record

    def get(self, conversation_id: str) -> ConversationRecord:
        try:
            return self._conversations[conversation_id]
        except KeyError as exc:
            raise ConversationAccessDenied(f"conversation_not_found:{conversation_id}") from exc

    def get_turn(self, turn_id: str) -> TurnRecord:
        try:
            return self._turns[turn_id]
        except KeyError as exc:
            raise ConversationAccessDenied(f"turn_not_found:{turn_id}") from exc

    def list_conversations_for_user(self, *, user_id: int) -> list[ConversationRecord]:
        conversations = [record for record in self._conversations.values() if record.user_id == user_id]
        conversations.sort(key=lambda record: record.conversation_id)
        return conversations

    def list_turns(self, *, conversation_id: str) -> list[TurnRecord]:
        self.get(conversation_id)
        turns = [turn for turn in self._turns.values() if turn.conversation_id == conversation_id]
        turns.sort(key=lambda turn: turn.turn_index)
        return turns

    def ensure_access(self, *, conversation_id: str, user_id: int) -> ConversationRecord:
        record = self.get(conversation_id)
        if record.user_id != user_id:
            raise ConversationAccessDenied(f"conversation_access_denied:{conversation_id}")
        return record
