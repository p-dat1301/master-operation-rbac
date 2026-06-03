import pytest
from unittest.mock import AsyncMock

from app.application.dtos.auth import LoginInput
from app.application.use_cases.auth.login import LoginUseCase
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound


class FakePasswordService:
    def verify(self, plain: str, hashed: str) -> bool:
        return plain == "secret" and hashed == "hashed_secret"

    def hash(self, plain: str) -> str:
        return f"hashed_{plain}"


class FakeTokenService:
    def create_access_token(self, subject: str, claims: dict | None = None) -> str:
        return "fake-jwt-token"


@pytest.fixture
def login_use_case():
    user_repo = AsyncMock()
    return LoginUseCase(
        user_repo=user_repo,
        password_service=FakePasswordService(),
        token_service=FakeTokenService(),
    )


@pytest.mark.asyncio
async def test_login_success(login_use_case):
    user = User(
        id=1,
        employee_code="E001",
        email="test@example.com",
        full_name="Test User",
        role_name="employee",
        hashed_password="hashed_secret",
        is_active=True,
    )
    login_use_case.user_repo.find_by_email.return_value = user

    result = await login_use_case.execute(LoginInput(email="test@example.com", password="secret"))

    assert result.access_token == "fake-jwt-token"
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_user_not_found(login_use_case):
    login_use_case.user_repo.find_by_email.return_value = None

    with pytest.raises(ResourceNotFound):
        await login_use_case.execute(LoginInput(email="missing@example.com", password="secret"))


@pytest.mark.asyncio
async def test_login_inactive_user(login_use_case):
    user = User(
        id=1,
        employee_code="E001",
        email="inactive@example.com",
        full_name="Inactive",
        role_name="employee",
        hashed_password="hashed_secret",
        is_active=False,
    )
    login_use_case.user_repo.find_by_email.return_value = user

    with pytest.raises(PermissionDenied):
        await login_use_case.execute(LoginInput(email="inactive@example.com", password="secret"))


@pytest.mark.asyncio
async def test_login_wrong_password(login_use_case):
    user = User(
        id=1,
        employee_code="E001",
        email="test@example.com",
        full_name="Test User",
        role_name="employee",
        hashed_password="hashed_secret",
        is_active=True,
    )
    login_use_case.user_repo.find_by_email.return_value = user

    with pytest.raises(PermissionDenied):
        await login_use_case.execute(LoginInput(email="test@example.com", password="wrong"))
