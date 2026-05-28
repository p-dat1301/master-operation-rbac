from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class Notification:
    id: int
    recipient_id: int
    type: str
    channel: str
    message: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None