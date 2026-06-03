"""SQLAlchemy 2.0 async implementation của TaskRepository."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.task import Task
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.database.models.task_model import TaskModel


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            task_code=model.task_code,
            title=model.title,
            description=model.description,
            assignee_id=model.assignee_id,
            assigner_id=model.creator_id,
            department_id=model.department_id,
            status=model.status,
            priority=model.priority,
            due_date=model.due_date,
            created_at=model.created_at,
        )

    async def find_by_id(self, task_id: int) -> Task | None:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_task_code(self, task_code: str) -> Task | None:
        stmt = select(TaskModel).where(TaskModel.task_code == task_code)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[Task]:
        stmt = select(TaskModel).order_by(TaskModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_department(self, dept_id: int) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.department_id == dept_id).order_by(TaskModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_assignee(self, assignee_id: int) -> list[Task]:
        stmt = select(TaskModel).where(TaskModel.assignee_id == assignee_id).order_by(TaskModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, task: Task) -> Task:
        model = TaskModel(
            task_code=task.task_code,
            title=task.title,
            description=task.description,
            creator_id=task.assigner_id,
            assignee_id=task.assignee_id,
            department_id=task.department_id,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, task: Task) -> Task:
        stmt = select(TaskModel).where(TaskModel.id == task.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Task {task.id} not found")
        model.title = task.title
        model.description = task.description
        model.assignee_id = task.assignee_id
        model.department_id = task.department_id
        model.status = task.status
        model.priority = task.priority
        model.due_date = task.due_date
        await self._session.flush()
        return self._to_entity(model)

    async def assign_task(self, task_id: int, assignee_id: int, assigner_id: int) -> Task:
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Task {task_id} not found")
        model.assignee_id = assignee_id
        model.creator_id = assigner_id
        await self._session.flush()
        return self._to_entity(model)
