import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from app.application.dtos.attendance import CheckinInput
from app.application.use_cases.attendance.checkin import CheckinUseCase
from app.domain.entities.attendance import Attendance
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation


@pytest.mark.asyncio
async def test_checkin_success():
    attendance_repo = AsyncMock()
    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = User(
        id=1, employee_code="E001", email="emp@example.com", full_name="Emp",
        role_name="employee", department_id=10, is_active=True,
    )
    attendance_repo.find_by_user_date.return_value = None
    created = Attendance(
        id=1,
        user_id=1,
        date=datetime(2026, 6, 1, 8, 30).date(),
        check_in=datetime(2026, 6, 1, 8, 30),
        ip_address="127.0.0.1",
        department_id=10,
        status="checked_in",
    )
    attendance_repo.create.return_value = created

    use_case = CheckinUseCase(attendance_repo=attendance_repo, user_repo=user_repo)
    data = CheckinInput(
        user_id=1,
        check_in=datetime(2026, 6, 1, 8, 30),
        ip_address="127.0.0.1",
    )
    result = await use_case.execute(data=data)

    assert result.id == 1
    assert result.status == "checked_in"
    assert result.department_id == 10


@pytest.mark.asyncio
async def test_checkin_already_checked_in():
    attendance_repo = AsyncMock()
    user_repo = AsyncMock()
    attendance_repo.find_by_user_date.return_value = Attendance(
        id=1,
        user_id=1,
        date=datetime(2026, 6, 1, 8, 30).date(),
        check_in=datetime(2026, 6, 1, 8, 30),
        status="checked_in",
    )

    use_case = CheckinUseCase(attendance_repo=attendance_repo, user_repo=user_repo)
    data = CheckinInput(
        user_id=1,
        check_in=datetime(2026, 6, 1, 8, 30),
    )
    with pytest.raises(BusinessRuleViolation):
        await use_case.execute(data=data)
