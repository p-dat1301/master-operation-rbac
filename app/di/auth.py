from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.auth.login import LoginUseCase
from app.infrastructure.security.bcrypt_service import BcryptService
from app.infrastructure.security.jwt_service import JWTService


def provide_login(db: AsyncSession) -> LoginUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    password_service = BcryptService()
    token_service = JWTService()
    return LoginUseCase(user_repo=user_repo, password_service=password_service, token_service=token_service)
