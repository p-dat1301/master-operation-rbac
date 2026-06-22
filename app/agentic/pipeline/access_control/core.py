"""Canonical access-control stage for agentic pipeline."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import AccessPolicyMetadata, UserAccessContext, VisibilityScope
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord, NormalizedDocument


class RetrievalFilterExpression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    clauses: tuple[dict[str, object], ...] = Field(default_factory=tuple)


def build_retrieval_filter(user_context: UserAccessContext) -> RetrievalFilterExpression:
    clauses: list[dict[str, object]] = [{"visibility_scope": "global"}]
    if user_context.role_names:
        clauses.append({"visibility_scope": "role", "allowed_roles_any": tuple(sorted(set(user_context.role_names)))})
    if user_context.department_id is not None:
        clauses.append({"visibility_scope": "department", "department_id": user_context.department_id})
    clauses.append({"visibility_scope": "owner", "owner_id": user_context.user_id})
    return RetrievalFilterExpression(clauses=tuple(clauses))


class AccessDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed: bool
    reason_code: Literal[
        "allow_global",
        "allow_role",
        "allow_department",
        "allow_owner",
        "deny_missing_access_policy",
        "deny_unknown_scope",
        "deny_role_mismatch",
        "deny_department_mismatch",
        "deny_missing_user_roles",
        "deny_missing_user_department",
        "deny_missing_user_id",
        "deny_owner_mismatch",
        "deny_owner_scope_unsupported",
        "deny_manager_scope_unsupported",
    ]
    matched_scope: str | None = Field(default=None, min_length=1)


class AccessPolicyResolutionError(ValueError):
    pass


def resolve_policy(subject: NormalizedDocument | DocumentChunk | DocumentRecord) -> AccessPolicyMetadata:
    policy = getattr(subject, "access_policy", None)
    if not isinstance(policy, AccessPolicyMetadata):
        raise AccessPolicyResolutionError("missing_access_policy")
    return policy


def evaluate_access(subject: NormalizedDocument | DocumentChunk | DocumentRecord, user_context: UserAccessContext) -> AccessDecision:
    try:
        policy = resolve_policy(subject)
    except AccessPolicyResolutionError:
        return AccessDecision(allowed=False, reason_code="deny_missing_access_policy")
    if policy.visibility_scope is VisibilityScope.GLOBAL:
        return AccessDecision(allowed=True, reason_code="allow_global", matched_scope=policy.visibility_scope.value)
    if policy.visibility_scope is VisibilityScope.ROLE:
        if not user_context.role_names:
            return AccessDecision(allowed=False, reason_code="deny_missing_user_roles")
        if not policy.allowed_roles:
            return AccessDecision(allowed=False, reason_code="deny_role_mismatch")
        if set(user_context.role_names).intersection(policy.allowed_roles):
            return AccessDecision(allowed=True, reason_code="allow_role", matched_scope=policy.visibility_scope.value)
        return AccessDecision(allowed=False, reason_code="deny_role_mismatch")
    if policy.visibility_scope is VisibilityScope.DEPARTMENT:
        if user_context.department_id is None:
            return AccessDecision(allowed=False, reason_code="deny_missing_user_department")
        if policy.department_id is None:
            return AccessDecision(allowed=False, reason_code="deny_department_mismatch")
        if policy.department_id == user_context.department_id:
            return AccessDecision(allowed=True, reason_code="allow_department", matched_scope=policy.visibility_scope.value)
        return AccessDecision(allowed=False, reason_code="deny_department_mismatch")
    if policy.visibility_scope is VisibilityScope.OWNER:
        if user_context.user_id is None:
            return AccessDecision(allowed=False, reason_code="deny_missing_user_id")
        if policy.owner_id is None:
            return AccessDecision(allowed=False, reason_code="deny_owner_scope_unsupported")
        if policy.owner_id == user_context.user_id:
            return AccessDecision(allowed=True, reason_code="allow_owner", matched_scope=policy.visibility_scope.value)
        return AccessDecision(allowed=False, reason_code="deny_owner_mismatch")
    if policy.visibility_scope is VisibilityScope.MANAGER_SUBTREE:
        return AccessDecision(allowed=False, reason_code="deny_manager_scope_unsupported")
    return AccessDecision(allowed=False, reason_code="deny_unknown_scope")
