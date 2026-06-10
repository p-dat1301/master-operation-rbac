from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.admin_config.i18n_sync import I18nSyncUseCase
from app.domain.services.rbac_service import RBACService
from app.infrastructure.database.repositories.sqlalchemy_translation_repo import SQLAlchemyTranslationRepository
from app.infrastructure.database.seed_loaders.admin_config import AdminConfigSeedLoader


def provide_i18n_sync(db: AsyncSession) -> I18nSyncUseCase:
    return I18nSyncUseCase(
        translation_repo=SQLAlchemyTranslationRepository(db),
        seed_loader=AdminConfigSeedLoader(),
        rbac_service=RBACService(),
    )
