from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.leave_request.create import CreateLeaveRequestUseCase
from app.application.use_cases.leave_request.manage import CancelLeaveRequestUseCase, UpdateLeaveRequestUseCase
from app.application.use_cases.leave_request.list_leave_request import ListLeaveRequestsUseCase
from app.application.use_cases.leave_request.review import ReviewLeaveRequestUseCase
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService
from app.infrastructure.notifications.console_notification import ConsoleNotificationService


def provide_create_leave(db: AsyncSession) -> CreateLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    balance_repo = SQLAlchemyLeaveBalanceRepository(db)
    return CreateLeaveRequestUseCase(leave_repo=leave_repo, leave_balance_repo=balance_repo)


def provide_list_leave(db: AsyncSession) -> ListLeaveRequestsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac = RBACService()
    dept_tree = DepartmentTreeService()
    return ListLeaveRequestsUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        rbac_service=rbac,
        dept_tree_service=dept_tree,
    )


def provide_review_leave(db: AsyncSession) -> ReviewLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    balance_repo = SQLAlchemyLeaveBalanceRepository(db)
    rbac = RBACService()
    dept_tree = DepartmentTreeService()
    notification_service = ConsoleNotificationService()
    return ReviewLeaveRequestUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        leave_balance_repo=balance_repo,
        rbac_service=rbac,
        dept_tree_service=dept_tree,
        notification_service=notification_service,
    )


def provide_update_leave(db: AsyncSession) -> UpdateLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    balance_repo = SQLAlchemyLeaveBalanceRepository(db)
    return UpdateLeaveRequestUseCase(leave_repo=leave_repo, leave_balance_repo=balance_repo)


def provide_cancel_leave(db: AsyncSession) -> CancelLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_balance_repo import SQLAlchemyLeaveBalanceRepository
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    balance_repo = SQLAlchemyLeaveBalanceRepository(db)
    return CancelLeaveRequestUseCase(leave_repo=leave_repo, leave_balance_repo=balance_repo)
