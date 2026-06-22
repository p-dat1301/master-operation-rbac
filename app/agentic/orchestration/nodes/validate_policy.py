from app.agentic.contracts.graph_state import GraphState


def route_after_retrieval(state: GraphState) -> str:
    if state.retrieval_candidate_count <= 0:
        return "deny_request"
    return "generate_answer"
