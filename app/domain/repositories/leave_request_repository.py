from abc import ABC, abstractmethod

from app.domain.entities.leave_request import LeaveRequest


class LeaveRequestRepository(ABC):
    @abstractmethod
    async def find_by_id(self, leave_id: int) -> LeaveRequest | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[LeaveRequest]:
        pass

    @abstractmethod
    async def list_by_requester(self, requester_id: int) -> list[LeaveRequest]:
        pass

    @abstractmethod
    async def list_by_reviewer(self, reviewer_id: int) -> list[LeaveRequest]:
        pass

    @abstractmethod
    async def list_by_status(self, status: str) -> list[LeaveRequest]:
        pass

    @abstractmethod
    async def create(self, leave: LeaveRequest) -> LeaveRequest:
        pass

    @abstractmethod
    async def update(self, leave: LeaveRequest) -> LeaveRequest:
        pass

    @abstractmethod
    async def update_status(
        self,
        leave_id: int,
        status: str,
        reviewed_by: int | None,
        rejection_reason: str | None = None,
    ) -> LeaveRequest:
        pass