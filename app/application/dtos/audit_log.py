from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

from app.domain.entities.audit_log import AuditLog


class AuditLogOutput(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource: str
    resource_id: int
    details: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, log: AuditLog) -> "AuditLogOutput":
        if not isinstance(log, AuditLog):
            raise TypeError("Expected AuditLog entity")
        return cls(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            details=log.details,
            created_at=log.created_at,
        )
