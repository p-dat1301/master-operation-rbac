from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from app.application.dtos.leave_request import LeaveRequestCreateInput, LeaveRequestOutput, ReviewLeaveRequestInput


class LeaveCreateRequest(LeaveRequestCreateInput):
    pass


class LeaveResponse(LeaveRequestOutput):
    pass


class ReviewLeaveRequest(ReviewLeaveRequestInput):
    pass
