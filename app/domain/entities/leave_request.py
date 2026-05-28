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
    reviewed_by: Optional[int] = None
    rejected_reason: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None