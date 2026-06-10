from __future__ import annotations

from datetime import date

from app.application.dtos.leave_request import LeaveRequestCreateInput, LeaveRequestOutput
from app.domain.entities.leave_balance import LeaveBalance
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.repositories.leave_balance_repository import LeaveBalanceRepository
from app.domain.repositories.leave_request_repository import LeaveRequestRepository


def _leave_days(start_date: date, end_date: date) -> int:
    return (end_date - start_date).days + 1


def _overlaps(start_date: date, end_date: date, other_start: date, other_end: date) -> bool:
    return start_date <= other_end and end_date >= other_start


class UpdateLeaveRequestUseCase:
    def __init__(self, leave_repo: LeaveRequestRepository, leave_balance_repo: LeaveBalanceRepository) -> None:
        self.leave_repo = leave_repo
        self.leave_balance_repo = leave_balance_repo

    async def execute(self, actor: User, leave_id: int, data: LeaveRequestCreateInput) -> LeaveRequestOutput:
        leave = await self.leave_repo.find_by_id(leave_id)
        if leave is None:
            raise ResourceNotFound("Leave request not found")
        if leave.requester_id != actor.id:
            raise PermissionDenied("You can only update your own leave request")
        if leave.status != "pending":
            raise BusinessRuleViolation("Only pending leave requests can be updated")

        existing_leaves = await self.leave_repo.list_by_requester(actor.id)
        for existing_leave in existing_leaves:
            if existing_leave.id == leave_id:
                continue
            if existing_leave.status in {"pending", "approved"} and _overlaps(data.start_date, data.end_date, existing_leave.start_date, existing_leave.end_date):
                raise BusinessRuleViolation("Leave request overlaps with an existing leave request")

        balance = await self.leave_balance_repo.find_by_user_year(actor.id, data.start_date.year)
        required_days = _leave_days(data.start_date, data.end_date)
        if balance is not None and balance.remaining_days < required_days:
            raise BusinessRuleViolation("Insufficient leave balance")

        updated_leave = LeaveRequest(
            id=leave_id,
            requester_id=actor.id,
            leave_type=data.leave_type,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            status=leave.status,
            department_id=leave.department_id,
        )
        updated = await self.leave_repo.update(updated_leave)
        return LeaveRequestOutput.from_entity(updated)


class CancelLeaveRequestUseCase:
    def __init__(self, leave_repo: LeaveRequestRepository, leave_balance_repo: LeaveBalanceRepository) -> None:
        self.leave_repo = leave_repo
        self.leave_balance_repo = leave_balance_repo

    async def execute(self, actor: User, leave_id: int) -> LeaveRequestOutput:
        leave = await self.leave_repo.find_by_id(leave_id)
        if leave is None:
            raise ResourceNotFound("Leave request not found")
        if leave.requester_id != actor.id:
            raise PermissionDenied("You can only cancel your own leave request")
        if leave.status == "cancelled":
            raise BusinessRuleViolation("Leave request already cancelled")

        if leave.status == "approved":
            balance = await self.leave_balance_repo.find_by_user_year(actor.id, leave.start_date.year)
            required_days = _leave_days(leave.start_date, leave.end_date)
            if balance is None:
                balance = LeaveBalance(
                    id=0,
                    user_id=actor.id,
                    year=leave.start_date.year,
                    total_days=12.0,
                    used_days=0.0,
                    pending_days=0.0,
                    remaining_days=12.0,
                )
            restored_used_days = max(balance.used_days - required_days, 0.0)
            restored_balance = LeaveBalance(
                id=balance.id,
                user_id=actor.id,
                year=leave.start_date.year,
                total_days=balance.total_days,
                used_days=restored_used_days,
                pending_days=0.0,
                remaining_days=balance.total_days - restored_used_days,
            )
            await self.leave_balance_repo.upsert(restored_balance)

        updated_leave = LeaveRequest(
            id=leave.id,
            requester_id=leave.requester_id,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status="cancelled",
            department_id=leave.department_id,
        )
        updated = await self.leave_repo.update(updated_leave)
        return LeaveRequestOutput.from_entity(updated)