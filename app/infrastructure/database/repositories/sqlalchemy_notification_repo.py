"""SQLAlchemy 2.0 async implementation của NotificationRepository."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.notification import Notification
from app.domain.repositories.notification_repository import NotificationRepository
from app.infrastructure.database.models.notification_model import NotificationModel


class SQLAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            recipient_id=model.recipient_id,
            type="general",
            channel=model.channel,
            message=model.body,
            is_read=model.is_read,
        )

    async def find_by_id(self, notification_id: int) -> Notification | None:
        stmt = select(NotificationModel).where(NotificationModel.id == notification_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_by_recipient(self, recipient_id: int) -> list[Notification]:
        stmt = select(NotificationModel).where(NotificationModel.recipient_id == recipient_id).order_by(NotificationModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_unread_by_recipient(self, recipient_id: int) -> list[Notification]:
        stmt = select(NotificationModel).where(
            NotificationModel.recipient_id == recipient_id,
            NotificationModel.is_read == False,
        ).order_by(NotificationModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, notification: Notification) -> Notification:
        model = NotificationModel(
            recipient_id=notification.recipient_id,
            sender_id=None,
            title=notification.type or "Notification",
            body=notification.message,
            channel=notification.channel,
            is_read=notification.is_read,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def mark_as_read(self, notification_id: int) -> Notification:
        stmt = select(NotificationModel).where(NotificationModel.id == notification_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Notification {notification_id} not found")
        model.is_read = True
        await self._session.flush()
        return self._to_entity(model)

    async def mark_all_as_read(self, recipient_id: int) -> int:
        stmt = select(NotificationModel).where(
            NotificationModel.recipient_id == recipient_id,
            NotificationModel.is_read == False,
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        for model in models:
            model.is_read = True
        await self._session.flush()
        return len(models)
