import json

import pytest

from app.application.use_cases.admin_config.i18n_sync import I18nSyncUseCase, I18nSyncValidationError
from app.application.use_cases.admin_config.menu_sync import MenuSyncUseCase, MenuSyncValidationError
from app.domain.entities.permission import Permission
from app.domain.entities.user import User
from app.domain.services.rbac_service import RBACService
from app.infrastructure.database.seed_loaders.admin_config import AdminConfigSeedLoader


class FakeMenuRepository:
    async def find_all(self):
        return []

    async def create(self, menu):
        return menu

    async def update(self, menu):
        return menu


class FakeTranslationRepository:
    async def find_all(self):
        return []

    async def create(self, translation):
        return translation

    async def update(self, translation):
        return translation


class FakePermissionRepository:
    async def find_all(self):
        return [Permission(id=1, code='system.config.manage')]


def actor() -> User:
    return User(
        id=1,
        employee_code='EMP001',
        email='admin@company.vn',
        full_name='Admin User',
        role_name='admin',
        permissions={'system.config.manage'},
    )


@pytest.mark.asyncio
async def test_menu_sync_uses_sync_seed_dir_override_for_invalid_json(tmp_path, monkeypatch):
    seed_dir = tmp_path / 'admin_config'
    seed_dir.mkdir()
    (seed_dir / 'menu.json').write_text('{broken json', encoding='utf-8')
    monkeypatch.setenv('SYNC_SEED_DIR', str(seed_dir))

    sync = MenuSyncUseCase(
        menu_repo=FakeMenuRepository(),
        permission_repo=FakePermissionRepository(),
        seed_loader=AdminConfigSeedLoader(),
        rbac_service=RBACService(),
    )

    with pytest.raises(MenuSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors
    assert exc.value.summary.errors[0].startswith('menu.json invalid:')


@pytest.mark.asyncio
async def test_i18n_sync_uses_sync_seed_dir_override_for_missing_locale_key(tmp_path, monkeypatch):
    seed_dir = tmp_path / 'admin_config'
    seed_dir.mkdir()
    (seed_dir / 'vi.json').write_text(
        json.dumps(
            [
                {"locale": "vi", "key": "menu.dashboard", "value": "Tổng quan", "namespace": "menu"},
                {"locale": "vi", "key": "menu.config", "value": "Cấu hình", "namespace": "menu"},
            ]
        ),
        encoding='utf-8',
    )
    (seed_dir / 'en.json').write_text(
        json.dumps(
            [
                {"locale": "en", "key": "menu.dashboard", "value": "Dashboard", "namespace": "menu"}
            ]
        ),
        encoding='utf-8',
    )
    monkeypatch.setenv('SYNC_SEED_DIR', str(seed_dir))

    sync = I18nSyncUseCase(
        translation_repo=FakeTranslationRepository(),
        seed_loader=AdminConfigSeedLoader(),
        rbac_service=RBACService(),
    )

    with pytest.raises(I18nSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ['missing locale key: en.menu.config']
