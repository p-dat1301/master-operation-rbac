from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.role.crud import (
    AddPermissionToRoleUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    ListRolesUseCase,
    ListRolePermissionsUseCase,
    RemovePermissionFromRoleUseCase,
    UpdateRoleUseCase,
)
from app.domain.services.rbac_service import RBACService


def provide_list_roles(db: AsyncSession) -> ListRolesUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return ListRolesUseCase(role_repo=SQLAlchemyRoleRepository(db))


def provide_create_role(db: AsyncSession) -> CreateRoleUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return CreateRoleUseCase(role_repo=SQLAlchemyRoleRepository(db), rbac_service=RBACService())


def provide_update_role(db: AsyncSession) -> UpdateRoleUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return UpdateRoleUseCase(role_repo=SQLAlchemyRoleRepository(db), rbac_service=RBACService())


def provide_delete_role(db: AsyncSession) -> DeleteRoleUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return DeleteRoleUseCase(role_repo=SQLAlchemyRoleRepository(db), rbac_service=RBACService())


def provide_list_role_permissions(db: AsyncSession) -> ListRolePermissionsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return ListRolePermissionsUseCase(role_repo=SQLAlchemyRoleRepository(db), rbac_service=RBACService())


def provide_add_permission_to_role(db: AsyncSession) -> AddPermissionToRoleUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return AddPermissionToRoleUseCase(
        role_repo=SQLAlchemyRoleRepository(db),
        permission_repo=SQLAlchemyPermissionRepository(db),
        rbac_service=RBACService(),
    )


def provide_remove_permission_from_role(db: AsyncSession) -> RemovePermissionFromRoleUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    return RemovePermissionFromRoleUseCase(
        role_repo=SQLAlchemyRoleRepository(db),
        permission_repo=SQLAlchemyPermissionRepository(db),
        rbac_service=RBACService(),
    )
