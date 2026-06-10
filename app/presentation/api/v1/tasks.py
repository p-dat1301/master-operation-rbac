from fastapi import APIRouter, Depends, Path, Query
from typing import Optional

from app.presentation.schemas.task_schema import AssignTaskRequest, TaskCreateRequest, TaskResponse, TaskUpdateRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.tasks import (
    provide_assign_task,
    provide_cancel_task,
    provide_complete_task,
    provide_create_task,
    provide_delete_task,
    provide_get_task,
    provide_list_tasks,
    provide_start_task,
    provide_update_task,
)
from app.application.dtos.task import AssignTaskInput, CompleteTaskInput, TaskCreateInput, TaskUpdateInput

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_create_task(db)
    dto = TaskCreateInput(**data.model_dump())
    created = await use_case.execute(actor, dto)
    return TaskResponse.from_entity(created)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    actor=Depends(get_current_user),
    db=Depends(get_db),
    status: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
):
    use_case = provide_list_tasks(db)
    tasks = await use_case.execute(actor)
    # Apply filters
    result = tasks
    if status is not None:
        result = [t for t in result if t.status == status]
    if assignee_id is not None:
        result = [t for t in result if t.assignee_id == assignee_id]
    if department_id is not None:
        result = [t for t in result if t.department_id == department_id]
    return [TaskResponse.from_entity(t) for t in result]


@router.get("/{id}", response_model=TaskResponse)
async def get_task(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_get_task(db)
    task = await use_case.execute(actor, id)
    return TaskResponse.from_entity(task)


@router.put("/{id}/assign", response_model=TaskResponse)
async def assign_task(id: int = Path(...), data: AssignTaskRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_assign_task(db)
    dto = AssignTaskInput(task_id=id, assignee_id=data.assignee_id)
    updated = await use_case.execute(actor, dto)
    return TaskResponse.from_entity(updated)


@router.put("/{id}/complete", response_model=TaskResponse)
async def complete_task(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_complete_task(db)
    dto = CompleteTaskInput(task_id=id)
    updated = await use_case.execute(actor, dto)
    return TaskResponse.from_entity(updated)


@router.put("/{id}", response_model=TaskResponse)
async def update_task(id: int = Path(...), data: TaskUpdateRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_update_task(db)
    dto = TaskUpdateInput(**data.dict())
    updated = await use_case.execute(actor, id, dto)
    return TaskResponse.from_entity(updated)


@router.delete("/{id}")
async def delete_task(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_delete_task(db)
    await use_case.execute(actor, id)
    return {"detail": "Task deleted"}


@router.put("/{id}/cancel", response_model=TaskResponse)
async def cancel_task(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_cancel_task(db)
    updated = await use_case.execute(actor, id)
    return TaskResponse.from_entity(updated)


@router.put("/{id}/start", response_model=TaskResponse)
async def start_task(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_start_task(db)
    updated = await use_case.execute(actor, id)
    return TaskResponse.from_entity(updated)
