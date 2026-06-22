"""Access-policy contracts shared by retrieval and indexing."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Classification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class VisibilityScope(StrEnum):
    GLOBAL = "global"
    ROLE = "role"
    DEPARTMENT = "department"
    OWNER = "owner"
    MANAGER_SUBTREE = "manager_subtree"


class AccessPolicyMetadata(BaseModel):
    """Deny-by-default access metadata attached to documents and chunks."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Classification
    visibility_scope: VisibilityScope
    allowed_roles: tuple[str, ...] = Field(default_factory=tuple)
    department_id: int | None = Field(default=None, ge=1)
    owner_id: int | None = Field(default=None, ge=1)
    policy_version: str = Field(default="access-policy-v1", min_length=1)

    @model_validator(mode="after")
    def validate_scope_requirements(self) -> "AccessPolicyMetadata":
        if self.visibility_scope is VisibilityScope.ROLE and not self.allowed_roles:
            raise ValueError("role-scoped policy requires allowed_roles")
        if self.visibility_scope is VisibilityScope.DEPARTMENT and self.department_id is None:
            raise ValueError("department-scoped policy requires department_id")
        if self.visibility_scope is VisibilityScope.OWNER and self.owner_id is None:
            raise ValueError("owner-scoped policy requires owner_id")
        return self


class UserAccessContext(BaseModel):
    """Minimal RBAC context needed before retrieval can expose evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    user_id: int = Field(ge=1)
    role_names: tuple[str, ...] = Field(default_factory=tuple)
    department_id: int | None = Field(default=None, ge=1)
    owner_id: int | None = Field(default=None, ge=1)
