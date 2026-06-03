import pytest
from unittest.mock import AsyncMock
from datetime import date

from app.application.dtos.leave_request import ReviewLeaveRequestInput
from app.application.use_cases.leave_request.review import ReviewLeaveRequestUseCase
from app.domain.entities.department import Department
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


class FakeNotificationService:
    async def notify_user(self, user_id: int, title: str, message: str) -> None:
        pass


@pytest.fixture
def review_use_case():
    leave_repo = AsyncMock()
    dept_repo = AsyncMock()
    rbac_service = RBACService()
    dept_tree = DepartmentTreeService()
    notif_service = FakeNotificationService()
    return ReviewLeaveRequestUseCase(
        leave_repo=leave_repo,
        dept_repo=dept_repo,
        rbac_service=rbac_service,
        dept_tree_service=dept_tree,
        notification_service=notif_service,
    )


@pytest.mark.asyncio
async def test_review_leave_request_approve_success(review_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"approve_leave"},
        department_id=10,
        is_active=True,
    )
    leave = LeaveRequest(
        id=5,
        requester_id=2,
        leave_type="annual",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        status="pending",
        department_id=20,
    )
    review_use_case.leave_repo.find_by_id.return_value = leave
    review_use_case.dept_repo.find_all.return_value = [
        Department(id=10, name="IT", level=2),
        Department(id=20, name="Dev", level=3, parent_id=10),
    ]

    updated = LeaveRequest(
        id=5,
        requester_id=2,
        leave_type="annual",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        status="approved",
        department_id=20,
        reviewed_by=1,
    )
    review_use_case.leave_repo.update_status.return_value = updated

    data = ReviewLeaveRequestInput(leave_request_id=5, action="approve")
    result = await review_use_case.execute(actor=actor, data=data)

    assert result.status == "approved"


@pytest.mark.asyncio
async def test_review_leave_request_not_found(review_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"approve_leave"},
        department_id=10,
        is_active=True,
    )
    review_use_case.leave_repo.find_by_id.return_value = None

    data = ReviewLeaveRequestInput(leave_request_id=99, action="approve")
    with pytest.raises(ResourceNotFound):
        await review_use_case.execute(actor=actor, data=data)


@pytest.mark.asyncio
async def test_review_leave_request_permission_denied(review_use_case):
    actor = User(
        id=1,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )
    leave = LeaveRequest(
        id=5,
        requester_id=2,
        leave_type="annual",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 3),
        status="pending",
        department_id=20,
    )
    review_use_case.leave_repo.find_by_id.return_value = leave
    review_use_case.dept_repo.find_all.return_value = [
        Department(id=10, name="IT", level=2),
        Department(id=20, name="Dev", level=3, parent_id=10),
    ]

    data = ReviewLeaveRequestInput(leave_request_id=5, action="approve")
    with pytest.raises(PermissionDenied):
        await review_use_case.execute(actor=actor, data=data)
