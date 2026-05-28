from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class AuditLog:
    id: int
    user_id: Optional[int]
    action: str
    resource: str
    resource_id: int
    details: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None