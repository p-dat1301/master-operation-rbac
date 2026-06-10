from app.application.dtos.permission import PermissionOutput
from app.domain.entities.permission import Permission
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, ResourceNotFound
from app.domain.repositories.permission_repository import PermissionRepository
from app.domain.services.rbac_service import RBACService


class ListPermissionsUseCase:
    def __init__(self, perm_repo: PermissionRepository) -> None:
        self.perm_repo = perm_repo

    async def execute(self) -> list[PermissionOutput]:
        perms = await self.perm_repo.find_all()
        return [PermissionOutput.from_entity(p) for p in perms]


class CreatePermissionUseCase:
    def __init__(self, perm_repo: PermissionRepository, rbac_service: RBACService) -> None:
        self.perm_repo = perm_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, code: str, description: str | None = None) -> PermissionOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        existing = await self.perm_repo.find_by_code(code)
        if existing is not None:
            raise BusinessRuleViolation(f"Permission '{code}' already exists")
        perm = Permission(id=0, code=code, description=description)
        created = await self.perm_repo.create(perm)
        return PermissionOutput.from_entity(created)


class UpdatePermissionUseCase:
    def __init__(self, perm_repo: PermissionRepository, rbac_service: RBACService) -> None:
        self.perm_repo = perm_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, perm_id: int, code: str, description: str | None = None) -> PermissionOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        perm = await self.perm_repo.find_by_id(perm_id)
        if perm is None:
            raise ResourceNotFound(f"Permission {perm_id} not found")
        updated_perm = Permission(id=perm_id, code=code, description=description)
        updated = await self.perm_repo.update(updated_perm)
        return PermissionOutput.from_entity(updated)


class DeletePermissionUseCase:
    def __init__(self, perm_repo: PermissionRepository, rbac_service: RBACService) -> None:
        self.perm_repo = perm_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, perm_id: int) -> None:
        self.rbac_service.require_permission(actor, "manage_org")
        perm = await self.perm_repo.find_by_id(perm_id)
        if perm is None:
            raise ResourceNotFound(f"Permission {perm_id} not found")
        await self.perm_repo.delete(perm_id)
