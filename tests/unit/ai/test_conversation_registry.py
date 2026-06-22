from __future__ import annotations

import pytest

from app.agentic.orchestration.conversation_registry import ConversationAccessDenied, ConversationRegistry


def test_register_starts_conversation_with_single_thread() -> None:
    registry = ConversationRegistry()

    record = registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    assert record.thread_id == "thr-1"
    assert record.conversation_id == "conv-1"
    assert record.user_id == 7


def test_register_turn_creates_turn_record_for_existing_conversation() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    turn = registry.register_turn(
        conversation_id="conv-1",
        turn_id="turn-2",
        turn_index=2,
        user_message="hello",
        assistant_message="world",
        assistant_status="pending",
    )

    assert turn.turn_id == "turn-2"
    assert turn.conversation_id == "conv-1"
    assert turn.turn_index == 2
    assert turn.user_message == "hello"
    assert turn.assistant_message == "world"
    assert turn.assistant_status == "pending"


def test_ensure_access_rejects_foreign_user_access() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    with pytest.raises(ConversationAccessDenied):
        registry.ensure_access(conversation_id="conv-1", user_id=8)


def test_get_turn_rejects_missing_turn() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")

    with pytest.raises(ConversationAccessDenied):
        registry.get_turn("turn-9")


def test_list_turns_returns_conversation_history_in_order() -> None:
    registry = ConversationRegistry()
    registry.register(conversation_id="conv-1", user_id=7, thread_id="thr-1")
    registry.register_turn(
        conversation_id="conv-1",
        turn_id="turn-2",
        turn_index=2,
        user_message="second",
        assistant_message="reply-2",
        assistant_status="answered",
    )
    registry.register_turn(
        conversation_id="conv-1",
        turn_id="turn-1",
        turn_index=1,
        user_message="first",
        assistant_message="reply-1",
        assistant_status="answered",
    )

    turns = registry.list_turns(conversation_id="conv-1")

    assert [turn.turn_id for turn in turns] == ["turn-1", "turn-2"]
    assert turns[0].user_message == "first"
    assert turns[1].assistant_message == "reply-2"
