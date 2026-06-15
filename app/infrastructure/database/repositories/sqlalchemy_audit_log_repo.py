"""SQLAlchemy 2.0 async implementation của AuditLogRepository."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.audit_log import AuditLog
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.database.models.audit_log_model import AuditLogModel


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _to_entity(self, model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=model.id,
            user_id=model.actor_id,
            action=model.action,
            resource=model.resource_type,
            resource_id=model.resource_id or 0,
            details=model.details,
            created_at=self._as_utc(model.created_at),
        )

    async def find_by_id(self, log_id: int) -> AuditLog | None:
        stmt = select(AuditLogModel).where(AuditLogModel.id == log_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[AuditLog]:
        stmt = select(AuditLogModel).order_by(AuditLogModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_user(self, user_id: int) -> list[AuditLog]:
        stmt = select(AuditLogModel).where(AuditLogModel.actor_id == user_id).order_by(AuditLogModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_resource(self, resource: str, resource_id: int) -> list[AuditLog]:
        stmt = select(AuditLogModel).where(
            AuditLogModel.resource_type == resource,
            AuditLogModel.resource_id == resource_id,
        ).order_by(AuditLogModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_recent(self, limit: int = 100) -> list[AuditLog]:
        stmt = select(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            actor_id=log.user_id,
            action=log.action,
            resource_type=log.resource,
            resource_id=log.resource_id,
            details=log.details,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
