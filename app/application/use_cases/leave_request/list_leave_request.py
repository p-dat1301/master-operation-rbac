from app.application.dtos.leave_request import LeaveRequestOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.repositories.leave_request_repository import LeaveRequestRepository
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


class ListLeaveRequestsUseCase:
    """Use case liệt kê đơn xin nghỉ theo scope của actor."""

    def __init__(
        self,
        leave_repo: LeaveRequestRepository,
        dept_repo: DepartmentRepository,
        rbac_service: RBACService,
        dept_tree_service: DepartmentTreeService,
    ) -> None:
        self.leave_repo = leave_repo
        self.dept_repo = dept_repo
        self.rbac_service = rbac_service
        self.dept_tree_service = dept_tree_service

    async def execute(self, actor: User) -> list[LeaveRequestOutput]:
        scope = self.rbac_service.get_leave_request_scope(actor)

        if scope == "all":
            leaves = await self.leave_repo.list_all()
        elif scope == "department" and actor.department_id is not None:
            all_depts = await self.dept_repo.find_all()
            dept_ids = self.dept_tree_service.get_dept_and_descendants(
                actor.department_id, all_depts
            )
            leaves = await self.leave_repo.list_by_departments(dept_ids)
        else:
            leaves = await self.leave_repo.list_by_requester(actor.id)

        return [LeaveRequestOutput.from_entity(l) for l in leaves]
