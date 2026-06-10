from app.application.dtos.task import TaskOutput
from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class GetTaskUseCase:
    """Use case lấy chi tiết task theo ID."""

    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, task_id: int) -> TaskOutput:
        task = await self.task_repo.find_by_id(task_id)
        if task is None:
            raise ResourceNotFound(f"Task {task_id} not found")

        # Check scope
        scope = self.rbac_service.get_task_scope(actor)
        if scope == "self" and task.assignee_id != actor.id and task.assigner_id != actor.id:
            from app.domain.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to view this task")

        return TaskOutput.from_entity(task)
