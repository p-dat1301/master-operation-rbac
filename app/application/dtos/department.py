from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.domain.entities.department import Department


class DepartmentOutput(BaseModel):
    id: int
    name: str
    level: int
    parent_id: Optional[int] = None

    @classmethod
    def from_entity(cls, dept: Department) -> "DepartmentOutput":
        if not isinstance(dept, Department):
            raise TypeError("Expected Department entity")
        return cls(
            id=dept.id,
            name=dept.name,
            level=dept.level,
            parent_id=dept.parent_id,
        )
