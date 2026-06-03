from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.attendance import Attendance


class AttendanceOutput(BaseModel):
    id: int
    user_id: int
    date: date
    check_in: datetime
    check_out: Optional[datetime] = None
    total_minutes: Optional[int] = None
    ip_address: Optional[str] = None
    note: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[str] = None

    @classmethod
    def from_entity(cls, att) -> "AttendanceOutput":
        
        if not isinstance(att, Attendance):
            raise TypeError("Expected Attendance entity")
        return cls(
            id=att.id,
            user_id=att.user_id,
            date=att.date,
            check_in=att.check_in,
            check_out=att.check_out,
            total_minutes=att.total_minutes,
            ip_address=att.ip_address,
            note=att.note,
            department_id=att.department_id,
            status=att.status,
        )


class CheckinInput(BaseModel):
    user_id: int
    check_in: datetime
    ip_address: Optional[str] = None
    note: Optional[str] = None


class HeatmapFilterInput(BaseModel):
    start_date: date
    end_date: date
    user_id: Optional[int] = None
    department_id: Optional[int] = None
