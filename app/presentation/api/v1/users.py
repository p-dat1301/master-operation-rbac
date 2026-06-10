from fastapi import APIRouter, Depends, Path, Query
from typing import Optional

from app.presentation.schemas.user_schema import UserCreateRequest, UserResponse, UserUpdateRequest
from app.presentation.schemas.user_account_schema import ChangePasswordRequest, ResetPasswordRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.users import (
    provide_activate_user,
    provide_change_password,
    provide_create_user,
    provide_deactivate_user,
    provide_delete_user,
    provide_get_user,
    provide_list_users,
    provide_reset_password,
    provide_update_user,
)
from app.application.dtos.user import UserCreateInput
from app.application.use_cases.user.update_user import UpdateUserInput

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)
):
    use_case = provide_create_user(db)
    dto = UserCreateInput(**data.model_dump())
    created = await use_case.execute(actor, dto)
    return UserResponse.from_entity(created)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    actor=Depends(get_current_user),
    db=Depends(get_db),
    department_id: Optional[int] = Query(None),
    role_name: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    use_case = provide_list_users(db)
    users = await use_case.execute(actor)
    # Apply filters on the result set
    result = users
    if department_id is not None:
        result = [u for u in result if u.department_id == department_id]
    if role_name is not None:
        result = [u for u in result if u.role_name == role_name]
    if is_active is not None:
        result = [u for u in result if u.is_active == is_active]
    return [UserResponse.from_entity(u) for u in result]


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_get_user(db)
    user = await use_case.execute(actor, id)
    return UserResponse.from_entity(user)


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    data: UserUpdateRequest,
    id: int = Path(...),
    actor=Depends(get_current_user),
    db=Depends(get_db),
):
    use_case = provide_update_user(db)
    update_input = UpdateUserInput(**data.model_dump(exclude_unset=True))
    updated = await use_case.execute(actor, id, update_input)
    return UserResponse.from_entity(updated)


@router.delete("/{id}", response_model=UserResponse)
async def delete_user(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_delete_user(db)
    deleted = await use_case.execute(actor, id)
    return UserResponse.from_entity(deleted)


@router.put("/{id}/activate", response_model=UserResponse)
async def activate_user(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_activate_user(db)
    updated = await use_case.execute(actor, id)
    return UserResponse.from_entity(updated)


@router.put("/{id}/deactivate", response_model=UserResponse)
async def deactivate_user(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_deactivate_user(db)
    updated = await use_case.execute(actor, id)
    return UserResponse.from_entity(updated)


@router.put("/{id}/change-password", response_model=UserResponse)
async def change_password(id: int = Path(...), data: ChangePasswordRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_change_password(db)
    updated = await use_case.execute(actor, id, data)
    return UserResponse.from_entity(updated)


@router.put("/{id}/reset-password", response_model=UserResponse)
async def reset_password(id: int = Path(...), data: ResetPasswordRequest = None, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_reset_password(db)
    updated = await use_case.execute(actor, id, data)
    return UserResponse.from_entity(updated)
