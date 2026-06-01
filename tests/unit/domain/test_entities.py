from datetime import date, datetime

import pytest

from app.domain.entities.attendance import Attendance
from app.domain.entities.department import Department
from app.domain.entities.leave_balance import LeaveBalance
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.notification import Notification
from app.domain.entities.permission import Permission
from app.domain.entities.role import Role
from app.domain.entities.role_permission import RolePermission
from app.domain.entities.task import Task
from app.domain.entities.user import User


def test_entities_support_equality_and_defaults():
    assert User(
        id=1,
        employee_code="EMP0001",
        email="user@example.com",
        full_name="User One",
        role_name="employee",
    ) == User(
        id=1,
        employee_code="EMP0001",
        email="user@example.com",
        full_name="User One",
        role_name="employee",
    )

    assert Department(id=2, name="Sales", level=2, parent_id=1) == Department(
        id=2,
        name="Sales",
        level=2,
        parent_id=1,
    )

    assert Task(id=3, task_code="TSK-001", title="Task") == Task(
        id=3,
        task_code="TSK-001",
        title="Task",
    )

    assert LeaveBalance(
        id=4,
        user_id=1,
        year=2026,
        total_days=12,
        used_days=1,
        pending_days=2,
        remaining_days=9,
    ) == LeaveBalance(
        id=4,
        user_id=1,
        year=2026,
        total_days=12,
        used_days=1,
        pending_days=2,
        remaining_days=9,
    )

    assert Attendance(
        id=5,
        user_id=1,
        date=date(2026, 6, 1),
        check_in=datetime(2026, 6, 1, 8, 0),
    ) == Attendance(
        id=5,
        user_id=1,
        date=date(2026, 6, 1),
        check_in=datetime(2026, 6, 1, 8, 0),
    )

    assert Notification(
        id=6,
        recipient_id=1,
        type="info",
        channel="in_app",
        message="Hello",
    ) == Notification(
        id=6,
        recipient_id=1,
        type="info",
        channel="in_app",
        message="Hello",
    )

    assert Role(id=7, name="manager", display_name="Manager") == Role(
        id=7,
        name="manager",
        display_name="Manager",
    )

    assert Permission(id=8, code="manage_org") == Permission(id=8, code="manage_org")
    assert RolePermission(role_id=7, permission_id=8) == RolePermission(
        role_id=7,
        permission_id=8,
    )


def test_leave_request_rejects_invalid_date_range():
    with pytest.raises(ValueError, match="end_date must be greater than or equal to start_date"):
        LeaveRequest(
            id=1,
            requester_id=1,
            leave_type="annual",
            start_date=date(2026, 6, 5),
            end_date=date(2026, 6, 4),
        )


def test_leave_request_accepts_valid_range():
    request = LeaveRequest(
        id=2,
        requester_id=1,
        leave_type="annual",
        start_date=date(2026, 6, 4),
        end_date=date(2026, 6, 5),
    )

    assert request.start_date == date(2026, 6, 4)
    assert request.end_date == date(2026, 6, 5)