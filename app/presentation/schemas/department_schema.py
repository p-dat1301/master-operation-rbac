from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class DepartmentResponse(BaseModel):
    id: int
    name: str
    level: int
    parent_id: Optional[int] = None

    @classmethod
    def from_dto(cls, dto) -> "DepartmentResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            level=dto.level,
            parent_id=dto.parent_id,
        )
