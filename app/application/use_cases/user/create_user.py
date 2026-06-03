from app.application.dtos.user import UserCreateInput, UserOutput
from app.application.ports.password import IPasswordService
from app.domain.entities.user import User
from app.domain.exceptions import BusinessRuleViolation, PermissionDenied, ResourceNotFound
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.rbac_service import RBACService


class CreateUserUseCase:
    """Use case tạo user mới — yêu cầu quyền manage_org."""

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        password_service: IPasswordService,
        rbac_service: RBACService,
    ) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.password_service = password_service
        self.rbac_service = rbac_service

    async def execute(self, actor: User, data: UserCreateInput) -> UserOutput:
        try:
            self.rbac_service.require_permission(actor, "manage_org")
        except PermissionError:
            raise PermissionDenied("You do not have permission to create users")

        role = await self.role_repo.find_by_name(data.role_name)
        if role is None:
            raise ResourceNotFound(f"Role '{data.role_name}' not found")

        existing = await self.user_repo.find_by_email(data.email)
        if existing is not None:
            raise BusinessRuleViolation("Email already exists")

        hashed = self.password_service.hash(data.password)

        user_entity = User(
            id=0,  # sẽ được DB gán
            employee_code=data.employee_code,
            email=data.email,
            full_name=data.full_name,
            role_name=role.name,
            role_id=role.id,
            phone=data.phone,
            job_title=data.job_title,
            contact_type=data.contact_type,
            department_id=data.department_id,
            manager_id=data.manager_id,
            hire_date=data.hire_date,
            is_active=data.is_active,
        )

        created = await self.user_repo.create(user_entity, hashed_password=hashed)
        return UserOutput.from_entity(created)
