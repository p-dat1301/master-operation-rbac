from app.application.dtos.task import CompleteTaskInput, TaskOutput
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService
from app.domain.entities.task import Task


class CompleteTaskUseCase:
    """Use case đánh dấu task hoàn thành — yêu cầu quyền complete_task hoặc là assigner/admin/bod."""

    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, data: CompleteTaskInput) -> TaskOutput:
        task = await self.task_repo.find_by_id(data.task_id)
        if task is None:
            raise ResourceNotFound("Task not found")

        is_assigner = task.assigner_id == actor.id
        has_permission = self.rbac_service.has_permission(actor, "complete_task")
        is_admin_bod = actor.role_name in ("admin", "bod")

        if not (is_assigner or has_permission or is_admin_bod):
            raise PermissionDenied("You do not have permission to complete this task")

        if task.status in ("done", "cancelled"):
            raise BusinessRuleViolation(f"Task already {task.status}")

        updated_task = Task(
            id=task.id,
            task_code=task.task_code,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assigner_id=task.assigner_id,
            department_id=task.department_id,
            status="done",
            priority=task.priority,
            start_date=task.start_date,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours,
            created_at=task.created_at,
        )

        result = await self.task_repo.update(updated_task)
        return TaskOutput.from_entity(result)
