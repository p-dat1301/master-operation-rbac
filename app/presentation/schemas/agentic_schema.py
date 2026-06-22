"""Agentic conversation API schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AgenticConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class AgenticConversationSummary(BaseModel):
    conversation_id: str
    thread_id: str
    user_id: int
    status: str
    title: str | None = None


class AgenticConversationResponse(AgenticConversationSummary):
    pass


class AgenticConversationListResponse(BaseModel):
    conversations: list[AgenticConversationSummary] = Field(default_factory=list)


class AgenticMessageResponse(BaseModel):
    turn_id: str
    conversation_id: str
    turn_index: int
    user_message: str
    assistant_message: str | None = None
    assistant_status: str
    langfuse_trace_id: str | None = None


class AgenticMessageListResponse(BaseModel):
    messages: list[AgenticMessageResponse] = Field(default_factory=list)


class AgenticChatRequest(BaseModel):
    message: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class AgenticChatResponse(BaseModel):
    conversation_id: str
    thread_id: str
    answer: str
    status: str
    cited_chunk_ids: list[str] = Field(default_factory=list)
    cited_document_ids: list[str] = Field(default_factory=list)
    citations: list[dict[str, object]] = Field(default_factory=list)


class AgenticDocumentUploadRequest(BaseModel):
    classification: str = Field(default="internal", min_length=1)
    visibility_scope: str = Field(default="owner", min_length=1)
    allowed_roles: list[str] = Field(default_factory=list)
    department_id: int | None = Field(default=None, ge=1)


class AgenticDocumentUploadResponse(BaseModel):
    ingestion_id: str
    document_id: str
    status: str
    parser_target: str
    checksum: str
    filename: str | None = None
    mime_type: str


class AgenticDocumentSummary(BaseModel):
    document_id: str
    status: str
    filename: str | None = None
    mime_type: str | None = None


class AgenticDocumentListResponse(BaseModel):
    documents: list[AgenticDocumentSummary] = Field(default_factory=list)
