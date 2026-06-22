from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.presentation.dependencies.auth_deps import get_current_user


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


def test_quick_chat_endpoint_returns_graph_response() -> None:
    client = _client()
    response = client.post("/api/v1/agentic/chat", json={"message": "hello", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"].startswith("conv-")
    assert body["thread_id"].startswith("thr-")
    assert body["status"] in {"insufficient_evidence", "insufficient_permission", "answered"}


def test_chat_endpoint_returns_graph_response() -> None:
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


def test_list_messages_endpoint_returns_persisted_chat_history() -> None:
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
