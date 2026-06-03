import pytest
from unittest.mock import AsyncMock
from datetime import date

from app.application.use_cases.leave_request.list_leave_request import ListLeaveRequestsUseCase
from app.domain.entities.department import Department
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.user import User
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.fixture
def dept_tree_service():
    return DepartmentTreeService()


@pytest.mark.asyncio
async def test_list_leave_requests_admin(rbac_service, dept_tree_service):
    leave_repo = AsyncMock()
    dept_repo = AsyncMock()
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"approve_leave"},
        is_active=True,
    )
    leave_repo.list_all.return_value = [
        LeaveRequest(id=1, requester_id=2, leave_type="sick", start_date=date(2026, 6, 1), end_date=date(2026, 6, 2)),
    ]

    use_case = ListLeaveRequestsUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    result = await use_case.execute(actor=admin)

    assert len(result) == 1
    leave_repo.list_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_leave_requests_manager_scope(rbac_service, dept_tree_service):
    leave_repo = AsyncMock()
    dept_repo = AsyncMock()
    manager = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"approve_leave"},
        department_id=10,
        is_active=True,
    )
    dept_repo.find_all.return_value = [
        Department(id=10, name="IT", level=2),
        Department(id=20, name="Dev", level=3, parent_id=10),
    ]
    leave_repo.list_by_departments.return_value = [
        LeaveRequest(id=1, requester_id=2, leave_type="sick", start_date=date(2026, 6, 1), end_date=date(2026, 6, 2), department_id=20),
    ]

    use_case = ListLeaveRequestsUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    result = await use_case.execute(actor=manager)

    assert len(result) == 1
    leave_repo.list_by_departments.assert_awaited_once_with({10, 20})


@pytest.mark.asyncio
async def test_list_leave_requests_employee(rbac_service, dept_tree_service):
    leave_repo = AsyncMock()
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
    leave_repo.list_by_requester.return_value = [
        LeaveRequest(id=2, requester_id=2, leave_type="annual", start_date=date(2026, 6, 1), end_date=date(2026, 6, 2)),
    ]

    use_case = ListLeaveRequestsUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree_service,
    )
    result = await use_case.execute(actor=emp)

    assert len(result) == 1
    leave_repo.list_by_requester.assert_awaited_once_with(2)
