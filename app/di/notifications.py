from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.notification.list_notifications import ListNotificationsUseCase


def provide_list_notifications(db: AsyncSession) -> ListNotificationsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_notification_repo import SQLAlchemyNotificationRepository

    notification_repo = SQLAlchemyNotificationRepository(db)
    return ListNotificationsUseCase(notification_repo=notification_repo)
