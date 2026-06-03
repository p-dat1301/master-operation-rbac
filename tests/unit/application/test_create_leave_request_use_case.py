import pytest
from unittest.mock import AsyncMock
from datetime import date

from app.application.dtos.leave_request import LeaveRequestCreateInput
from app.application.use_cases.leave_request.create import CreateLeaveRequestUseCase
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.user import User


@pytest.mark.asyncio
async def test_create_leave_request_success():
    leave_repo = AsyncMock()
    actor = User(
        id=1,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        department_id=10,
        is_active=True,
    )
    created = LeaveRequest(
        id=10,
        requester_id=1,
        leave_type="annual",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 5),
        reason="Vacation",
        status="pending",
        department_id=10,
    )
    leave_repo.create.return_value = created

    use_case = CreateLeaveRequestUseCase(leave_repo=leave_repo)
    data = LeaveRequestCreateInput(
        leave_type="annual",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 5),
        reason="Vacation",
    )
    result = await use_case.execute(actor=actor, data=data)

    assert result.id == 10
    assert result.status == "pending"
    assert result.department_id == 10
    assert result.requester_id == 1
