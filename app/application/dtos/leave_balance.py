from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.leave_balance import LeaveBalance


class LeaveBalanceOutput(BaseModel):
    id: int
    user_id: int
    year: int
    total_days: float
    used_days: float
    pending_days: float
    remaining_days: float
    updated_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, balance: LeaveBalance) -> "LeaveBalanceOutput":
        if not isinstance(balance, LeaveBalance):
            raise TypeError("Expected LeaveBalance entity")
        return cls(
            id=balance.id,
            user_id=balance.user_id,
            year=balance.year,
            total_days=balance.total_days,
            used_days=balance.used_days,
            pending_days=balance.pending_days,
            remaining_days=balance.remaining_days,
            updated_at=balance.updated_at,
        )


class LeaveBalanceUpdateInput(BaseModel):
    year: int
    total_days: float
    used_days: float = 0.0