from __future__ import annotations

from datetime import date

from app.application.dtos.leave_request import LeaveRequestCreateInput, LeaveRequestOutput
from app.domain.entities.leave_request import LeaveRequest, LeaveRequestStatus
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation
from app.domain.repositories.leave_balance_repository import LeaveBalanceRepository
from app.domain.repositories.leave_request_repository import LeaveRequestRepository


def _leave_days(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1


def _overlaps(start_date: date, end_date: date, other_start: date, other_end: date) -> bool:
    return start_date <= other_end and end_date >= other_start


class CreateLeaveRequestUseCase:
    """Use case tạo đơn xin nghỉ."""

    def __init__(self, leave_repo: LeaveRequestRepository, leave_balance_repo: LeaveBalanceRepository) -> None:
        self.leave_repo = leave_repo
        self.leave_balance_repo = leave_balance_repo

    async def execute(self, actor: User, data: LeaveRequestCreateInput) -> LeaveRequestOutput:
        existing_leaves = await self.leave_repo.list_by_requester(actor.id)
        for leave in existing_leaves:
            if leave.status in {LeaveRequestStatus.PENDING, LeaveRequestStatus.APPROVED} and _overlaps(data.start_date, data.end_date, leave.start_date, leave.end_date):
                raise BusinessRuleViolation("Leave request overlaps with an existing leave request")

        balance = await self.leave_balance_repo.find_by_user_year(actor.id, data.start_date.year)
        required_days = _leave_days(data.start_date, data.end_date)
        if balance is not None and balance.remaining_days < required_days:
            raise BusinessRuleViolation("Insufficient leave balance")

        leave_entity = LeaveRequest(
            id=0,
            requester_id=actor.id,
            leave_type=data.leave_type,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            status=LeaveRequestStatus.PENDING,
            department_id=actor.department_id,
        )
        created = await self.leave_repo.create(leave_entity)
        return LeaveRequestOutput.from_entity(created)
