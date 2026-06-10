from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.application.dtos.leave_request import LeaveRequestCreateInput, LeaveRequestOutput, ReviewLeaveRequestInput


class LeaveCreateRequest(LeaveRequestCreateInput):
    pass


class LeaveResponse(LeaveRequestOutput):
    pass


class ReviewLeaveRequest(ReviewLeaveRequestInput):
    pass


class LeaveUpdateRequest(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
