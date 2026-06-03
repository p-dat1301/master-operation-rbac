from abc import ABC, abstractmethod

from app.domain.entities.department import Department


class DepartmentRepository(ABC):
    @abstractmethod
    async def find_by_id(self, dept_id: int) -> Department | None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Department]:
        pass
