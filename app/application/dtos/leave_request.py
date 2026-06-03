from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class LeaveRequestOutput(BaseModel):
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

    @classmethod
    def from_entity(cls, lr) -> "LeaveRequestOutput":
        from app.domain.entities.leave_request import LeaveRequest
        if not isinstance(lr, LeaveRequest):
            raise TypeError("Expected LeaveRequest entity")
        return cls(
            id=lr.id,
            requester_id=lr.requester_id,
            leave_type=lr.leave_type,
            start_date=lr.start_date,
            end_date=lr.end_date,
            reason=lr.reason,
            status=lr.status,
            department_id=lr.department_id,
            reviewed_by=lr.reviewed_by,
            rejected_reason=lr.rejected_reason,
            reviewed_at=lr.reviewed_at,
        )


class LeaveRequestCreateInput(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None


class ReviewLeaveRequestInput(BaseModel):
    leave_request_id: int
    action: str  # "approve" | "reject"
    rejected_reason: Optional[str] = None
