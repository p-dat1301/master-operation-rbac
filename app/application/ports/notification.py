from typing import Protocol


class INotificationService(Protocol):
    """Port để Application layer gửi notification mà không phụ thuộc WebSocket/Telegram cụ thể."""

    async def notify_user(self, user_id: int, title: str, message: str) -> None:
        ...
