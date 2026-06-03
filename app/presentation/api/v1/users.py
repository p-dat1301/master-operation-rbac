from fastapi import APIRouter, Depends

from app.presentation.schemas.user_schema import UserCreateRequest, UserResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.container import get_create_user_use_case, get_list_users_use_case
from app.application.dtos.user import UserCreateInput

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)
):
    use_case = get_create_user_use_case(db)
    dto = UserCreateInput(**data.dict())
    created = await use_case.execute(actor, dto)
    return UserResponse.from_entity(created)


@router.get("/", response_model=list[UserResponse])
async def list_users(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = get_list_users_use_case(db)
    users = await use_case.execute(actor)
    return [UserResponse.from_entity(u) for u in users]
