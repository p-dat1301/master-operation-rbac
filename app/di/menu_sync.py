from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.admin_config.menu_sync import MenuSyncUseCase
from app.domain.services.rbac_service import RBACService
from app.infrastructure.database.repositories.sqlalchemy_menu_repo import SQLAlchemyMenuRepository
from app.infrastructure.database.repositories.sqlalchemy_permission_repo import SQLAlchemyPermissionRepository
from app.infrastructure.database.seed_loaders.admin_config import AdminConfigSeedLoader


def provide_menu_sync(db: AsyncSession) -> MenuSyncUseCase:
    return MenuSyncUseCase(
        menu_repo=SQLAlchemyMenuRepository(db),
        permission_repo=SQLAlchemyPermissionRepository(db),
        seed_loader=AdminConfigSeedLoader(),
        rbac_service=RBACService(),
    )
