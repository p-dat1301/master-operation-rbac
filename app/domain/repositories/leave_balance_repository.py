from abc import ABC, abstractmethod

from app.domain.entities.leave_balance import LeaveBalance


class LeaveBalanceRepository(ABC):
    @abstractmethod
    async def find_by_id(self, balance_id: int) -> LeaveBalance | None:
        pass

    @abstractmethod
    async def find_by_user_year(self, user_id: int, year: int) -> LeaveBalance | None:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[LeaveBalance]:
        pass

    @abstractmethod
    async def create(self, balance: LeaveBalance) -> LeaveBalance:
        pass

    @abstractmethod
    async def update(self, balance: LeaveBalance) -> LeaveBalance:
        pass

    @abstractmethod
    async def upsert(self, balance: LeaveBalance) -> LeaveBalance:
        pass