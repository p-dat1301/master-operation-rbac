from __future__ import annotations

import sys
import importlib
from types import ModuleType, SimpleNamespace

import pytest
from fastapi.testclient import TestClient

if "minio" not in sys.modules:
    minio_module = ModuleType("minio")
    minio_module.Minio = object
    minio_error_module = ModuleType("minio.error")
    minio_error_module.S3Error = Exception
    sys.modules["minio"] = minio_module
    sys.modules["minio.error"] = minio_error_module

if "transformers" not in sys.modules:
    transformers_module = ModuleType("transformers")
    transformers_module.AutoModel = object
    transformers_module.AutoTokenizer = object
    sys.modules["transformers"] = transformers_module

from app.main import app
from app.presentation.dependencies.auth_deps import get_current_user

agentic_router = importlib.import_module("app.presentation.api.v1.agentic.router")


class StubUser:
    def __init__(self, role_name: str = "employee") -> None:
        self.id = 7
        self.employee_code = "EMP007"
        self.email = "agentic@example.com"
        self.full_name = "Agentic User"
        self.role_name = role_name
        self.permissions = []
        self.phone = None
        self.job_title = None
        self.department_id = None
        self.manager_id = None
        self.is_active = True


def _override_user(role_name: str = "employee"):
    def _inner():
        return StubUser(role_name=role_name)

    return _inner


def _client(role_name: str = "employee") -> TestClient:
    app.dependency_overrides[get_current_user] = _override_user(role_name)
    return TestClient(app)


def _stub_default_chat_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_invoke_rag_graph(graph, state, *, thread_id: str):
        return SimpleNamespace(
            answer=SimpleNamespace(answer=f"answer:{state.request.query}", status="answered"),
            last_answer_status="answered",
            last_cited_chunk_ids=(),
            last_cited_document_ids=(),
            last_citations=(),
            langfuse_trace_id=None,
        )

    monkeypatch.setattr(agentic_router, "invoke_rag_graph", fake_invoke_rag_graph)


def test_create_conversation_endpoint_returns_conversation() -> None:
    client = _client()
    response = client.post("/api/v1/agentic/conversations", json={"title": "Test Chat"})
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"].startswith("conv-")
    assert body["thread_id"].startswith("thr-")
    assert body["user_id"] == 7


def test_list_and_get_conversation_endpoints_return_created_conversation() -> None:
    client = _client()
    created = client.post("/api/v1/agentic/conversations", json={"title": "History Chat"}).json()
    listed = client.get("/api/v1/agentic/conversations")
    assert listed.status_code == 200
    assert any(item["conversation_id"] == created["conversation_id"] for item in listed.json()["conversations"])
    detail = client.get(f"/api/v1/agentic/conversations/{created['conversation_id']}")
    assert detail.status_code == 200
    assert detail.json()["conversation_id"] == created["conversation_id"]


def test_quick_chat_endpoint_returns_graph_response(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_default_chat_runtime(monkeypatch)
    client = _client()
    response = client.post("/api/v1/agentic/chat", json={"message": "hello", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"].startswith("conv-")
    assert body["thread_id"].startswith("thr-")
    assert body["status"] in {"insufficient_evidence", "insufficient_permission", "answered"}


def test_chat_endpoint_returns_graph_response(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_default_chat_runtime(monkeypatch)
    client = _client()
    conversation = client.post("/api/v1/agentic/conversations", json={"title": "Chat"}).json()
    response = client.post(
        f"/api/v1/agentic/conversations/{conversation['conversation_id']}/messages",
        json={"message": "hello", "top_k": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == conversation["conversation_id"]
    assert body["thread_id"] == conversation["thread_id"]
    assert body["status"] in {"insufficient_evidence", "insufficient_permission", "answered"}


@pytest.mark.asyncio
async def test_chat_endpoint_reuses_checkpointed_state_for_same_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agentic.contracts.chunk import RetrievalRequest
    from app.agentic.contracts.graph_state import GraphState

    client = _client()
    conversation = client.post("/api/v1/agentic/conversations", json={"title": "Thread Continuity"}).json()

    checkpoints: dict[str, GraphState] = {}
    observed_previous_state_queries: list[str] = []

    async def fake_load_previous_graph_state(*, thread_id: str, request: RetrievalRequest, conversation_id: str, user_id: int) -> GraphState:
        state = checkpoints.get(thread_id)
        if state is not None:
            observed_previous_state_queries.append(state.request.query)
            return state
        return GraphState(
            request=request,
            conversation_id=conversation_id,
            thread_id=thread_id,
            user_id=user_id,
        )

    async def fake_invoke_rag_graph(graph, state: GraphState, *, thread_id: str):
        checkpoints[thread_id] = state.model_copy(
            update={
                "last_user_question": state.request.query,
                "memory_summary": f"memory:{state.request.query}",
            }
        )
        return SimpleNamespace(
            answer=SimpleNamespace(answer=f"answer:{state.request.query}", status="answered"),
            last_answer_status="answered",
            last_cited_chunk_ids=(),
            last_cited_document_ids=(),
            last_citations=(),
            langfuse_trace_id=None,
        )

    monkeypatch.setattr(agentic_router, "_load_previous_graph_state", fake_load_previous_graph_state)
    monkeypatch.setattr(agentic_router, "invoke_rag_graph", fake_invoke_rag_graph)

    first = client.post(
        f"/api/v1/agentic/conversations/{conversation['conversation_id']}/messages",
        json={"message": "hello", "top_k": 3},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/agentic/conversations/{conversation['conversation_id']}/messages",
        json={"message": "follow up", "top_k": 3},
    )
    assert second.status_code == 200

    assert observed_previous_state_queries == ["hello"]
    assert second.json()["conversation_id"] == conversation["conversation_id"]
    assert second.json()["thread_id"] == conversation["thread_id"]
    assert second.json()["answer"] == "answer:follow up"


@pytest.mark.asyncio
async def test_chat_endpoint_keeps_checkpointed_state_isolated_across_threads(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agentic.contracts.chunk import RetrievalRequest
    from app.agentic.contracts.graph_state import GraphState

    client = _client()
    first_conversation = client.post("/api/v1/agentic/conversations", json={"title": "Thread One"}).json()
    second_conversation = client.post("/api/v1/agentic/conversations", json={"title": "Thread Two"}).json()

    checkpoints: dict[str, GraphState] = {}
    observed_previous_state_queries: dict[str, list[str]] = {
        first_conversation["thread_id"]: [],
        second_conversation["thread_id"]: [],
    }

    async def fake_load_previous_graph_state(*, thread_id: str, request: RetrievalRequest, conversation_id: str, user_id: int) -> GraphState:
        state = checkpoints.get(thread_id)
        if state is not None:
            observed_previous_state_queries[thread_id].append(state.request.query)
            return state
        return GraphState(
            request=request,
            conversation_id=conversation_id,
            thread_id=thread_id,
            user_id=user_id,
        )

    async def fake_invoke_rag_graph(graph, state: GraphState, *, thread_id: str):
        checkpoints[thread_id] = state.model_copy(
            update={
                "last_user_question": state.request.query,
                "memory_summary": f"memory:{state.request.query}",
            }
        )
        return SimpleNamespace(
            answer=SimpleNamespace(answer=f"answer:{state.request.query}", status="answered"),
            last_answer_status="answered",
            last_cited_chunk_ids=(),
            last_cited_document_ids=(),
            last_citations=(),
            langfuse_trace_id=None,
        )

    monkeypatch.setattr(agentic_router, "_load_previous_graph_state", fake_load_previous_graph_state)
    monkeypatch.setattr(agentic_router, "invoke_rag_graph", fake_invoke_rag_graph)

    first = client.post(
        f"/api/v1/agentic/conversations/{first_conversation['conversation_id']}/messages",
        json={"message": "alpha", "top_k": 3},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/agentic/conversations/{second_conversation['conversation_id']}/messages",
        json={"message": "beta", "top_k": 3},
    )
    assert second.status_code == 200

    third = client.post(
        f"/api/v1/agentic/conversations/{first_conversation['conversation_id']}/messages",
        json={"message": "alpha-2", "top_k": 3},
    )
    assert third.status_code == 200

    assert observed_previous_state_queries[first_conversation["thread_id"]] == ["alpha"]
    assert observed_previous_state_queries[second_conversation["thread_id"]] == []
    assert third.json()["thread_id"] == first_conversation["thread_id"]
    assert third.json()["answer"] == "answer:alpha-2"


def test_list_messages_endpoint_returns_persisted_chat_history(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_default_chat_runtime(monkeypatch)
    client = _client()
    conversation = client.post("/api/v1/agentic/conversations", json={"title": "Messages"}).json()
    chat = client.post(
        f"/api/v1/agentic/conversations/{conversation['conversation_id']}/messages",
        json={"message": "hello", "top_k": 3},
    )
    assert chat.status_code == 200

    response = client.get(f"/api/v1/agentic/conversations/{conversation['conversation_id']}/messages")
    assert response.status_code == 200
    body = response.json()
    assert "messages" in body
    assert len(body["messages"]) >= 1
    assert body["messages"][-1]["user_message"] == "hello"
    assert body["messages"][-1]["assistant_message"] == chat.json()["answer"]
    assert body["messages"][-1]["assistant_status"] == chat.json()["status"]


def test_upload_document_endpoint_returns_forbidden_for_non_manager_roles() -> None:
    client = _client(role_name="employee")
    upload = client.post(
        "/api/v1/agentic/documents",
        files={"file": ("policy.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )
    assert upload.status_code == 403
    assert upload.json()["detail"] == "Only admin and manager can upload documents"


def test_upload_document_endpoint_accepts_multipart_policy() -> None:
    client = _client(role_name="manager")
    upload = client.post(
        "/api/v1/agentic/documents",
        files={"file": ("policy.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={"visibility_scope": "owner"},
    )
    assert upload.status_code == 200
    body = upload.json()
    assert body["parser_target"] == "uploaded-file-parser"
    assert body["filename"] == "policy.pdf"
    assert body["status"] in {"indexed", "failed"}
