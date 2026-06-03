from app.application.dtos.user import UserOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.rbac_service import RBACService


class ListUsersUseCase:
    """Use case liệt kê user theo scope của actor."""

    def __init__(self, user_repo: UserRepository, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User) -> list[UserOutput]:
        try:
            self.rbac_service.require_permission(actor, "manage_org")
        except PermissionError:
            raise PermissionDenied("You do not have permission to list users")

        # admin / manage_org → toàn bộ
        users = await self.user_repo.find_all()
        return [UserOutput.from_entity(u) for u in users]
