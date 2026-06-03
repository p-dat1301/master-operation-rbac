import pytest
from unittest.mock import AsyncMock
from datetime import date, datetime

from app.application.dtos.attendance import HeatmapFilterInput
from app.application.use_cases.attendance.heatmap import GetHeatmapUseCase
from app.domain.entities.attendance import Attendance
from app.domain.entities.department import Department
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.fixture
def dept_tree_service():
    return DepartmentTreeService()


@pytest.mark.asyncio
async def test_get_heatmap_admin_scope(rbac_service, dept_tree_service):
    attendance_repo = AsyncMock()
    dept_repo = AsyncMock()
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"view_attendance_all"},
        is_active=True,
    )
    attendance_repo.list_by_date_range.return_value = [
        Attendance(id=1, user_id=1, date=date(2026, 6, 1), check_in=datetime(2026, 6, 1, 8, 0)),
    ]

    use_case = GetHeatmapUseCase(
        attendance_repo=attendance_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    filters = HeatmapFilterInput(start_date=date(2026, 6, 1), end_date=date(2026, 6, 7))
    result = await use_case.execute(actor=admin, filters=filters)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_heatmap_manager_scope(rbac_service, dept_tree_service):
    attendance_repo = AsyncMock()
    dept_repo = AsyncMock()
    manager = User(
        id=2,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"view_attendance_dept"},
        department_id=10,
        is_active=True,
    )
    dept_repo.find_all.return_value = [
        Department(id=10, name="IT", level=2),
        Department(id=20, name="Dev", level=3, parent_id=10),
    ]
    attendance_repo.list_by_departments.return_value = [
        Attendance(id=2, user_id=2, date=date(2026, 6, 1), check_in=datetime(2026, 6, 1, 8, 0), department_id=20),
    ]

    use_case = GetHeatmapUseCase(
        attendance_repo=attendance_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    filters = HeatmapFilterInput(start_date=date(2026, 6, 1), end_date=date(2026, 6, 7))
    result = await use_case.execute(actor=manager, filters=filters)

    assert len(result) == 1
    attendance_repo.list_by_departments.assert_awaited_once_with({10, 20})


@pytest.mark.asyncio
async def test_get_heatmap_self_scope(rbac_service, dept_tree_service):
    attendance_repo = AsyncMock()
    dept_repo = AsyncMock()
    emp = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )
    attendance_repo.list_by_user.return_value = [
        Attendance(id=2, user_id=2, date=date(2026, 6, 1), check_in=datetime(2026, 6, 1, 8, 0)),
    ]

    use_case = GetHeatmapUseCase(
        attendance_repo=attendance_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    filters = HeatmapFilterInput(start_date=date(2026, 6, 1), end_date=date(2026, 6, 7))
    result = await use_case.execute(actor=emp, filters=filters)

    assert len(result) == 1
    attendance_repo.list_by_user.assert_awaited_once_with(2)


@pytest.mark.asyncio
async def test_get_heatmap_self_cannot_view_other_user(rbac_service, dept_tree_service):
    attendance_repo = AsyncMock()
    dept_repo = AsyncMock()
    emp = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )

    use_case = GetHeatmapUseCase(
        attendance_repo=attendance_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    filters = HeatmapFilterInput(
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 7),
        user_id=99,
    )
    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=emp, filters=filters)
