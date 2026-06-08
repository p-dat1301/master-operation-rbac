from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.application.dtos.attendance import AttendanceOutput, CheckinInput, HeatmapFilterInput


class CheckinRequest(BaseModel):
    check_in: datetime
    ip_address: Optional[str] = None
    note: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

    def to_dto(self) -> CheckinInput:
        return CheckinInput(**self.model_dump())


class AttendanceResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_dto(cls, dto: AttendanceOutput) -> "AttendanceResponse":
        return cls(**dto.model_dump())


class HeatmapRequest(BaseModel):
    start_date: date
    end_date: date
    user_id: Optional[int] = None
    department_id: Optional[int] = None

    model_config = ConfigDict(extra="ignore")

    def to_dto(self) -> HeatmapFilterInput:
        return HeatmapFilterInput(**self.model_dump())
