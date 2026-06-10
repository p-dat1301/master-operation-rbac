import pytest

from app.application.use_cases.admin_config.i18n_sync import I18nSyncUseCase, I18nSyncValidationError
from app.domain.entities.translation import Translation
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.rbac_service import RBACService


class FakeTranslationRepository:
    def __init__(self, translations=None):
        self.translations = {(translation.locale, translation.key): translation for translation in translations or []}

    async def find_by_locale_key(self, locale: str, key: str):
        return self.translations.get((locale, key))

    async def find_all(self):
        return list(self.translations.values())

    async def create(self, translation: Translation):
        created = Translation(**{**translation.__dict__, "id": len(self.translations) + 1})
        self.translations[(created.locale, created.key)] = created
        return created

    async def update(self, translation: Translation):
        self.translations[(translation.locale, translation.key)] = translation
        return translation


class FakeSeedLoader:
    def __init__(self, data):
        self.data = data

    async def load_i18n(self):
        return self.data


class FailingSeedLoader:
    async def load_i18n(self):
        raise ValueError("unexpected token at line 1")


def actor(role_name="admin", permissions=None):
    return User(
        id=1,
        employee_code="EMP001",
        email="admin@company.vn",
        full_name="Admin User",
        role_name=role_name,
        permissions=permissions or set(),
    )


def seed_i18n():
    return {
        "vi": [
            {"locale": "vi", "key": "menu.dashboard", "value": "Tổng quan", "namespace": "menu"},
            {"locale": "vi", "key": "menu.config", "value": "Cấu hình", "namespace": "menu"},
        ],
        "en": [
            {"locale": "en", "key": "menu.dashboard", "value": "Dashboard", "namespace": "menu"},
            {"locale": "en", "key": "menu.config", "value": "Configuration", "namespace": "menu"},
        ],
    }


def use_case(repo, data):
    return I18nSyncUseCase(
        translation_repo=repo,
        seed_loader=FakeSeedLoader(data),
        rbac_service=RBACService(),
    )


@pytest.mark.asyncio
async def test_i18n_sync_creates_then_skips_existing_rows():
    repo = FakeTranslationRepository()
    sync = use_case(repo, seed_i18n())

    first = await sync.execute(actor())
    second = await sync.execute(actor())

    assert first.resource == "i18n"
    assert first.created == 4
    assert first.updated == 0
    assert first.skipped == 0
    assert second.created == 0
    assert second.updated == 0
    assert second.skipped == 4
    assert len(repo.translations) == 4


@pytest.mark.asyncio
async def test_i18n_sync_missing_locale_key_returns_errors_without_write():
    repo = FakeTranslationRepository()
    data = seed_i18n()
    data["en"] = data["en"][:1]
    sync = use_case(repo, data)

    with pytest.raises(I18nSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["missing locale key: en.menu.config"]
    assert repo.translations == {}


@pytest.mark.asyncio
async def test_i18n_sync_duplicate_locale_key_returns_errors_without_write():
    repo = FakeTranslationRepository()
    data = seed_i18n()
    data["vi"] = data["vi"] + [data["vi"][0]]
    sync = use_case(repo, data)

    with pytest.raises(I18nSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["duplicate locale key: vi.menu.dashboard"]
    assert repo.translations == {}


@pytest.mark.asyncio
async def test_i18n_sync_dry_run_does_not_write():
    repo = FakeTranslationRepository()
    sync = use_case(repo, seed_i18n())

    result = await sync.execute(actor(), dry_run=True)

    assert result.created == 4
    assert result.dry_run is True
    assert repo.translations == {}


@pytest.mark.asyncio
async def test_i18n_sync_malformed_json_returns_errors_without_write():
    repo = FakeTranslationRepository()
    sync = I18nSyncUseCase(
        translation_repo=repo,
        seed_loader=FailingSeedLoader(),
        rbac_service=RBACService(),
    )

    with pytest.raises(I18nSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["i18n seed invalid: unexpected token at line 1"]
    assert repo.translations == {}


@pytest.mark.asyncio
async def test_i18n_sync_requires_system_config_permission():
    repo = FakeTranslationRepository()
    sync = use_case(repo, seed_i18n())

    with pytest.raises(PermissionDenied):
        await sync.execute(actor(role_name="manager"))
