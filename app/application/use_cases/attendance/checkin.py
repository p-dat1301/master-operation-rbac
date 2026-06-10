from datetime import date

from app.application.dtos.attendance import AttendanceOutput, CheckinInput
from app.domain.entities.attendance import Attendance
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.attendance_repository import AttendanceRepository


class CheckinUseCase:
    """Use case check-in chấm công — actor tự check-in cho mình."""

    def __init__(
        self,
        attendance_repo: AttendanceRepository,
    ) -> None:
        self.attendance_repo = attendance_repo

    async def execute(self, actor: User, data: CheckinInput) -> AttendanceOutput:
        today = data.check_in.date()
        existing = await self.attendance_repo.find_by_user_date(actor.id, today)
        if existing is not None:
            raise BusinessRuleViolation("Already checked in today")

        attendance_entity = Attendance(
            id=0,
            user_id=actor.id,
            date=today,
            check_in=data.check_in,
            ip_address=data.ip_address,
            note=data.note,
            department_id=actor.department_id,
            status="checked_in",
        )
        created = await self.attendance_repo.create(attendance_entity)
        return AttendanceOutput.from_entity(created)
