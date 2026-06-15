from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

from app.domain.entities.audit_log import AuditLog


class AuditLogOutput(BaseModel):
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
    def from_entity(cls, log: AuditLog) -> "AuditLogOutput":
        if not isinstance(log, AuditLog):
            raise TypeError("Expected AuditLog entity")
        return cls(
            id=log.id,
            user_id=log.user_id,
            actor_id=log.user_id,
            actor_name=None,
            action=log.action,
            resource=log.resource,
            resource_type=log.resource,
            resource_id=log.resource_id,
            details=log.details,
            detail=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
