import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.task.list_tasks import ListTasksUseCase
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def rbac_service():
    return RBACService()


@pytest.mark.asyncio
async def test_list_tasks_admin_scope(rbac_service):
    task_repo = AsyncMock()
    admin = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions=set(),
        is_active=True,
    )
    task_repo.list_all.return_value = [
        Task(id=1, task_code="T1", title="Task 1"),
    ]

    use_case = ListTasksUseCase(task_repo=task_repo, rbac_service=rbac_service)
    result = await use_case.execute(actor=admin)

    assert len(result) == 1
    task_repo.list_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_tasks_manager_scope(rbac_service):
    task_repo = AsyncMock()
    manager = User(
        id=2,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions=set(),
        department_id=10,
        is_active=True,
    )
    task_repo.list_by_department.return_value = [
        Task(id=2, task_code="T2", title="Task 2", department_id=10),
    ]

    use_case = ListTasksUseCase(task_repo=task_repo, rbac_service=rbac_service)
    result = await use_case.execute(actor=manager)

    assert len(result) == 1
    task_repo.list_by_department.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_list_tasks_employee_scope(rbac_service):
    task_repo = AsyncMock()
    emp = User(
        id=3,
        employee_code="E001",
        email="emp@example.com",
        full_name="Employee",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )
    task_repo.list_by_assignee.return_value = [
        Task(id=3, task_code="T3", title="Task 3", assignee_id=3),
    ]

    use_case = ListTasksUseCase(task_repo=task_repo, rbac_service=rbac_service)
    result = await use_case.execute(actor=emp)

    assert len(result) == 1
    task_repo.list_by_assignee.assert_awaited_once_with(3)
