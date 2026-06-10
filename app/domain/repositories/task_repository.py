from abc import ABC, abstractmethod

from app.domain.entities.task import Task


class TaskRepository(ABC):
    @abstractmethod
    async def find_by_id(self, task_id: int) -> Task | None:
        pass

    @abstractmethod
    async def find_by_task_code(self, task_code: str) -> Task | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Task]:
        pass

    @abstractmethod
    async def list_by_department(self, dept_id: int) -> list[Task]:
        pass

    @abstractmethod
    async def list_by_assignee(self, assignee_id: int) -> list[Task]:
        pass

    @abstractmethod
    async def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def assign_task(self, task_id: int, assignee_id: int, assigner_id: int) -> Task:
        pass

    @abstractmethod
    async def delete(self, task_id: int) -> None:
        pass