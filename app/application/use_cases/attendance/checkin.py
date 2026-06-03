from datetime import date

from app.application.dtos.attendance import AttendanceOutput, CheckinInput
from app.domain.entities.attendance import Attendance
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.attendance_repository import AttendanceRepository
from app.domain.repositories.user_repository import UserRepository


class CheckinUseCase:
    """Use case check-in chấm công."""

    def __init__(
        self,
        attendance_repo: AttendanceRepository,
        user_repo: UserRepository,
    ) -> None:
        self.attendance_repo = attendance_repo
        self.user_repo = user_repo

    async def execute(self, data: CheckinInput) -> AttendanceOutput:
        today = data.check_in.date()
        existing = await self.attendance_repo.find_by_user_date(data.user_id, today)
        if existing is not None:
            raise BusinessRuleViolation("Already checked in today")

        actor_user = await self.user_repo.find_by_id(data.user_id)
        dept_id = actor_user.department_id if actor_user else None

        attendance_entity = Attendance(
            id=0,
            user_id=data.user_id,
            date=today,
            check_in=data.check_in,
            ip_address=data.ip_address,
            note=data.note,
            department_id=dept_id,
            status="checked_in",
        )
        created = await self.attendance_repo.create(attendance_entity)
        return AttendanceOutput.from_entity(created)
