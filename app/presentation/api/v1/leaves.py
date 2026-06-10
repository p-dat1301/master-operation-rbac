from fastapi import APIRouter, Depends, Path

from app.presentation.schemas.leave_schema import LeaveCreateRequest, LeaveResponse, LeaveUpdateRequest, ReviewLeaveRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di import provide_cancel_leave, provide_create_leave, provide_list_leave, provide_review_leave, provide_update_leave
from app.application.dtos.leave_request import LeaveRequestCreateInput, ReviewLeaveRequestInput
from app.application.dtos.leave_request import LeaveRequestOutput

router = APIRouter(prefix="/api/v1/leaves", tags=["leaves"])


@router.post("/", response_model=LeaveResponse)
async def create_leave(data: LeaveCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_create_leave(db)
    dto = LeaveRequestCreateInput(**data.dict())
    created = await use_case.execute(actor, dto)
    return LeaveResponse.from_entity(created)


@router.get("/", response_model=list[LeaveResponse])
async def list_leaves(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_list_leave(db)
    leaves = await use_case.execute(actor)
    return [LeaveResponse.from_entity(leave_request) for leave_request in leaves]


@router.put("/{id}/review", response_model=LeaveResponse)
async def review_leave(id: int = Path(...), data: ReviewLeaveRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_review_leave(db)
    dto = ReviewLeaveRequestInput(**{"leave_request_id": id, **(data.dict() if data else {})})
    updated = await use_case.execute(actor, dto)
    return LeaveResponse.from_entity(updated)


@router.put("/{id}", response_model=LeaveResponse)
async def update_leave(id: int = Path(...), data: LeaveUpdateRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_update_leave(db)
    dto = LeaveRequestCreateInput(**data.dict())
    updated = await use_case.execute(actor, id, dto)
    return LeaveResponse.from_entity(updated)


@router.put("/{id}/cancel", response_model=LeaveResponse)
async def cancel_leave(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_cancel_leave(db)
    updated = await use_case.execute(actor, id)
    return LeaveResponse.from_entity(updated)
