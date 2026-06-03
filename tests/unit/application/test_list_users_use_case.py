import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.user.list_users import ListUsersUseCase
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.mark.asyncio
async def test_list_users_success(rbac_service):
    user_repo = AsyncMock()
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"manage_org"},
        is_active=True,
    )
    user_repo.find_all.return_value = [admin]

    use_case = ListUsersUseCase(user_repo=user_repo, rbac_service=rbac_service)
    result = await use_case.execute(actor=admin)

    assert len(result) == 1
    assert result[0].id == 1


@pytest.mark.asyncio
async def test_list_users_permission_denied(rbac_service):
    user_repo = AsyncMock()
    employee = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )

    use_case = ListUsersUseCase(user_repo=user_repo, rbac_service=rbac_service)
    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=employee)
