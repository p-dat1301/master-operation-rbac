from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domain.entities.role import Role


class RoleOutput(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None

    @classmethod
    def from_entity(cls, role: Role) -> "RoleOutput":
        if not isinstance(role, Role):
            raise TypeError("Expected Role entity")
        return cls(
            id=role.id,
            name=role.name,
            display_name=role.display_name,
        )
