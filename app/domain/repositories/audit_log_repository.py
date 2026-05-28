from abc import ABC, abstractmethod

from app.domain.entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    async def find_by_id(self, log_id: int) -> AuditLog | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[AuditLog]:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[AuditLog]:
        pass

    @abstractmethod
    async def list_by_resource(self, resource: str, resource_id: int) -> list[AuditLog]:
        pass

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> list[AuditLog]:
        pass

    @abstractmethod
    async def create(self, log: AuditLog) -> AuditLog:
        pass