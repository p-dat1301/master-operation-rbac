from app.application.dtos.user import UserOutput
from app.domain.exceptions import ResourceNotFound
from app.domain.repositories.user_repository import UserRepository


class GetMeUseCase:
    """Use case lấy thông tin user hiện tại."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: int) -> UserOutput:
        user = await self.user_repo.find_by_id(user_id)
        if user is None:
            raise ResourceNotFound("User not found")
        return UserOutput.from_entity(user)
