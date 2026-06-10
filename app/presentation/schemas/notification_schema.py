from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    type: str
    channel: str
    message: Optional[str] = None
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    @classmethod
    def from_dto(cls, dto) -> "NotificationResponse":
        return cls(
            id=dto.id,
            recipient_id=dto.recipient_id,
            type=dto.type,
            channel=dto.channel,
            message=dto.message,
            is_read=dto.is_read,
            sent_at=dto.sent_at,
            read_at=dto.read_at,
        )
