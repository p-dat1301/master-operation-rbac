from abc import ABC, abstractmethod

from app.domain.entities.menu import Menu


class MenuRepository(ABC):
    @abstractmethod
    async def find_by_key(self, key: str) -> Menu | None:
        pass

    @abstractmethod
    async def find_by_route(self, route: str) -> Menu | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Menu]:
        pass

    @abstractmethod
    async def create(self, menu: Menu) -> Menu:
        pass

    @abstractmethod
    async def update(self, menu: Menu) -> Menu:
        pass
