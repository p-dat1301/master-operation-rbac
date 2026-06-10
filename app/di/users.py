from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user.account import ActivateUserUseCase, ChangePasswordUseCase, DeactivateUserUseCase, ResetPasswordUseCase
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.use_cases.user.delete_user import DeleteUserUseCase
from app.application.use_cases.user.get_user import GetUserUseCase
from app.application.use_cases.user.list_users import ListUsersUseCase
from app.application.use_cases.user.update_user import UpdateUserUseCase
from app.domain.services.rbac_service import RBACService
from app.infrastructure.security.bcrypt_service import BcryptService


def provide_list_users(db: AsyncSession) -> ListUsersUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return ListUsersUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_create_user(db: AsyncSession) -> CreateUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_role_repo import SQLAlchemyRoleRepository
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    role_repo = SQLAlchemyRoleRepository(db)
    password_service = BcryptService()
    rbac = RBACService()
    return CreateUserUseCase(user_repo=user_repo, role_repo=role_repo, password_service=password_service, rbac_service=rbac)


def provide_get_user(db: AsyncSession) -> GetUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return GetUserUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_update_user(db: AsyncSession) -> UpdateUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return UpdateUserUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_delete_user(db: AsyncSession) -> DeleteUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return DeleteUserUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_activate_user(db: AsyncSession) -> ActivateUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return ActivateUserUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_deactivate_user(db: AsyncSession) -> DeactivateUserUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    rbac = RBACService()
    return DeactivateUserUseCase(user_repo=user_repo, rbac_service=rbac)


def provide_change_password(db: AsyncSession) -> ChangePasswordUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    password_service = BcryptService()
    return ChangePasswordUseCase(user_repo=user_repo, password_service=password_service)


def provide_reset_password(db: AsyncSession) -> ResetPasswordUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository

    user_repo = SQLAlchemyUserRepository(db)
    password_service = BcryptService()
    rbac = RBACService()
    return ResetPasswordUseCase(user_repo=user_repo, password_service=password_service, rbac_service=rbac)
