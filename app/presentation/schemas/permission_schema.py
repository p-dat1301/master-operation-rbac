from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.application.dtos.permission import PermissionOutput


class PermissionResponse(PermissionOutput):
    pass


class PermissionCreateRequest(BaseModel):
    code: str
    description: Optional[str] = None


class PermissionUpdateRequest(BaseModel):
    code: str
    description: Optional[str] = None
