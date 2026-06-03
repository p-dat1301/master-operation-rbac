from app.application.dtos.task import TaskCreateInput, TaskOutput
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class CreateTaskUseCase:
    """Use case tạo task — yêu cầu quyền create_task."""

    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, data: TaskCreateInput) -> TaskOutput:
        try:
            self.rbac_service.require_permission(actor, "create_task")
        except PermissionError:
            raise PermissionDenied("You do not have permission to create tasks")

        task_entity = Task(
            id=0,
            task_code=data.task_code,
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
            assigner_id=actor.id,
            department_id=data.department_id,
            status="todo",
            priority=data.priority,
            start_date=data.start_date,
            due_date=data.due_date,
            estimated_hours=data.estimated_hours,
        )
        created = await self.task_repo.create(task_entity)
        return TaskOutput.from_entity(created)
