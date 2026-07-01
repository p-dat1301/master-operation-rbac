from __future__ import annotations

from pydantic import BaseModel

from app.application.dtos.leave_balance import LeaveBalanceOutput, LeaveBalanceUpdateInput


class LeaveBalanceResponse(LeaveBalanceOutput):

    @classmethod
    def from_dto(cls, dto: LeaveBalanceOutput) -> "LeaveBalanceResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            year=dto.year,
            total_days=dto.total_days,
            used_days=dto.used_days,
            pending_days=dto.pending_days,
            remaining_days=dto.remaining_days,
        )


class LeaveBalanceUpdateRequest(LeaveBalanceUpdateInput):
    pass
