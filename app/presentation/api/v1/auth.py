from fastapi import APIRouter, Depends

from app.presentation.schemas.auth_schema import LoginRequest, LoginResponse
from app.presentation.schemas.user_schema import UserResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di import provide_login

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db=Depends(get_db)) -> LoginResponse:
    use_case = provide_login(db)
    result = await use_case.execute(data)
    return LoginResponse(access_token=result.access_token, expires_in=result.expires_in)


@router.get("/me", response_model=UserResponse)
async def me(actor=Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_entity(actor)
