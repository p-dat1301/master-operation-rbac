from fastapi import APIRouter, Depends, Path

from app.presentation.schemas.leave_schema import LeaveCreateRequest, LeaveResponse, ReviewLeaveRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.container import get_create_leave_use_case, get_list_leave_use_case, get_review_leave_use_case
from app.application.dtos.leave_request import LeaveRequestCreateInput, ReviewLeaveRequestInput

router = APIRouter(prefix="/api/v1/leaves", tags=["leaves"])


@router.post("/", response_model=LeaveResponse)
async def create_leave(data: LeaveCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_create_leave_use_case(db)
    dto = LeaveRequestCreateInput(**data.dict())
    created = await use_case.execute(actor, dto)
    return LeaveResponse.from_entity(created)


@router.get("/", response_model=list[LeaveResponse])
async def list_leaves(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_list_leave_use_case(db)
    leaves = await use_case.execute(actor)
    return [LeaveResponse.from_entity(l) for l in leaves]


@router.put("/{id}/review", response_model=LeaveResponse)
async def review_leave(id: int = Path(...), data: ReviewLeaveRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_review_leave_use_case(db)
    dto = ReviewLeaveRequestInput(**{"leave_request_id": id, **(data.dict() if data else {})})
    updated = await use_case.execute(actor, dto)
    return LeaveResponse.from_entity(updated)
