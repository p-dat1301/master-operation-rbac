from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    title: str
    body: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
    channel: str = "in_app"
    type: Optional[str] = None
    message: Optional[str] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    @classmethod
    def from_dto(cls, dto) -> "NotificationResponse":
        return cls(
            id=dto.id,
            recipient_id=dto.recipient_id,
            title=dto.title,
            body=dto.body,
            is_read=dto.is_read,
            created_at=dto.created_at,
            channel=dto.channel,
            type=dto.type,
            message=dto.message,
            sent_at=dto.sent_at,
            read_at=dto.read_at,
        )
