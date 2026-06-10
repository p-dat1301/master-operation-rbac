from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.permission import Permission
from app.domain.entities.role import Role
from app.domain.repositories.role_repository import RoleRepository
from app.infrastructure.database.models.permission_model import PermissionModel
from app.infrastructure.database.models.role_model import RoleModel


class SQLAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: RoleModel) -> Role:
        return Role(
            id=model.id,
            name=model.name,
            display_name=model.display_name,
            created_at=model.created_at,
        )

    async def find_by_id(self, role_id: int) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_name(self, name: str) -> Role | None:
        stmt = select(RoleModel).where(RoleModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Role]:
        stmt = select(RoleModel).order_by(RoleModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, role: Role) -> Role:
        model = RoleModel(
            name=role.name,
            display_name=role.display_name,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, role: Role) -> Role:
        stmt = select(RoleModel).where(RoleModel.id == role.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Role {role.id} not found")
        model.name = role.name
        model.display_name = role.display_name
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, role_id: int) -> None:
        stmt = select(RoleModel).where(RoleModel.id == role_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def list_permissions(self, role_id: int) -> list[Permission]:
        stmt = select(RoleModel).options(selectinload(RoleModel.permissions)).where(RoleModel.id == role_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            return []
        return [Permission(id=p.id, code=p.code, description=p.description, created_at=p.created_at) for p in model.permissions]

    async def add_permission(self, role_id: int, permission_id: int) -> None:
        role_stmt = select(RoleModel).options(selectinload(RoleModel.permissions)).where(RoleModel.id == role_id)
        role_result = await self._session.execute(role_stmt)
        role = role_result.scalars().first()
        if not role:
            return
        perm_stmt = select(PermissionModel).where(PermissionModel.id == permission_id)
        perm_result = await self._session.execute(perm_stmt)
        permission = perm_result.scalars().first()
        if not permission:
            return
        if permission not in role.permissions:
            role.permissions.append(permission)
            await self._session.flush()

    async def remove_permission(self, role_id: int, permission_id: int) -> None:
        role_stmt = select(RoleModel).options(selectinload(RoleModel.permissions)).where(RoleModel.id == role_id)
        role_result = await self._session.execute(role_stmt)
        role = role_result.scalars().first()
        if not role:
            return
        permission = next((p for p in role.permissions if p.id == permission_id), None)
        if permission is not None:
            role.permissions.remove(permission)
            await self._session.flush()
