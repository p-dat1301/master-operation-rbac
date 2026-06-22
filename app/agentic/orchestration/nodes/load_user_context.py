from app.agentic.contracts.graph_state import GraphState


def load_user_context_node(state: GraphState) -> dict:
    user_id = state.user_context.user_id if state.user_context is not None else state.user_id
    return {
        "user_id": user_id,
        "last_user_question": state.request.query,
    }
