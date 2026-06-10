from __future__ import annotations

from datetime import date

from app.application.dtos.leave_balance import LeaveBalanceOutput, LeaveBalanceUpdateInput
from app.domain.entities.leave_balance import LeaveBalance
from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.leave_balance_repository import LeaveBalanceRepository
from app.domain.services.rbac_service import RBACService


def _default_balance(user_id: int, year: int) -> LeaveBalance:
    total_days = 12.0
    used_days = 0.0
    return LeaveBalance(
        id=0,
        user_id=user_id,
        year=year,
        total_days=total_days,
        used_days=used_days,
        pending_days=0.0,
        remaining_days=total_days - used_days,
    )


class GetMyLeaveBalanceUseCase:
    def __init__(self, balance_repo: LeaveBalanceRepository) -> None:
        self.balance_repo = balance_repo

    async def execute(self, actor: User, year: int | None = None) -> LeaveBalanceOutput:
        target_year = year or date.today().year
        balance = await self.balance_repo.find_by_user_year(actor.id, target_year)
        if balance is None:
            balance = _default_balance(actor.id, target_year)
        return LeaveBalanceOutput.from_entity(balance)


class GetUserLeaveBalanceUseCase:
    def __init__(self, balance_repo: LeaveBalanceRepository, rbac_service: RBACService) -> None:
        self.balance_repo = balance_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int, year: int | None = None) -> LeaveBalanceOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        target_year = year or date.today().year
        balance = await self.balance_repo.find_by_user_year(user_id, target_year)
        if balance is None:
            balance = _default_balance(user_id, target_year)
        return LeaveBalanceOutput.from_entity(balance)


class UpdateLeaveBalanceUseCase:
    def __init__(self, balance_repo: LeaveBalanceRepository, rbac_service: RBACService) -> None:
        self.balance_repo = balance_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int, data: LeaveBalanceUpdateInput) -> LeaveBalanceOutput:
        self.rbac_service.require_permission(actor, "manage_org")
        balance = LeaveBalance(
            id=0,
            user_id=user_id,
            year=data.year,
            total_days=data.total_days,
            used_days=data.used_days,
            pending_days=0.0,
            remaining_days=data.total_days - data.used_days,
        )
        updated = await self.balance_repo.upsert(balance)
        return LeaveBalanceOutput.from_entity(updated)