from abc import ABC, abstractmethod

from app.domain.entities.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def find_by_id(self, notification_id: int) -> Notification | None:
        pass

    @abstractmethod
    async def list_by_recipient(self, recipient_id: int) -> list[Notification]:
        pass

    @abstractmethod
    async def list_unread_by_recipient(self, recipient_id: int) -> list[Notification]:
        pass

    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: int) -> Notification:
        pass

    @abstractmethod
    async def mark_all_as_read(self, recipient_id: int) -> int:
        pass