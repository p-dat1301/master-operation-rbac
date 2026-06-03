from __future__ import annotations

from app.application.ports.notification import INotificationService


class ConsoleNotificationService(INotificationService):
    async def notify_user(self, user_id: int, title: str, message: str) -> None:
        # Simple non-blocking console notifier for dev/testing
        print(f"[notification] to={user_id} title={title} message={message}")
