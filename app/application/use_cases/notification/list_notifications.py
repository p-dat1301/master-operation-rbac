from app.application.dtos.notification import NotificationOutput
from app.domain.entities.user import User
from app.domain.repositories.notification_repository import NotificationRepository


class ListNotificationsUseCase:
    """Use case lấy danh sách thông báo của người dùng hiện tại."""

    def __init__(self, notification_repo: NotificationRepository) -> None:
        self.notification_repo = notification_repo

    async def execute(self, actor: User) -> list[NotificationOutput]:
        records = await self.notification_repo.list_by_recipient(actor.id)
        return [NotificationOutput.from_entity(r) for r in records]
