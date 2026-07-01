from __future__ import annotations

from pydantic import BaseModel

from app.application.dtos.role import RoleOutput


class RoleResponse(RoleOutput):
    @classmethod
    def from_dto(cls, dto: RoleOutput) -> "RoleResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            display_name=dto.display_name,
        )


class RoleCreateRequest(BaseModel):
    name: str
    display_name: str


class RoleUpdateRequest(BaseModel):
    name: str
    display_name: str
