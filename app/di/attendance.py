from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.attendance.checkin import CheckinUseCase
from app.application.use_cases.attendance.checkout import CheckoutUseCase
from app.application.use_cases.attendance.heatmap import GetHeatmapUseCase
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


def provide_checkin(db: AsyncSession) -> CheckinUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_attendance_repo import SQLAlchemyAttendanceRepository

    attendance_repo = SQLAlchemyAttendanceRepository(db)
    return CheckinUseCase(attendance_repo=attendance_repo)


def provide_checkout(db: AsyncSession) -> CheckoutUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_attendance_repo import SQLAlchemyAttendanceRepository

    attendance_repo = SQLAlchemyAttendanceRepository(db)
    return CheckoutUseCase(attendance_repo=attendance_repo)


def provide_heatmap(db: AsyncSession) -> GetHeatmapUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_attendance_repo import SQLAlchemyAttendanceRepository
    from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

    attendance_repo = SQLAlchemyAttendanceRepository(db)
    dept_repo = SQLAlchemyDepartmentRepository(db)
    rbac = RBACService()
    dept_tree = DepartmentTreeService()
    return GetHeatmapUseCase(
        attendance_repo=attendance_repo,
        dept_repo=dept_repo,
        rbac_service=rbac,
        dept_tree_service=dept_tree,
    )
