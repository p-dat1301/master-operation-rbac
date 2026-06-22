from app.agentic.contracts.answer import AnswerResult
from app.agentic.contracts.graph_state import GraphState


def deny_request_node(state: GraphState) -> dict:
    answer = AnswerResult(status="insufficient_permission", answer="Access denied for this conversation or evidence scope.")
    return {
        "answer": answer,
        "last_answer_status": answer.status,
    }
