from __future__ import annotations

from pydantic import ConfigDict

from app.application.dtos.attendance import AttendanceOutput, CheckinInput, HeatmapFilterInput


class CheckinRequest(CheckinInput):
    model_config = ConfigDict(extra="ignore")


class AttendanceResponse(AttendanceOutput):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_dto(cls, dto: AttendanceOutput) -> "AttendanceResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            date=dto.date,
            check_in=dto.check_in,
            check_out=dto.check_out,
            total_minutes=dto.total_minutes,
            ip_address=dto.ip_address,
            note=dto.note,
            department_id=dto.department_id,
            status=dto.status,
        )


class HeatmapRequest(HeatmapFilterInput):
    model_config = ConfigDict(extra="ignore")
