from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class LeaveRequest:
    id: int
    requester_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str = "pending"
    department_id: Optional[int] = None
    reviewed_by: Optional[int] = None
    rejected_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")