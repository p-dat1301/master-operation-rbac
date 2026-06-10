from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource: str
    resource_id: int
    details: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dto(cls, dto) -> "AuditLogResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            action=dto.action,
            resource=dto.resource,
            resource_id=dto.resource_id,
            details=dto.details,
            created_at=dto.created_at,
        )
