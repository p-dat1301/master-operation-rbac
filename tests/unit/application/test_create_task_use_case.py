import pytest
from unittest.mock import AsyncMock

from app.application.dtos.task import TaskCreateInput
from app.application.use_cases.task.create import CreateTaskUseCase
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.mark.asyncio
async def test_create_task_success(rbac_service):
    task_repo = AsyncMock()
    actor = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"create_task"},
        is_active=True,
    )
    created = Task(id=10, task_code="T10", title="New Task", assigner_id=1)
    task_repo.create.return_value = created

    use_case = CreateTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)
    data = TaskCreateInput(task_code="T10", title="New Task")
    result = await use_case.execute(actor=actor, data=data)

    assert result.id == 10
    assert result.assigner_id == 1


@pytest.mark.asyncio
async def test_create_task_permission_denied(rbac_service):
    task_repo = AsyncMock()
    actor = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )

    use_case = CreateTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)
    data = TaskCreateInput(task_code="T10", title="New Task")
    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, data=data)
