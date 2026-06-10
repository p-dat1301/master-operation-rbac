from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.department.list_departments import ListDepartmentsUseCase


def provide_list_departments(db: AsyncSession) -> ListDepartmentsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    dept_repo = SQLAlchemyDepartmentRepository(db)
    return ListDepartmentsUseCase(dept_repo=dept_repo)
