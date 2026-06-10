from __future__ import annotations

from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.rbac_service import RBACService


class DeleteTaskUseCase:
    def __init__(self, task_repo: TaskRepository, rbac_service: RBACService) -> None:
        self.task_repo = task_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, task_id: int) -> None:
        self.rbac_service.require_permission(actor, "manage_org")
        task = await self.task_repo.find_by_id(task_id)
        if task is None:
            raise ResourceNotFound("Task not found")
        await self.task_repo.delete(task_id)