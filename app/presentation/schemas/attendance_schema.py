from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from app.application.dtos.attendance import CheckinInput, AttendanceOutput, HeatmapFilterInput


class CheckinRequest(CheckinInput):
    pass


class AttendanceResponse(AttendanceOutput):
    pass


class HeatmapRequest(HeatmapFilterInput):
    pass
