from __future__ import annotations

from typing import Optional
from datetime import date

from pydantic import BaseModel

from app.application.dtos.user import UserOutput
from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.rbac_service import RBACService


class UpdateUserInput(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None


class UpdateUserUseCase:
    """Use case cập nhật user — yêu cầu manage_org."""

    def __init__(self, user_repo: UserRepository, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int, data: UpdateUserInput) -> UserOutput:
        self.rbac_service.require_permission(actor, "manage_org")

        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")

        # Apply partial updates
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone
        if data.job_title is not None:
            user.job_title = data.job_title
        if data.contact_type is not None:
            user.contact_type = data.contact_type
        if data.department_id is not None:
            user.department_id = data.department_id
        if data.manager_id is not None:
            user.manager_id = data.manager_id
        if data.is_active is not None:
            user.is_active = data.is_active

        updated = await self.user_repo.update(user)
        return UserOutput.from_entity(updated)
