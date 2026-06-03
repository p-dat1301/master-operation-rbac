from app.application.dtos.task import TaskOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class ListTasksUseCase:
    """Use case liệt kê task theo scope của actor."""

    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User) -> list[TaskOutput]:
        scope = self.rbac_service.get_task_scope(actor)

        if scope == "all":
            tasks = await self.task_repo.list_all()
        elif scope == "department" and actor.department_id is not None:
            tasks = await self.task_repo.list_by_department(actor.department_id)
        else:
            tasks = await self.task_repo.list_by_assignee(actor.id)

        return [TaskOutput.from_entity(t) for t in tasks]
