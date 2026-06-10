from app.application.dtos.role import RoleOutput
from app.application.dtos.permission import PermissionOutput
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, ResourceNotFound
from app.domain.repositories.permission_repository import PermissionRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.services.rbac_service import RBACService


class ListRolesUseCase:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    async def execute(self) -> list[RoleOutput]:
        roles = await self.role_repo.find_all()
        return [RoleOutput.from_entity(r) for r in roles]


class CreateRoleUseCase:
    def __init__(self, role_repo: RoleRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, name: str, display_name: str) -> RoleOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        existing = await self.role_repo.find_by_name(name)
        if existing is not None:
            raise BusinessRuleViolation(f"Role '{name}' already exists")
        role = Role(id=0, name=name, display_name=display_name)
        created = await self.role_repo.create(role)
        return RoleOutput.from_entity(created)


class UpdateRoleUseCase:
    def __init__(self, role_repo: RoleRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, role_id: int, name: str, display_name: str) -> RoleOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        role = await self.role_repo.find_by_id(role_id)
        if role is None:
            raise ResourceNotFound(f"Role {role_id} not found")
        updated_role = Role(id=role_id, name=name, display_name=display_name)
        updated = await self.role_repo.update(updated_role)
        return RoleOutput.from_entity(updated)


class DeleteRoleUseCase:
    def __init__(self, role_repo: RoleRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, role_id: int) -> None:
        self.rbac_service.require_permission(actor, "manage_org")
        role = await self.role_repo.find_by_id(role_id)
        if role is None:
            raise ResourceNotFound(f"Role {role_id} not found")
        await self.role_repo.delete(role_id)


class ListRolePermissionsUseCase:
    def __init__(self, role_repo: RoleRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, role_id: int) -> list[PermissionOutput]:
        self.rbac_service.require_permission(actor, "manage_org")
        permissions = await self.role_repo.list_permissions(role_id)
        return [PermissionOutput.from_entity(permission) for permission in permissions]


class AddPermissionToRoleUseCase:
    def __init__(self, role_repo: RoleRepository, permission_repo: PermissionRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, role_id: int, permission_id: int) -> list[PermissionOutput]:
        self.rbac_service.require_permission(actor, "manage_org")
        role = await self.role_repo.find_by_id(role_id)
        if role is None:
            raise ResourceNotFound(f"Role {role_id} not found")
        permission = await self.permission_repo.find_by_id(permission_id)
        if permission is None:
            raise ResourceNotFound(f"Permission {permission_id} not found")
        await self.role_repo.add_permission(role_id, permission_id)
        return [PermissionOutput.from_entity(p) for p in await self.role_repo.list_permissions(role_id)]


class RemovePermissionFromRoleUseCase:
    def __init__(self, role_repo: RoleRepository, permission_repo: PermissionRepository, rbac_service: RBACService) -> None:
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, role_id: int, permission_id: int) -> list[PermissionOutput]:
        self.rbac_service.require_permission(actor, "manage_org")
        role = await self.role_repo.find_by_id(role_id)
        if role is None:
            raise ResourceNotFound(f"Role {role_id} not found")
        permission = await self.permission_repo.find_by_id(permission_id)
        if permission is None:
            raise ResourceNotFound(f"Permission {permission_id} not found")
        await self.role_repo.remove_permission(role_id, permission_id)
        return [PermissionOutput.from_entity(p) for p in await self.role_repo.list_permissions(role_id)]
