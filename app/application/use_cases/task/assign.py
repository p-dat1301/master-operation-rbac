from app.application.dtos.task import AssignTaskInput, TaskOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class AssignTaskUseCase:
    """Use case gán task cho người khác — yêu cầu quyền assign_task."""

    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, data: AssignTaskInput) -> TaskOutput:
        try:
            self.rbac_service.require_permission(actor, "assign_task")
        except PermissionError:
            raise PermissionDenied("You do not have permission to assign tasks")

        task = await self.task_repo.find_by_id(data.task_id)
        if task is None:
            raise ResourceNotFound("Task not found")

        updated = await self.task_repo.assign_task(
            task_id=data.task_id,
            assignee_id=data.assignee_id,
            assigner_id=actor.id,
        )
        return TaskOutput.from_entity(updated)
