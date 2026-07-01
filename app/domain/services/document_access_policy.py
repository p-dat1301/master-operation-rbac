"""Document access-policy adapter for agentic access evaluation."""
from __future__ import annotations

from dataclasses import dataclass

from app.agentic.contracts.access_policy import (
    AccessPolicyMetadata,
    Classification,
    UserAccessContext,
    VisibilityScope,
)
from app.agentic.pipeline.access_control.core import evaluate_access
from app.domain.entities.department import Department
from app.domain.entities.document import Document, DocumentClassification, DocumentVisibility
from app.domain.entities.user import User
from app.domain.services.department_tree import DepartmentTreeService

_ADMIN_ROLES = frozenset({"admin", "bod"})
_MANAGER_ROLE = "manager"

_DOCUMENT_VISIBILITY_TO_POLICY_SCOPE: dict[DocumentVisibility, VisibilityScope] = {
    DocumentVisibility.PUBLIC: VisibilityScope.GLOBAL,
    DocumentVisibility.COMPANY: VisibilityScope.GLOBAL,
    DocumentVisibility.DEPARTMENT: VisibilityScope.DEPARTMENT,
    DocumentVisibility.ROLE: VisibilityScope.ROLE,
    DocumentVisibility.OWNER: VisibilityScope.OWNER,
    DocumentVisibility.MANAGER_SUBTREE: VisibilityScope.MANAGER_SUBTREE,
}

_DOCUMENT_CLASSIFICATION_TO_POLICY_CLASSIFICATION: dict[DocumentClassification, Classification] = {
    DocumentClassification.PUBLIC: Classification.PUBLIC,
    DocumentClassification.INTERNAL: Classification.INTERNAL,
    DocumentClassification.CONFIDENTIAL: Classification.CONFIDENTIAL,
    DocumentClassification.RESTRICTED: Classification.RESTRICTED,
}


@dataclass(frozen=True)
class _PolicySubject:
    access_policy: AccessPolicyMetadata


def build_document_policy(document: Document) -> AccessPolicyMetadata:
    """Map a domain Document into canonical agentic access metadata."""
    department_id = min(document.allowed_departments) if document.allowed_departments else None
    return AccessPolicyMetadata(
        classification=_DOCUMENT_CLASSIFICATION_TO_POLICY_CLASSIFICATION[document.class_document],
        visibility_scope=_DOCUMENT_VISIBILITY_TO_POLICY_SCOPE[document.visibility_scope],
        allowed_roles=tuple(sorted(document.allowed_role_names)),
        department_id=department_id,
        owner_id=document.uploaded_by,
    )


def evaluate_document_access(
    document: Document,
    actor: User,
    departments: list[Department] | None = None,
) -> bool:
    """Evaluate whether actor can access document using canonical access policies."""
    if not actor.is_active:
        return False
    if actor.role_name in _ADMIN_ROLES:
        return True

    policy = build_document_policy(document)
    user_context = UserAccessContext(
        user_id=actor.id,
        role_names=(actor.role_name,),
        department_id=actor.department_id,
        owner_id=actor.id,
    )

    if policy.visibility_scope is VisibilityScope.DEPARTMENT and actor.role_name == _MANAGER_ROLE:
        return _manager_can_access_department_policy(policy, actor, departments)

    if policy.visibility_scope is VisibilityScope.MANAGER_SUBTREE:
        return _manager_can_access_department_policy(policy, actor, departments)

    return evaluate_access(_PolicySubject(policy), user_context).allowed


def _manager_can_access_department_policy(
    policy: AccessPolicyMetadata,
    actor: User,
    departments: list[Department] | None,
) -> bool:
    if actor.role_name != _MANAGER_ROLE or actor.department_id is None or policy.department_id is None:
        return False
    if departments is None:
        return policy.department_id == actor.department_id
    scoped_department_ids = DepartmentTreeService().get_dept_and_descendants(actor.department_id, departments)
    return policy.department_id in scoped_department_ids
