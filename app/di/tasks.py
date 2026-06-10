from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.task.cancel import CancelTaskUseCase
from app.application.use_cases.task.delete import DeleteTaskUseCase
from app.application.use_cases.task.assign import AssignTaskUseCase
from app.application.use_cases.task.complete import CompleteTaskUseCase
from app.application.use_cases.task.create import CreateTaskUseCase
from app.application.use_cases.task.get_task import GetTaskUseCase
from app.application.use_cases.task.list_tasks import ListTasksUseCase
from app.application.use_cases.task.start import StartTaskUseCase
from app.application.use_cases.task.update import UpdateTaskUseCase
from app.domain.services.rbac_service import RBACService


def provide_list_tasks(db: AsyncSession) -> ListTasksUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return ListTasksUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_create_task(db: AsyncSession) -> CreateTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return CreateTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_assign_task(db: AsyncSession) -> AssignTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return AssignTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_complete_task(db: AsyncSession) -> CompleteTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return CompleteTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_get_task(db: AsyncSession) -> GetTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return GetTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_update_task(db: AsyncSession) -> UpdateTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return UpdateTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_cancel_task(db: AsyncSession) -> CancelTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return CancelTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_start_task(db: AsyncSession) -> StartTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return StartTaskUseCase(task_repo=task_repo, rbac_service=rbac)


def provide_delete_task(db: AsyncSession) -> DeleteTaskUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_task_repo import SQLAlchemyTaskRepository

    task_repo = SQLAlchemyTaskRepository(db)
    rbac = RBACService()
    return DeleteTaskUseCase(task_repo=task_repo, rbac_service=rbac)
