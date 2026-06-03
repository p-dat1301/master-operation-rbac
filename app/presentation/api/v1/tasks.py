from fastapi import APIRouter, Depends

from app.presentation.schemas.task_schema import TaskCreateRequest, TaskResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.container import get_create_task_use_case, get_list_tasks_use_case
from app.application.dtos.task import TaskCreateInput

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_create_task_use_case(db)
    dto = TaskCreateInput(**data.dict())
    created = await use_case.execute(actor, dto)
    return TaskResponse.from_entity(created)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_list_tasks_use_case(db)
    tasks = await use_case.execute(actor)
    return [TaskResponse.from_entity(t) for t in tasks]
