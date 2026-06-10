from __future__ import annotations

from pydantic import BaseModel

from app.application.dtos.user import UserOutput
from app.application.ports.password import IPasswordService
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.rbac_service import RBACService


class ChangePasswordInput(BaseModel):
    current_password: str
    new_password: str


class ResetPasswordInput(BaseModel):
    new_password: str


class ActivateUserUseCase:
    def __init__(self, user_repo: UserRepository, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int) -> UserOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")
        user.is_active = True
        updated = await self.user_repo.update(user)
        return UserOutput.from_entity(updated)


class DeactivateUserUseCase:
    def __init__(self, user_repo: UserRepository, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int) -> UserOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")
        user.is_active = False
        updated = await self.user_repo.update(user)
        return UserOutput.from_entity(updated)


class ChangePasswordUseCase:
    def __init__(self, user_repo: UserRepository, password_service: IPasswordService) -> None:
        self.user_repo = user_repo
        self.password_service = password_service

    async def execute(self, actor: User, user_id: int, data: ChangePasswordInput) -> UserOutput:
        if actor.id != user_id:
            raise PermissionDenied("You can only change your own password")
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")
        if user.hashed_password is None or not self.password_service.verify(data.current_password, user.hashed_password):
            raise PermissionDenied("Invalid current password")
        user.hashed_password = self.password_service.hash(data.new_password)
        updated = await self.user_repo.update(user)
        return UserOutput.from_entity(updated)


class ResetPasswordUseCase:
    def __init__(self, user_repo: UserRepository, password_service: IPasswordService, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.password_service = password_service
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int, data: ResetPasswordInput) -> UserOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")
        user.hashed_password = self.password_service.hash(data.new_password)
        updated = await self.user_repo.update(user)
        return UserOutput.from_entity(updated)