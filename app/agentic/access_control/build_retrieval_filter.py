"""Adapter-neutral retrieval filter builder for access-controlled evidence lookup."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.agentic.contracts.access_policy import UserAccessContext


class RetrievalFilterExpression(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    clauses: tuple[dict[str, Any], ...] = Field(default_factory=tuple)


def build_retrieval_filter(user_context: UserAccessContext) -> RetrievalFilterExpression:
    clauses: list[dict[str, Any]] = [
        {"visibility_scope": "global"},
    ]
    if user_context.role_names:
        clauses.append(
            {
                "visibility_scope": "role",
                "allowed_roles_any": tuple(sorted(set(user_context.role_names))),
            }
        )
    if user_context.department_id is not None:
        clauses.append(
            {
                "visibility_scope": "department",
                "department_id": user_context.department_id,
            }
        )
    return RetrievalFilterExpression(clauses=tuple(clauses))
