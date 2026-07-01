from abc import ABC, abstractmethod
from app.domain.entities.document import Document

class DocumentRepository(ABC):
    @abstractmethod
    async def create(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def find_by_id(self, document_id: int) -> Document | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Document]:
        pass

    @abstractmethod
    async def list_by_departments(self, dept_ids: list[int]) -> list[Document]:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_id: int) -> list[Document]:
        pass

    @abstractmethod
    async def search(self, keyword: str, dept_ids: list[int] | None = None) -> list[Document]:
        pass

    @abstractmethod
    async def update(self, document_id: int, data: dict) -> Document | None:
        pass

    @abstractmethod
    async def delete(self, document_id: int) -> Document | None:
        pass
