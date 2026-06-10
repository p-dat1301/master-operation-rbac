from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.leave_balance.crud import (
    GetMyLeaveBalanceUseCase,
    GetUserLeaveBalanceUseCase,
    UpdateLeaveBalanceUseCase,
)
from app.domain.services.rbac_service import RBACService


def provide_get_my_leave_balance(db: AsyncSession) -> GetMyLeaveBalanceUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository

    return GetMyLeaveBalanceUseCase(balance_repo=SQLAlchemyLeaveBalanceRepository(db))


def provide_get_user_leave_balance(db: AsyncSession) -> GetUserLeaveBalanceUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository

    return GetUserLeaveBalanceUseCase(balance_repo=SQLAlchemyLeaveBalanceRepository(db), rbac_service=RBACService())


def provide_update_leave_balance(db: AsyncSession) -> UpdateLeaveBalanceUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository

    return UpdateLeaveBalanceUseCase(balance_repo=SQLAlchemyLeaveBalanceRepository(db), rbac_service=RBACService())