from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: int
    code: str
    description: Optional[str] = None

    @classmethod
    def from_dto(cls, dto) -> "PermissionResponse":
        return cls(id=dto.id, code=dto.code, description=dto.description)


class PermissionCreateRequest(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionUpdateRequest(BaseModel):
    code: str
    description: Optional[str] = None
