import pytest
from unittest.mock import AsyncMock

from app.application.dtos.task import AssignTaskInput
from app.application.use_cases.task.assign import AssignTaskUseCase
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.mark.asyncio
async def test_assign_task_success(rbac_service):
    task_repo = AsyncMock()
    actor = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"assign_task"},
        is_active=True,
    )
    task = Task(id=5, task_code="T5", title="Task 5")
    task_repo.find_by_id.return_value = task
    updated = Task(id=5, task_code="T5", title="Task 5", assignee_id=10, assigner_id=1)
    task_repo.assign_task.return_value = updated

    use_case = AssignTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)
    data = AssignTaskInput(task_id=5, assignee_id=10)
    result = await use_case.execute(actor=actor, data=data)

    assert result.assignee_id == 10


@pytest.mark.asyncio
async def test_assign_task_permission_denied(rbac_service):
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

    use_case = AssignTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)
    data = AssignTaskInput(task_id=5, assignee_id=10)
    with pytest.raises(PermissionDenied):
        await use_case.execute(actor=actor, data=data)


@pytest.mark.asyncio
async def test_assign_task_not_found(rbac_service):
    task_repo = AsyncMock()
    actor = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions={"assign_task"},
        is_active=True,
    )
    task_repo.find_by_id.return_value = None

    use_case = AssignTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)
    data = AssignTaskInput(task_id=99, assignee_id=10)
    with pytest.raises(ResourceNotFound):
        await use_case.execute(actor=actor, data=data)
