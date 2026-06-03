import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.auth.get_me import GetMeUseCase
from app.application.dtos.user import UserOutput
from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound


@pytest.mark.asyncio
async def test_get_me_success():
    user_repo = AsyncMock()
    user = User(
        id=1,
        employee_code="E001",
        email="me@example.com",
        full_name="Me",
        role_name="employee",
    )
    user_repo.find_by_id.return_value = user

    use_case = GetMeUseCase(user_repo=user_repo)
    result = await use_case.execute(user_id=1)

    assert isinstance(result, UserOutput)
    assert result.id == 1
    assert result.email == "me@example.com"


@pytest.mark.asyncio
async def test_get_me_not_found():
    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = None

    use_case = GetMeUseCase(user_repo=user_repo)
    with pytest.raises(ResourceNotFound):
        await use_case.execute(user_id=99)
