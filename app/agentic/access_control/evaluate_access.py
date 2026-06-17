"""Fail-closed access evaluation for document and chunk retrieval."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.access_control.resolve_policy import AccessPolicyResolutionError, resolve_policy
from app.agentic.contracts.access_policy import UserAccessContext, VisibilityScope
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord, NormalizedDocument


class AccessDecision(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed: bool
    reason_code: Literal[
        "allow_global",
        "allow_role",
        "allow_department",
        "deny_missing_access_policy",
        "deny_unknown_scope",
        "deny_role_mismatch",
        "deny_department_mismatch",
        "deny_missing_user_roles",
        "deny_missing_user_department",
        "deny_owner_scope_unsupported",
        "deny_manager_scope_unsupported",
    ]
    matched_scope: str | None = Field(default=None, min_length=1)


def evaluate_access(
    subject: NormalizedDocument | DocumentChunk | DocumentRecord,
    user_context: UserAccessContext,
) -> AccessDecision:
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

    scope_name = policy.visibility_scope.value.lower()
    if scope_name == "owner":
        return AccessDecision(allowed=False, reason_code="deny_owner_scope_unsupported")
    if scope_name == "manager_subtree":
        return AccessDecision(allowed=False, reason_code="deny_manager_scope_unsupported")
    return AccessDecision(allowed=False, reason_code="deny_unknown_scope")
