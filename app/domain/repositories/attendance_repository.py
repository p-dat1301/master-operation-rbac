from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.attendance import Attendance


class AttendanceRepository(ABC):
    @abstractmethod
    async def find_by_id(self, attendance_id: int) -> Attendance | None:
        pass

    @abstractmethod
    async def find_by_user_date(self, user_id: int, day: date) -> Attendance | None:
        pass

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[Attendance]:
        pass

    @abstractmethod
    async def list_by_departments(self, department_ids: set[int]) -> list[Attendance]:
        pass

    @abstractmethod
    async def list_by_date_range(self, start_date: date, end_date: date) -> list[Attendance]:
        pass

    @abstractmethod
    async def create(self, attendance: Attendance) -> Attendance:
        pass

    @abstractmethod
    async def update(self, attendance: Attendance) -> Attendance:
        pass

    @abstractmethod
    async def checkout(
        self,
        attendance_id: int,
        check_out: str | None,
        total_minutes: int | None,
    ) -> Attendance:
        pass