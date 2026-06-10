from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query

from app.di.leave_balances import provide_get_my_leave_balance, provide_get_user_leave_balance, provide_update_leave_balance
from app.presentation.dependencies.auth_deps import get_current_user
from app.presentation.dependencies.db_deps import get_db
from app.presentation.schemas.leave_balance_schema import LeaveBalanceResponse, LeaveBalanceUpdateRequest

router = APIRouter(prefix="/api/v1/leave-balances", tags=["leave-balances"])


@router.get("/me", response_model=LeaveBalanceResponse)
async def get_my_leave_balance(actor=Depends(get_current_user), db=Depends(get_db), year: int | None = Query(None)):
    use_case = provide_get_my_leave_balance(db)
    dto = await use_case.execute(actor, year=year)
    return LeaveBalanceResponse.from_dto(dto)


@router.get("/users/{user_id}", response_model=LeaveBalanceResponse)
async def get_user_leave_balance(user_id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db), year: int | None = Query(None)):
    use_case = provide_get_user_leave_balance(db)
    dto = await use_case.execute(actor, user_id=user_id, year=year)
    return LeaveBalanceResponse.from_dto(dto)


@router.put("/users/{user_id}", response_model=LeaveBalanceResponse)
async def update_user_leave_balance(user_id: int = Path(...), data: LeaveBalanceUpdateRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_update_leave_balance(db)
    dto = await use_case.execute(actor, user_id=user_id, data=data)
    return LeaveBalanceResponse.from_dto(dto)