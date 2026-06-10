from __future__ import annotations

from app.application.dtos.menu_sync import MenuSyncSummary
from app.domain.entities.menu import Menu
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.menu_repository import MenuRepository
from app.domain.repositories.permission_repository import PermissionRepository
from app.domain.services.rbac_service import RBACService


class MenuSyncValidationError(BusinessRuleViolation):
    def __init__(self, summary: MenuSyncSummary) -> None:
        super().__init__("Menu sync validation failed")
        self.summary = summary


class MenuSyncUseCase:
    def __init__(
        self,
        menu_repo: MenuRepository,
        permission_repo: PermissionRepository,
        seed_loader,
        rbac_service: RBACService,
    ) -> None:
        self.menu_repo = menu_repo
        self.permission_repo = permission_repo
        self.seed_loader = seed_loader
        self.rbac_service = rbac_service

    async def execute(self, actor: User, dry_run: bool = False) -> MenuSyncSummary:
        self.rbac_service.require_permission(actor, "system.config.manage")
        try:
            raw_items = await self.seed_loader.load_menu()
        except (OSError, TypeError, ValueError) as exc:
            summary = MenuSyncSummary(resource="menu", created=0, updated=0, skipped=0, errors=[f"menu.json invalid: {exc}"], dry_run=dry_run)
            raise MenuSyncValidationError(summary) from exc
        summary = await self._sync(raw_items, dry_run=dry_run)
        if summary.errors:
            raise MenuSyncValidationError(summary)
        return summary

    async def _sync(self, raw_items, dry_run: bool) -> MenuSyncSummary:
        errors: list[str] = []
        if not isinstance(raw_items, list):
            return MenuSyncSummary(resource="menu", created=0, updated=0, skipped=0, errors=["menu.json must be an array"], dry_run=dry_run)

        normalized_items: list[dict] = []
        seen_keys: set[str] = set()
        seen_routes: set[str] = set()

        for index, item in enumerate(raw_items):
            if not isinstance(item, dict):
                errors.append(f"item[{index}] must be an object")
                continue
            missing = [field for field in ["key", "parent_key", "title_key", "route", "icon", "order", "permission_key", "is_visible", "is_external"] if field not in item]
            if missing:
                errors.append(f"item[{index}] missing required fields: {', '.join(missing)}")
                continue
            key = item["key"]
            if not isinstance(key, str) or not key.strip():
                errors.append(f"item[{index}] key must be a non-empty string")
                continue
            if key in seen_keys:
                errors.append(f"duplicate key: {key}")
                continue
            route = item["route"]
            if route is not None and (not isinstance(route, str) or not route.strip()):
                errors.append(f"item[{index}] route must be a string or null")
                continue
            if route is not None and route in seen_routes:
                errors.append(f"duplicate route: {route}")
                continue
            parent_key = item["parent_key"]
            if parent_key is not None and (not isinstance(parent_key, str) or not parent_key.strip()):
                errors.append(f"item[{index}] parent_key must be a string or null")
                continue
            if parent_key == key:
                errors.append(f"item[{index}] parent_key cannot equal key: {key}")
                continue
            permission_key = item["permission_key"]
            if permission_key is not None and (not isinstance(permission_key, str) or not permission_key.strip()):
                errors.append(f"item[{index}] permission_key must be a string or null")
                continue
            if not isinstance(item["title_key"], str) or not item["title_key"].strip():
                errors.append(f"item[{index}] title_key must be a non-empty string")
                continue
            if not isinstance(item["order"], int) or isinstance(item["order"], bool):
                errors.append(f"item[{index}] order must be an integer")
                continue
            if not isinstance(item["is_visible"], bool):
                errors.append(f"item[{index}] is_visible must be a boolean")
                continue
            if not isinstance(item["is_external"], bool):
                errors.append(f"item[{index}] is_external must be a boolean")
                continue
            normalized_items.append(item)
            seen_keys.add(key)
            if route is not None:
                seen_routes.add(route)

        if errors:
            return MenuSyncSummary(resource="menu", created=0, updated=0, skipped=0, errors=errors, dry_run=dry_run)

        seed_keys = {item["key"] for item in normalized_items}
        for item in normalized_items:
            parent_key = item["parent_key"]
            if parent_key is not None and parent_key not in seed_keys:
                errors.append(f"missing parent reference: {item['key']} -> {parent_key}")

        existing_permissions = await self._fetch_existing_permissions()
        for item in normalized_items:
            permission_key = item["permission_key"]
            if permission_key is not None and permission_key not in existing_permissions:
                errors.append(f"missing permission_key: {permission_key}")

        existing_menus = await self.menu_repo.find_all()
        existing_by_key = {menu.key: menu for menu in existing_menus}
        existing_by_route = {menu.route: menu for menu in existing_menus if menu.route is not None}

        for item in normalized_items:
            route = item["route"]
            if route is not None:
                existing = existing_by_route.get(route)
                if existing is not None and existing.key != item["key"]:
                    errors.append(f"duplicate route in database: {route}")

        if errors:
            return MenuSyncSummary(resource="menu", created=0, updated=0, skipped=0, errors=errors, dry_run=dry_run)

        created = 0
        updated = 0
        skipped = 0

        for item in sorted(normalized_items, key=lambda row: row["order"]):
            current = existing_by_key.get(item["key"])
            payload = Menu(
                id=current.id if current else 0,
                key=item["key"],
                parent_key=item["parent_key"],
                title_key=item["title_key"],
                route=item["route"],
                icon=item["icon"],
                order=item["order"],
                permission_key=item["permission_key"],
                is_visible=item["is_visible"],
                is_external=item["is_external"],
                created_at=current.created_at if current else None,
                updated_at=current.updated_at if current else None,
            )
            if current is None:
                created += 1
                if not dry_run:
                    await self.menu_repo.create(payload)
                continue
            if self._same_menu(current, payload):
                skipped += 1
                continue
            updated += 1
            if not dry_run:
                await self.menu_repo.update(payload)

        seed_key_set = {item["key"] for item in normalized_items}
        for key in existing_by_key:
            if key not in seed_key_set:
                skipped += 1

        return MenuSyncSummary(resource="menu", created=created, updated=updated, skipped=skipped, errors=[], dry_run=dry_run)

    async def _fetch_existing_permissions(self) -> set[str]:
        permissions = await self.permission_repo.find_all()
        return {permission.code for permission in permissions}

    def _same_menu(self, current: Menu, payload: Menu) -> bool:
        return (
            current.key == payload.key
            and current.parent_key == payload.parent_key
            and current.title_key == payload.title_key
            and current.route == payload.route
            and current.icon == payload.icon
            and current.order == payload.order
            and current.permission_key == payload.permission_key
            and current.is_visible == payload.is_visible
            and current.is_external == payload.is_external
        )
