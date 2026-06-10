from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.permission.crud import (
    CreatePermissionUseCase,
    DeletePermissionUseCase,
    ListPermissionsUseCase,
    UpdatePermissionUseCase,
)
from app.domain.services.rbac_service import RBACService


def provide_list_permissions(db: AsyncSession) -> ListPermissionsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    return ListPermissionsUseCase(perm_repo=SQLAlchemyPermissionRepository(db))


def provide_create_permission(db: AsyncSession) -> CreatePermissionUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    return CreatePermissionUseCase(perm_repo=SQLAlchemyPermissionRepository(db), rbac_service=RBACService())


def provide_update_permission(db: AsyncSession) -> UpdatePermissionUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    return UpdatePermissionUseCase(perm_repo=SQLAlchemyPermissionRepository(db), rbac_service=RBACService())


def provide_delete_permission(db: AsyncSession) -> DeletePermissionUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
    return DeletePermissionUseCase(perm_repo=SQLAlchemyPermissionRepository(db), rbac_service=RBACService())
