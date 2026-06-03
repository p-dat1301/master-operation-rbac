from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.role import Role
from app.domain.repositories.role_repository import RoleRepository
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
