from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.security.bcrypt_service import BcryptService
from app.infrastructure.security.jwt_service import JWTService
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.user.list_users import ListUsersUseCase
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.domain.services.rbac_service import RBACService
from app.domain.services.department_tree import DepartmentTreeService
from app.infrastructure.notifications.console_notification import ConsoleNotificationService


def get_login_use_case(db: AsyncSession) -> LoginUseCase:
    """Factory to create LoginUseCase wired with infra implementations.

    Keep wiring centralized so routers don't instantiate dependencies directly.
    """
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    password_service = BcryptService()
    token_service = JWTService()
    return LoginUseCase(user_repo=user_repo, password_service=password_service, token_service=token_service)


def get_list_users_use_case(db: AsyncSession) -> ListUsersUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return ListUsersUseCase(user_repo=user_repo, rbac_service=rbac)


def get_create_user_use_case(db: AsyncSession) -> CreateUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository

    user_repo = SQLAlchemyUserRepository(db)
    role_repo = SQLAlchemyRoleRepository(db)
    password_service = BcryptService()
    rbac = RBACService()
    return CreateUserUseCase(user_repo=user_repo, role_repo=role_repo, password_service=password_service, rbac_service=rbac)


def get_list_tasks_use_case(db: AsyncSession) -> ListTasksUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return ListTasksUseCase(task_repo=task_repo, rbac_service=rbac)


def get_create_task_use_case(db: AsyncSession) -> CreateTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return CreateTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def get_create_leave_use_case(db: AsyncSession) -> CreateLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    return CreateLeaveRequestUseCase(leave_repo=leave_repo)


def get_list_leave_use_case(db: AsyncSession) -> ListLeaveRequestsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac = RBACService()
    dept_tree = DepartmentTreeService()
    return ListLeaveRequestsUseCase(leave_repo=leave_repo, dept_repo=dept_repo, rbac_service=rbac, dept_tree_service=dept_tree)


def get_review_leave_use_case(db: AsyncSession) -> ReviewLeaveRequestUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_leave_request_repo import SQLAlchemyLeaveRequestRepository
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    leave_repo = SQLAlchemyLeaveRequestRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac = RBACService()
    dept_tree = DepartmentTreeService()
    notification_service = ConsoleNotificationService()
    return ReviewLeaveRequestUseCase(leave_repo=leave_repo, dept_repo=dept_repo, rbac_service=rbac, dept_tree_service=dept_tree, notification_service=notification_service)


def get_checkin_use_case(db: AsyncSession) -> CheckinUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_attendance_repo import SQLAlchemyAttendanceRepository
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    attendance_repo = SQLAlchemyAttendanceRepository(db)
    user_repo = SQLAlchemyUserRepository(db)
    return CheckinUseCase(attendance_repo=attendance_repo, user_repo=user_repo)
