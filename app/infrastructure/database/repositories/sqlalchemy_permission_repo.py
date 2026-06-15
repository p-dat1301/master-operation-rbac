"""SQLAlchemy 2.0 async implementation của PermissionRepository."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.permission import Permission
from app.domain.repositories.permission_repository import PermissionRepository
from app.infrastructure.database.models.permission_model import PermissionModel


class SQLAlchemyPermissionRepository(PermissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _to_entity(self, model: PermissionModel) -> Permission:
        return Permission(
            id=model.id,
            code=model.code,
            description=model.description,
            created_at=self._as_utc(model.created_at),
        )

    async def find_by_id(self, permission_id: int) -> Permission | None:
        stmt = select(PermissionModel).where(PermissionModel.id == permission_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_code(self, code: str) -> Permission | None:
        stmt = select(PermissionModel).where(PermissionModel.code == code)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Permission]:
        stmt = select(PermissionModel).order_by(PermissionModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_role_id(self, role_id: int) -> list[Permission]:
        from app.infrastructure.database.models.role_model import RoleModel
        stmt = (
            select(PermissionModel)
            .join(PermissionModel.roles)
            .where(RoleModel.id == role_id)
            .order_by(PermissionModel.id)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, permission: Permission) -> Permission:
        model = PermissionModel(
            code=permission.code,
            description=permission.description,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, permission: Permission) -> Permission:
        stmt = select(PermissionModel).where(PermissionModel.id == permission.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Permission {permission.id} not found")
        model.code = permission.code
        model.description = permission.description
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, permission_id: int) -> None:
        stmt = select(PermissionModel).where(PermissionModel.id == permission_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
