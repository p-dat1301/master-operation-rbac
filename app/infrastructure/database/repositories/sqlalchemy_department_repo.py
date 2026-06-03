from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.department import Department
from app.domain.repositories.department_repository import DepartmentRepository
from app.infrastructure.database.models.department_model import DepartmentModel


class SQLAlchemyDepartmentRepository(DepartmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: DepartmentModel) -> Department:
        return Department(
            id=model.id,
            name=model.name,
            level=model.level,
            parent_id=model.parent_id,
        )

    async def find_by_id(self, dept_id: int) -> Department | None:
        stmt = select(DepartmentModel).where(DepartmentModel.id == dept_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Department]:
        stmt = select(DepartmentModel).order_by(DepartmentModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
