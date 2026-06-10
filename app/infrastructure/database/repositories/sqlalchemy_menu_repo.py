from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.menu import Menu
from app.domain.repositories.menu_repository import MenuRepository
from app.infrastructure.database.models.menu_model import MenuModel


class SQLAlchemyMenuRepository(MenuRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: MenuModel) -> Menu:
        return Menu(
            id=model.id,
            key=model.key,
            parent_key=model.parent_key,
            title_key=model.title_key,
            route=model.route,
            icon=model.icon,
            order=model.order,
            permission_key=model.permission_key,
            is_visible=model.is_visible,
            is_external=model.is_external,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def find_by_key(self, key: str) -> Menu | None:
        stmt = select(MenuModel).where(MenuModel.key == key)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_route(self, route: str) -> Menu | None:
        stmt = select(MenuModel).where(MenuModel.route == route)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[Menu]:
        stmt = select(MenuModel).order_by(MenuModel.order, MenuModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def create(self, menu: Menu) -> Menu:
        model = MenuModel(
            key=menu.key,
            parent_key=menu.parent_key,
            title_key=menu.title_key,
            route=menu.route,
            icon=menu.icon,
            order=menu.order,
            permission_key=menu.permission_key,
            is_visible=menu.is_visible,
            is_external=menu.is_external,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, menu: Menu) -> Menu:
        stmt = select(MenuModel).where(MenuModel.id == menu.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model is None:
            raise ValueError(f"Menu {menu.id} not found")
        model.key = menu.key
        model.parent_key = menu.parent_key
        model.title_key = menu.title_key
        model.route = menu.route
        model.icon = menu.icon
        model.order = menu.order
        model.permission_key = menu.permission_key
        model.is_visible = menu.is_visible
        model.is_external = menu.is_external
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)
