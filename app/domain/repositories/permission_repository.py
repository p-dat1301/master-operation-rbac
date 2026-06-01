from abc import ABC, abstractmethod

from app.domain.entities.permission import Permission


class PermissionRepository(ABC):
    @abstractmethod
    async def find_by_id(self, permission_id: int) -> Permission | None:
        pass

    @abstractmethod
    async def find_by_code(self, code: str) -> Permission | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Permission]:
        pass