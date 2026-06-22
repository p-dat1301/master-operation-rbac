"""Agentic API router for chat and document upload."""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select

from app.agentic.adapters.checkpoint.inmemory_checkpointer import build_inmemory_checkpointer
from app.agentic.adapters.parsers.base import ParserError
from app.agentic.adapters.storage.models.agentic_chunk_model import AgenticChunkModel
from app.agentic.adapters.storage.models.agentic_document_model import AgenticDocumentModel
from app.agentic.contracts.access_policy import AccessPolicyMetadata, UserAccessContext
from app.agentic.contracts.chunk import RetrievalRequest
from app.agentic.contracts.graph_state import GraphState
from app.agentic.contracts.source import SourceMetadata, SourceType
from app.agentic.orchestration.conversation_registry import ConversationRegistry
from app.agentic.orchestration.rag_graph import build_rag_graph, invoke_rag_graph
from app.agentic.orchestration.session_seeding import build_next_session_state
from app.agentic.pipeline.chunking.core import chunk_document
from app.agentic.pipeline.ingestion.core import IngestSource
from app.agentic.pipeline.parsing.core import normalize_document, parse_document
from app.di.agentic import AgenticConversationService, build_agentic_retrieval_store
from app.presentation.dependencies.auth_deps import get_current_user
from app.presentation.dependencies.db_deps import get_db
from app.presentation.schemas.agentic_schema import (
    AgenticChatRequest,
    AgenticChatResponse,
    AgenticConversationCreateRequest,
    AgenticConversationListResponse,
    AgenticConversationResponse,
    AgenticConversationSummary,
    AgenticDocumentListResponse,
    AgenticDocumentSummary,
    AgenticDocumentUploadRequest,
    AgenticDocumentUploadResponse,
    AgenticMessageListResponse,
    AgenticMessageResponse,
)


router = APIRouter(prefix="/api/v1/agentic", tags=["agentic"])
_registry = ConversationRegistry()
_service = AgenticConversationService(registry=_registry)
_ingestor = IngestSource()
_graph = build_rag_graph(checkpointer=build_inmemory_checkpointer(), retrieval_store=build_agentic_retrieval_store())
_last_states: dict[str, GraphState] = {}


def _record_chat_turn(*, conversation_id: str, user_message: str, answer_text: str | None, answer_status: str, langfuse_trace_id: str | None) -> None:
    turn_index = len(_registry.list_turns(conversation_id=conversation_id)) + 1
    _registry.register_turn(
        conversation_id=conversation_id,
        turn_id=f"turn-{uuid4().hex}",
        turn_index=turn_index,
        user_message=user_message,
        assistant_message=answer_text,
        assistant_status=answer_status,
        langfuse_trace_id=langfuse_trace_id,
    )


def _ensure_document_upload_permission(actor) -> None:
    role_name = getattr(actor, "role_name", None)
    if role_name not in {"admin", "manager"}:
        raise HTTPException(status_code=403, detail="Only admin and manager can upload documents")


def build_document_upload_policy_request(
    classification: str = Form("internal"),
    visibility_scope: str = Form("owner"),
    allowed_roles: list[str] | None = Form(None),
    department_id: int | None = Form(None),
) -> AgenticDocumentUploadRequest:
    normalized_allowed_roles = [role.strip() for role in (allowed_roles or []) if role and role.strip()]
    return AgenticDocumentUploadRequest(
        classification=classification,
        visibility_scope=visibility_scope,
        allowed_roles=normalized_allowed_roles,
        department_id=department_id,
    )


@router.post("/conversations", response_model=AgenticConversationResponse)
async def create_conversation(
    data: AgenticConversationCreateRequest,
    actor=Depends(get_current_user),
) -> AgenticConversationResponse:
    result = _service.create_conversation(user_id=actor.id, title=data.title)
    return AgenticConversationResponse(**result)


@router.get("/conversations", response_model=AgenticConversationListResponse)
async def list_conversations(actor=Depends(get_current_user)) -> AgenticConversationListResponse:
    conversations = [
        AgenticConversationSummary(
            conversation_id=record.conversation_id,
            thread_id=record.thread_id,
            user_id=record.user_id,
            status=record.status,
            title=record.title,
        )
        for record in _registry.list_conversations_for_user(user_id=actor.id)
    ]
    return AgenticConversationListResponse(conversations=conversations)


@router.get("/conversations/{conversation_id}", response_model=AgenticConversationResponse)
async def get_conversation(conversation_id: str, actor=Depends(get_current_user)) -> AgenticConversationResponse:
    conversation = _registry.ensure_access(conversation_id=conversation_id, user_id=actor.id)
    return AgenticConversationResponse(
        conversation_id=conversation.conversation_id,
        thread_id=conversation.thread_id,
        user_id=conversation.user_id,
        status=conversation.status,
        title=conversation.title,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=AgenticMessageListResponse)
async def list_messages(conversation_id: str, actor=Depends(get_current_user)) -> AgenticMessageListResponse:
    _registry.ensure_access(conversation_id=conversation_id, user_id=actor.id)
    messages = [
        AgenticMessageResponse(
            turn_id=turn.turn_id,
            conversation_id=turn.conversation_id,
            turn_index=turn.turn_index,
            user_message=turn.user_message,
            assistant_message=turn.assistant_message,
            assistant_status=turn.assistant_status,
            langfuse_trace_id=turn.langfuse_trace_id,
        )
        for turn in _registry.list_turns(conversation_id=conversation_id)
    ]
    return AgenticMessageListResponse(messages=messages)


@router.post("/chat", response_model=AgenticChatResponse)
async def quick_chat(data: AgenticChatRequest, actor=Depends(get_current_user), db=Depends(get_db)) -> AgenticChatResponse:
    conversation = next((record for record in _registry.list_conversations_for_user(user_id=actor.id)), None)
    if conversation is None:
        conversation = _registry.get(_service.create_conversation(user_id=actor.id, title="Default chat")["conversation_id"])
    
    previous_state = _last_states.get(conversation.conversation_id)
    if previous_state is None:
        previous_state = GraphState(
            request=RetrievalRequest(query=data.message, top_k=data.top_k),
            conversation_id=conversation.conversation_id,
            user_id=actor.id,
            thread_id=conversation.thread_id,
            user_context=UserAccessContext(user_id=actor.id),
        )
    
    state = build_next_session_state(
        previous_state,
        request=RetrievalRequest(query=data.message, top_k=data.top_k),
        conversation_id=conversation.conversation_id,
    )
    result = await invoke_rag_graph(_graph, state, thread_id=conversation.thread_id)
    _last_states[conversation.conversation_id] = result
    answer = result.answer
    answer_text = answer.answer if answer is not None else "No answer generated."
    answer_status = result.last_answer_status or (answer.status if answer is not None else "unknown")
    _record_chat_turn(
        conversation_id=conversation.conversation_id,
        user_message=data.message,
        answer_text=answer_text,
        answer_status=answer_status,
        langfuse_trace_id=getattr(result, "langfuse_trace_id", None),
    )
    return AgenticChatResponse(
        conversation_id=conversation.conversation_id,
        thread_id=conversation.thread_id,
        answer=answer_text,
        status=answer_status,
        cited_chunk_ids=list(result.last_cited_chunk_ids),
        cited_document_ids=list(result.last_cited_document_ids),
        citations=list(result.last_citations),
    )


@router.post("/conversations/{conversation_id}/messages", response_model=AgenticChatResponse)
async def chat(
    conversation_id: str,
    data: AgenticChatRequest,
    actor=Depends(get_current_user),
    db=Depends(get_db),
) -> AgenticChatResponse:
    conversation = _registry.ensure_access(conversation_id=conversation_id, user_id=actor.id)
    
    previous_state = _last_states.get(conversation.conversation_id)
    if previous_state is None:
        previous_state = GraphState(
            request=RetrievalRequest(query=data.message, top_k=data.top_k),
            conversation_id=conversation.conversation_id,
            user_id=actor.id,
            thread_id=conversation.thread_id,
            user_context=UserAccessContext(user_id=actor.id),
        )
    
    state = build_next_session_state(
        previous_state,
        request=RetrievalRequest(query=data.message, top_k=data.top_k),
        conversation_id=conversation.conversation_id,
    )
    result = await invoke_rag_graph(_graph, state, thread_id=conversation.thread_id)
    _last_states[conversation.conversation_id] = result
    answer = result.answer
    answer_text = answer.answer if answer is not None else "No answer generated."
    answer_status = result.last_answer_status or (answer.status if answer is not None else "unknown")
    _record_chat_turn(
        conversation_id=conversation.conversation_id,
        user_message=data.message,
        answer_text=answer_text,
        answer_status=answer_status,
        langfuse_trace_id=getattr(result, "langfuse_trace_id", None),
    )
    return AgenticChatResponse(
        conversation_id=conversation.conversation_id,
        thread_id=conversation.thread_id,
        answer=answer_text,
        status=answer_status,
        cited_chunk_ids=list(result.last_cited_chunk_ids),
        cited_document_ids=list(result.last_cited_document_ids),
        citations=list(result.last_citations),
    )


@router.post("/documents", response_model=AgenticDocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    upload_policy: AgenticDocumentUploadRequest = Depends(build_document_upload_policy_request),
    actor=Depends(get_current_user),
    db=Depends(get_db),
) -> AgenticDocumentUploadResponse:
    _ensure_document_upload_permission(actor)
    policy_kwargs = {
        "classification": upload_policy.classification,
        "visibility_scope": upload_policy.visibility_scope,
    }

    if upload_policy.visibility_scope == "role":
        if not upload_policy.allowed_roles:
            raise HTTPException(400, detail="role scope requires allowed_roles")
        policy_kwargs["allowed_roles"] = tuple(upload_policy.allowed_roles)
    elif upload_policy.visibility_scope == "department":
        if not upload_policy.department_id:
            raise HTTPException(400, detail="department scope requires department_id")
        policy_kwargs["department_id"] = upload_policy.department_id
    elif upload_policy.visibility_scope == "owner":
        policy_kwargs["owner_id"] = actor.id

    access_policy = AccessPolicyMetadata(**policy_kwargs)
    content = await file.read()
    source = SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type=file.content_type or "application/octet-stream",
        source_uri=file.filename or "uploaded-file",
        filename=file.filename,
        size_bytes=len(content),
        metadata={
            "uploaded_by": str(actor.id),
            "access_policy": access_policy,
        },
    )
    result = _ingestor.ingest(source, access_policy=access_policy)

    db_doc = AgenticDocumentModel(
        document_id=result.document_id,
        source=result.source.model_dump(mode="json"),
        access_policy=result.access_policy.model_dump(),
        status="ingested",
        parser_name=None,
        metadata=result.metadata,
    )
    db.add(db_doc)
    await db.commit()

    final_status = "ingested"
    try:
        parsed = parse_document(source, result.document_id)
        db_doc.status = "parsed"
        db_doc.parser_name = parsed.parser_name
        await db.commit()
        
        normalized = normalize_document(parsed)
        chunks = chunk_document(normalized)
        
        # Persist chunks
        for chunk in chunks:
            db_chunk = AgenticChunkModel(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                token_count=chunk.token_count,
                chunk_index=chunk.chunk_index,
                chunker_version=chunk.chunker_version,
                source_type=chunk.source_type,
                mime_type=chunk.mime_type,
                citation=chunk.citation.model_dump(),
                access_policy=chunk.access_policy.model_dump(),
                chunk_metadata=chunk.metadata,
            )
            db.add(db_chunk)
        
        db_doc.status = "indexed"
        await db.commit()
        final_status = "indexed"
    except ParserError as e:
        db_doc.status = "failed"
        db_doc.metadata = {**db_doc.metadata, "error": str(e)}
        await db.commit()
        final_status = "failed"
    except Exception as e:
        db_doc.status = "failed"
        db_doc.metadata = {**db_doc.metadata, "error": f"Unexpected error: {str(e)}"}
        await db.commit()
        final_status = "failed"
    
    return AgenticDocumentUploadResponse(
        ingestion_id=result.ingestion_id,
        document_id=result.document_id,
        status=final_status,
        parser_target=result.parser_target,
        checksum=result.checksum,
        filename=file.filename,
        mime_type=source.mime_type,
    )


@router.get("/documents", response_model=AgenticDocumentListResponse)
async def list_documents(actor=Depends(get_current_user), db=Depends(get_db)) -> AgenticDocumentListResponse:
    result = await db.execute(select(AgenticDocumentModel))
    docs = result.scalars().all()
    return AgenticDocumentListResponse(documents=[
        AgenticDocumentSummary(
            document_id=d.document_id,
            status=d.status,
            filename=d.metadata.get("filename"),
            mime_type=d.source.get("mime_type"),
        ) for d in docs
    ])


@router.get("/documents/{document_id}", response_model=AgenticDocumentSummary)
async def get_document(document_id: str, actor=Depends(get_current_user), db=Depends(get_db)) -> AgenticDocumentSummary:
    result = await db.execute(select(AgenticDocumentModel).where(AgenticDocumentModel.document_id == document_id))
    document = result.scalars().first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return AgenticDocumentSummary(
        document_id=document.document_id,
        status=document.status,
        filename=document.metadata.get("filename"),
        mime_type=document.source.get("mime_type"),
    )
