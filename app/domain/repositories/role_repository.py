from abc import ABC, abstractmethod

from app.domain.entities.role import Role


class RoleRepository(ABC):
    @abstractmethod
    async def find_by_id(self, role_id: int) -> Role | None:
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Role | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Role]:
        pass

    @abstractmethod
    async def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    async def update(self, role: Role) -> Role:
        pass

    @abstractmethod
    async def delete(self, role_id: int) -> None:
        pass