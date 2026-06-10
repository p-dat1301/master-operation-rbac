from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

from app.domain.entities.notification import Notification


class NotificationOutput(BaseModel):
    id: int
    recipient_id: int
    type: str
    channel: str
    message: Optional[str] = None
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, notif: Notification) -> "NotificationOutput":
        if not isinstance(notif, Notification):
            raise TypeError("Expected Notification entity")
        return cls(
            id=notif.id,
            recipient_id=notif.recipient_id,
            type=notif.type,
            channel=notif.channel,
            message=notif.message,
            is_read=notif.is_read,
            sent_at=notif.sent_at,
            read_at=notif.read_at,
        )
