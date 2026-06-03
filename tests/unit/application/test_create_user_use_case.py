import pytest
from unittest.mock import AsyncMock

from app.application.dtos.user import UserCreateInput
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.services.rbac_service import RBACService


class FakePasswordService:
    def hash(self, plain: str) -> str:
        return f"hashed_{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return True


@pytest.fixture
def create_use_case():
    user_repo = AsyncMock()
    role_repo = AsyncMock()
    rbac_service = RBACService()
    return CreateUserUseCase(
        user_repo=user_repo,
        role_repo=role_repo,
        password_service=FakePasswordService(),
        rbac_service=rbac_service,
    )


@pytest.mark.asyncio
async def test_create_user_success(create_use_case):
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"manage_org"},
        is_active=True,
    )
    role = Role(id=2, name="employee", display_name="Employee")
    create_use_case.role_repo.find_by_name.return_value = role
    create_use_case.user_repo.find_by_email.return_value = None

    created_user = User(
        id=10,
        employee_code="E002",
        email="new@example.com",
        full_name="New User",
        role_name="employee",
        role_id=2,
        is_active=True,
    )
    create_use_case.user_repo.create.return_value = created_user

    data = UserCreateInput(
        employee_code="E002",
        email="new@example.com",
        full_name="New User",
        password="Secret123",
        role_name="employee",
    )

    result = await create_use_case.execute(actor=admin, data=data)

    assert result.id == 10
    create_use_case.user_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_permission_denied(create_use_case):
    employee = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )

    data = UserCreateInput(
        employee_code="E002",
        email="new@example.com",
        full_name="New User",
        password="Secret123",
        role_name="employee",
    )

    with pytest.raises(PermissionDenied):
        await create_use_case.execute(actor=employee, data=data)


@pytest.mark.asyncio
async def test_create_user_role_not_found(create_use_case):
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"manage_org"},
        is_active=True,
    )
    create_use_case.role_repo.find_by_name.return_value = None

    data = UserCreateInput(
        employee_code="E002",
        email="new@example.com",
        full_name="New User",
        password="Secret123",
        role_name="nonexistent",
    )

    with pytest.raises(ResourceNotFound):
        await create_use_case.execute(actor=admin, data=data)


@pytest.mark.asyncio
async def test_create_user_duplicate_email(create_use_case):
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"manage_org"},
        is_active=True,
    )
    role = Role(id=2, name="employee", display_name="Employee")
    create_use_case.role_repo.find_by_name.return_value = role
    create_use_case.user_repo.find_by_email.return_value = User(
        id=5, employee_code="X", email="dup@example.com", full_name="Dup", role_name="employee"
    )

    data = UserCreateInput(
        employee_code="E002",
        email="dup@example.com",
        full_name="New User",
        password="Secret123",
        role_name="employee",
    )

    with pytest.raises(BusinessRuleViolation):
        await create_use_case.execute(actor=admin, data=data)
