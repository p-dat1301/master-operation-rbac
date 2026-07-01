from __future__ import annotations

from app.application.dtos.task import TaskOutput, TaskUpdateInput
from app.domain.entities.task import Task, TaskPriority, TaskStatus
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class UpdateTaskUseCase:
    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, task_id: int, data: TaskUpdateInput) -> TaskOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        task = await self.task_repo.find_by_id(task_id)
        if task is None:
            raise ResourceNotFound("Task not found")
        if task.status in {TaskStatus.DONE, TaskStatus.CANCELLED}:
            raise BusinessRuleViolation("Task cannot be updated in its current state")

        updated_task = Task(
            id=task.id,
            task_code=task.task_code,
            title=data.title if data.title is not None else task.title,
            description=data.description if data.description is not None else task.description,
            assignee_id=data.assignee_id if data.assignee_id is not None else task.assignee_id,
            assigner_id=task.assigner_id,
            department_id=data.department_id if data.department_id is not None else task.department_id,
            status=task.status,
            priority=TaskPriority(data.priority) if data.priority is not None else task.priority,
            start_date=data.start_date if data.start_date is not None else task.start_date,
            due_date=data.due_date if data.due_date is not None else task.due_date,
            estimated_hours=data.estimated_hours if data.estimated_hours is not None else task.estimated_hours,
            created_at=task.created_at,
        )
        result = await self.task_repo.update(updated_task)
        return TaskOutput.from_entity(result)