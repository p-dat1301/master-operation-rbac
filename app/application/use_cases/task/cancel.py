from __future__ import annotations

from app.application.dtos.task import TaskOutput
from app.domain.entities.task import Task, TaskStatus
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class CancelTaskUseCase:
    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, task_id: int) -> TaskOutput:
        task = await self.task_repo.find_by_id(task_id)
        if task is None:
            raise ResourceNotFound("Task not found")
        if task.status in {TaskStatus.DONE, TaskStatus.CANCELLED}:
            raise BusinessRuleViolation(f"Task already {task.status.value}")
        if actor.id != task.assigner_id and not self.rbac_service.has_permission(actor, "manage_org"):
            raise PermissionDenied("You do not have permission to cancel this task")

        updated_task = Task(
            id=task.id,
            task_code=task.task_code,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assigner_id=task.assigner_id,
            department_id=task.department_id,
            status=TaskStatus.CANCELLED,
            priority=task.priority,
            start_date=task.start_date,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours,
            created_at=task.created_at,
        )
        result = await self.task_repo.update(updated_task)
        return TaskOutput.from_entity(result)