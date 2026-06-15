from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class Notification:
    id: int
    recipient_id: int
    title: str = "Notification"
    body: Optional[str] = None
    channel: str = "in_app"
    is_read: bool = False
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    type: Optional[str] = None
    message: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    sent_at: Optional[datetime] = None
