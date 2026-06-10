from app.application.dtos.user import UserOutput
from app.domain.entities.user import User
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.rbac_service import RBACService


class GetUserUseCase:
    """Use case lấy thông tin user theo ID — yêu cầu manage_org hoặc xem chính mình."""

    def __init__(self, user_repo: UserRepository, rbac_service: RBACService) -> None:
        self.user_repo = user_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User, user_id: int) -> UserOutput:
        # User can always view themselves
        if actor.id != user_id:
            self.rbac_service.require_permission(actor, "manage_org")

        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found")
        return UserOutput.from_entity(user)
