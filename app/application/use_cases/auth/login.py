from app.application.dtos.auth import LoginInput, LoginOutput
from app.application.ports.password import IPasswordService
from app.application.ports.token import ITokenService
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.user_repository import UserRepository


class LoginUseCase:
    """Use case đăng nhập — validate password và issue JWT."""

    def __init__(
        self,
        user_repo: UserRepository,
        password_service: IPasswordService,
        token_service: ITokenService,
    ) -> None:
        self.user_repo = user_repo
        self.password_service = password_service
        self.token_service = token_service

    async def execute(self, data: LoginInput) -> LoginOutput:
        user = await self.user_repo.find_by_email(data.email)
        if user is None:
            raise ResourceNotFound("User not found")
        if not user.is_active:
            raise PermissionDenied("User is inactive")
        if user.hashed_password is None:
            raise ResourceNotFound("User credentials not found")
        if not self.password_service.verify(data.password, user.hashed_password):
            raise PermissionDenied("Invalid credentials")

        access_token = self.token_service.create_access_token(
            subject=str(user.id),
            claims={
                "role_name": user.role_name,
                "permissions": list(user.permissions),
            },
        )
        return LoginOutput(access_token=access_token)
