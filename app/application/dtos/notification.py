from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.notification import Notification


class NotificationOutput(BaseModel):
    id: int
    recipient_id: int
    title: str
    body: Optional[str] = None
    channel: str
    is_read: bool = False
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    type: Optional[str] = None
    message: Optional[str] = None
    sent_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, notif: Notification) -> "NotificationOutput":
        if not isinstance(notif, Notification):
            raise TypeError("Expected Notification entity")
        return cls(
            id=notif.id,
            recipient_id=notif.recipient_id,
            title=notif.title,
            body=notif.body,
            channel=notif.channel,
            is_read=notif.is_read,
            created_at=notif.created_at,
            read_at=notif.read_at,
            type=notif.type,
            message=notif.message,
            sent_at=notif.sent_at,
        )
