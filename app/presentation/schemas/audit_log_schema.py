from __future__ import annotations

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    action: str
    resource: str
    resource_type: Optional[str] = None
    resource_id: int
    details: Optional[dict[str, Any]] = None
    detail: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_dto(cls, dto) -> "AuditLogResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            actor_id=dto.actor_id,
            actor_name=dto.actor_name,
            action=dto.action,
            resource=dto.resource,
            resource_type=dto.resource_type,
            resource_id=dto.resource_id,
            details=dto.details,
            detail=dto.detail,
            ip_address=dto.ip_address,
            created_at=dto.created_at,
        )
