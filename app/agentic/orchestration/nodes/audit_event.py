from app.agentic.contracts.graph_state import GraphState


def audit_event_node(state: GraphState) -> dict:
    return {
        "audit_events": [
            *state.audit_events,
            {
                "event": "graph_turn_completed",
                "conversation_id": state.conversation_id,
                "answer_status": state.last_answer_status,
            },
        ]
    }
