from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None

    @classmethod
    def from_dto(cls, dto) -> "RoleResponse":
        return cls(id=dto.id, name=dto.name, display_name=dto.display_name)


class RoleCreateRequest(BaseModel):
    name: str
    display_name: str


class RoleUpdateRequest(BaseModel):
    name: str
    display_name: str
