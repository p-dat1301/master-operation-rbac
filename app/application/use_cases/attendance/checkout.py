from __future__ import annotations

from datetime import datetime

from app.application.dtos.attendance import AttendanceOutput
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, ResourceNotFound
from app.domain.repositories.attendance_repository import AttendanceRepository


class CheckoutUseCase:
    def __init__(self, attendance_repo: AttendanceRepository) -> None:
        self.attendance_repo = attendance_repo

    async def execute(self, actor: User, check_out: datetime | None = None) -> AttendanceOutput:
        checkout_time = check_out or datetime.utcnow()
        attendance = await self.attendance_repo.find_by_user_date(actor.id, checkout_time.date())
        if attendance is None:
            raise ResourceNotFound("Attendance check-in not found for today")
        if attendance.check_out is not None:
            raise BusinessRuleViolation("Already checked out today")
        total_minutes = int((checkout_time - attendance.check_in).total_seconds() // 60)
        updated = await self.attendance_repo.checkout(attendance.id, checkout_time, total_minutes)
        return AttendanceOutput.from_entity(updated)