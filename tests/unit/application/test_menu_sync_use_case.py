import pytest

from app.application.use_cases.admin_config.menu_sync import MenuSyncUseCase, MenuSyncValidationError
from app.domain.entities.menu import Menu
from app.domain.entities.permission import Permission
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.rbac_service import RBACService


class FakeMenuRepository:
    def __init__(self, menus=None):
        self.menus = {menu.key: menu for menu in menus or []}

    async def find_by_key(self, key: str):
        return self.menus.get(key)

    async def find_by_route(self, route: str):
        return next((menu for menu in self.menus.values() if menu.route == route), None)

    async def find_all(self):
        return list(self.menus.values())

    async def create(self, menu: Menu):
        created = Menu(**{**menu.__dict__, "id": len(self.menus) + 1})
        self.menus[created.key] = created
        return created

    async def update(self, menu: Menu):
        self.menus[menu.key] = menu
        return menu


class FakePermissionRepository:
    def __init__(self, codes=None):
        self.codes = codes or {"system.config.manage"}

    async def find_by_id(self, permission_id: int):
        return None

    async def find_by_code(self, code: str):
        return Permission(id=1, code=code) if code in self.codes else None

    async def find_all(self):
        return [Permission(id=index + 1, code=code) for index, code in enumerate(self.codes)]

    async def find_by_role_id(self, role_id: int):
        return []

    async def create(self, permission: Permission):
        return permission

    async def update(self, permission: Permission):
        return permission

    async def delete(self, permission_id: int):
        return None


class FakeSeedLoader:
    def __init__(self, data):
        self.data = data

    async def load_menu(self):
        return self.data


class FailingSeedLoader:
    async def load_menu(self):
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


def seed_menu():
    return [
        {
            "key": "dashboard",
            "parent_key": None,
            "title_key": "menu.dashboard",
            "route": "/",
            "icon": "dashboard",
            "order": 1,
            "permission_key": None,
            "is_visible": True,
            "is_external": False,
        },
        {
            "key": "config",
            "parent_key": None,
            "title_key": "menu.config",
            "route": None,
            "icon": "setting",
            "order": 90,
            "permission_key": "system.config.manage",
            "is_visible": True,
            "is_external": False,
        },
    ]


def use_case(repo, data):
    return MenuSyncUseCase(
        menu_repo=repo,
        permission_repo=FakePermissionRepository(),
        seed_loader=FakeSeedLoader(data),
        rbac_service=RBACService(),
    )


@pytest.mark.asyncio
async def test_menu_sync_creates_then_skips_existing_rows():
    repo = FakeMenuRepository()
    sync = use_case(repo, seed_menu())

    first = await sync.execute(actor())
    second = await sync.execute(actor())

    assert first.created == 2
    assert first.updated == 0
    assert first.skipped == 0
    assert second.created == 0
    assert second.updated == 0
    assert second.skipped == 2
    assert len(repo.menus) == 2


@pytest.mark.asyncio
async def test_menu_sync_duplicate_key_returns_errors_without_write():
    repo = FakeMenuRepository()
    data = seed_menu() + [seed_menu()[0]]
    sync = use_case(repo, data)

    with pytest.raises(MenuSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["duplicate key: dashboard"]
    assert repo.menus == {}


@pytest.mark.asyncio
async def test_menu_sync_missing_parent_returns_errors_without_write():
    repo = FakeMenuRepository()
    data = seed_menu()
    data[1] = {**data[1], "parent_key": "missing"}
    sync = use_case(repo, data)

    with pytest.raises(MenuSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["missing parent reference: config -> missing"]
    assert repo.menus == {}


@pytest.mark.asyncio
async def test_menu_sync_dry_run_does_not_write():
    repo = FakeMenuRepository()
    sync = use_case(repo, seed_menu())

    result = await sync.execute(actor(), dry_run=True)

    assert result.created == 2
    assert result.dry_run is True
    assert repo.menus == {}


@pytest.mark.asyncio
async def test_menu_sync_malformed_json_returns_errors_without_write():
    repo = FakeMenuRepository()
    sync = MenuSyncUseCase(
        menu_repo=repo,
        permission_repo=FakePermissionRepository(),
        seed_loader=FailingSeedLoader(),
        rbac_service=RBACService(),
    )

    with pytest.raises(MenuSyncValidationError) as exc:
        await sync.execute(actor())

    assert exc.value.summary.errors == ["menu.json invalid: unexpected token at line 1"]
    assert repo.menus == {}


@pytest.mark.asyncio
async def test_menu_sync_requires_system_config_permission():
    repo = FakeMenuRepository()
    sync = use_case(repo, seed_menu())

    with pytest.raises(PermissionDenied):
        await sync.execute(actor(role_name="manager"))
