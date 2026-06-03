import pytest
from unittest.mock import AsyncMock

from app.application.dtos.task import CompleteTaskInput
from app.application.use_cases.task.complete import CompleteTaskUseCase
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.services.rbac_service import RBACService


@pytest.fixture
def complete_use_case():
    task_repo = AsyncMock()
    rbac_service = RBACService()
    return CompleteTaskUseCase(task_repo=task_repo, rbac_service=rbac_service)


@pytest.mark.asyncio
async def test_complete_task_as_assigner(complete_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions=set(),
        is_active=True,
    )
    task = Task(
        id=5,
        task_code="T5",
        title="Task 5",
        assigner_id=1,
        assignee_id=2,
        status="in_progress",
    )
    complete_use_case.task_repo.find_by_id.return_value = task
    complete_use_case.task_repo.update.return_value = Task(
        id=5,
        task_code="T5",
        title="Task 5",
        assigner_id=1,
        assignee_id=2,
        status="done",
    )

    result = await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=5))

    assert result.status == "done"
    complete_use_case.task_repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_task_with_permission(complete_use_case):
    actor = User(
        id=3,
        employee_code="M002",
        email="mgr2@example.com",
        full_name="Manager 2",
        role_name="manager",
        permissions={"complete_task"},
        is_active=True,
    )
    task = Task(
        id=6,
        task_code="T6",
        title="Task 6",
        assigner_id=1,
        assignee_id=2,
        status="todo",
    )
    complete_use_case.task_repo.find_by_id.return_value = task
    complete_use_case.task_repo.update.return_value = Task(
        id=6,
        task_code="T6",
        title="Task 6",
        assigner_id=1,
        assignee_id=2,
        status="done",
    )

    result = await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=6))

    assert result.status == "done"


@pytest.mark.asyncio
async def test_complete_task_admin_bypass(complete_use_case):
    actor = User(
        id=1,
        employee_code="A001",
        email="admin@example.com",
        full_name="Admin",
        role_name="admin",
        permissions=set(),
        is_active=True,
    )
    task = Task(
        id=7,
        task_code="T7",
        title="Task 7",
        assigner_id=99,
        assignee_id=2,
        status="in_progress",
    )
    complete_use_case.task_repo.find_by_id.return_value = task
    complete_use_case.task_repo.update.return_value = Task(
        id=7,
        task_code="T7",
        title="Task 7",
        assigner_id=99,
        assignee_id=2,
        status="done",
    )

    result = await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=7))

    assert result.status == "done"


@pytest.mark.asyncio
async def test_complete_task_not_found(complete_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"complete_task"},
        is_active=True,
    )
    complete_use_case.task_repo.find_by_id.return_value = None

    with pytest.raises(ResourceNotFound):
        await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=99))


@pytest.mark.asyncio
async def test_complete_task_permission_denied(complete_use_case):
    actor = User(
        id=2,
        employee_code="E001",
        email="emp@example.com",
        full_name="Emp",
        role_name="employee",
        permissions=set(),
        is_active=True,
    )
    task = Task(
        id=5,
        task_code="T5",
        title="Task 5",
        assigner_id=1,
        assignee_id=2,
        status="in_progress",
    )
    complete_use_case.task_repo.find_by_id.return_value = task

    with pytest.raises(PermissionDenied):
        await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=5))


@pytest.mark.asyncio
async def test_complete_task_already_done(complete_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"complete_task"},
        is_active=True,
    )
    task = Task(
        id=5,
        task_code="T5",
        title="Task 5",
        assigner_id=1,
        assignee_id=2,
        status="done",
    )
    complete_use_case.task_repo.find_by_id.return_value = task

    with pytest.raises(BusinessRuleViolation):
        await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=5))


@pytest.mark.asyncio
async def test_complete_task_cancelled(complete_use_case):
    actor = User(
        id=1,
        employee_code="M001",
        email="mgr@example.com",
        full_name="Manager",
        role_name="manager",
        permissions={"complete_task"},
        is_active=True,
    )
    task = Task(
        id=5,
        task_code="T5",
        title="Task 5",
        assigner_id=1,
        assignee_id=2,
        status="cancelled",
    )
    complete_use_case.task_repo.find_by_id.return_value = task

    with pytest.raises(BusinessRuleViolation):
        await complete_use_case.execute(actor=actor, data=CompleteTaskInput(task_id=5))
