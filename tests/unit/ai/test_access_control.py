"""Unit tests for access-control primitives."""
from __future__ import annotations

from app.agentic.access_control import build_retrieval_filter, evaluate_access, resolve_policy
from app.agentic.access_control.resolve_policy import AccessPolicyResolutionError
from app.agentic.contracts import (
    AccessPolicyMetadata,
    Classification,
    DocumentChunk,
    SourceMetadata,
    SourceType,
    UserAccessContext,
    VisibilityScope,
)
from app.agentic.contracts.document import CitationMetadata


def _source() -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri="/tmp/policy.pdf",
        filename="policy.pdf",
    )


def _chunk(policy: AccessPolicyMetadata | None) -> DocumentChunk:
    kwargs = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "text": "Confidential HR note",
        "token_count": 5,
        "chunk_index": 0,
        "chunker_version": "token-window-v1",
        "source_type": SourceType.UPLOADED_FILE.value,
        "mime_type": "application/pdf",
        "citation": CitationMetadata(page_number=1),
        "metadata": {},
    }
    if policy is None:
        return DocumentChunk.model_construct(access_policy=None, **kwargs)
    return DocumentChunk(access_policy=policy, **kwargs)


def test_authorized_department_chunk_is_allowed() -> None:
    chunk = _chunk(
        AccessPolicyMetadata(
            classification=Classification.INTERNAL,
            visibility_scope=VisibilityScope.DEPARTMENT,
            department_id=10,
        )
    )
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    decision = evaluate_access(chunk, user)

    assert decision.allowed is True
    assert decision.reason_code == "allow_department"
    assert resolve_policy(chunk).department_id == 10


def test_missing_policy_fails_closed() -> None:
    chunk = _chunk(None)
    user = UserAccessContext(user_id=1, role_names=("employee",), department_id=10)

    decision = evaluate_access(chunk, user)

    assert decision.allowed is False
    assert decision.reason_code == "deny_missing_access_policy"
    try:
        resolve_policy(chunk)
    except AccessPolicyResolutionError as exc:
        assert str(exc) == "missing_access_policy"
    else:
        raise AssertionError("expected missing access policy failure")


def test_role_filter_contains_global_and_role_clauses() -> None:
    user = UserAccessContext(user_id=7, role_names=("manager", "hr"), department_id=None)

    retrieval_filter = build_retrieval_filter(user)

    assert retrieval_filter.clauses[0] == {"visibility_scope": "global"}
    assert retrieval_filter.clauses[1]["visibility_scope"] == "role"
    assert retrieval_filter.clauses[1]["allowed_roles_any"] == ("hr", "manager")
