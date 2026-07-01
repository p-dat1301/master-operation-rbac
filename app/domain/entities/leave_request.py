from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


class LeaveRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass
class LeaveRequest:
    id: int
    requester_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: LeaveRequestStatus = LeaveRequestStatus.PENDING
    department_id: Optional[int] = None
    reviewed_by: Optional[int] = None
    rejected_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")