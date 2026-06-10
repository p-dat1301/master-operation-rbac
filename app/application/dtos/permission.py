from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domain.entities.permission import Permission


class PermissionOutput(BaseModel):
    id: int
    code: str
    description: Optional[str] = None

    @classmethod
    def from_entity(cls, perm: Permission) -> "PermissionOutput":
        if not isinstance(perm, Permission):
            raise TypeError("Expected Permission entity")
        return cls(
            id=perm.id,
            code=perm.code,
            description=perm.description,
        )
