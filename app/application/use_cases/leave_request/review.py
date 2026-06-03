from app.application.dtos.leave_request import LeaveRequestOutput, ReviewLeaveRequestInput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied, ResourceNotFound
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.repositories.leave_request_repository import LeaveRequestRepository
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService
from app.application.ports.notification import INotificationService


class ReviewLeaveRequestUseCase:
    """Use case duyệt / từ chối đơn xin nghỉ — có kiểm tra department scope."""

    def __init__(
        self,
        leave_repo: LeaveRequestRepository,
        dept_repo: DepartmentRepository,
        rbac_service: RBACService,
        dept_tree_service: DepartmentTreeService,
        notification_service: INotificationService,
    ) -> None:
        self.leave_repo = leave_repo
        self.dept_repo = dept_repo
        self.rbac_service = rbac_service
        self.dept_tree_service = dept_tree_service
        self.notification_service = notification_service

    async def execute(self, actor: User, data: ReviewLeaveRequestInput) -> LeaveRequestOutput:
        leave = await self.leave_repo.find_by_id(data.leave_request_id)
        if leave is None:
            raise ResourceNotFound("Leave request not found")

        all_depts = await self.dept_repo.find_all()
        is_ancestor = False
        if actor.department_id is not None and leave.department_id is not None:
            is_ancestor = self.dept_tree_service.is_ancestor_of(
                actor.department_id, leave.department_id, all_depts
            )

        if not self.rbac_service.can_approve_leave_for(actor, is_ancestor):
            raise PermissionDenied("You do not have permission to review this leave request")

        new_status = "approved" if data.action == "approve" else "rejected"
        reviewed_by = actor.id

        updated = await self.leave_repo.update_status(
            leave_id=leave.id,
            status=new_status,
            reviewed_by=reviewed_by,
            rejection_reason=data.rejected_reason if new_status == "rejected" else None,
        )

        await self.notification_service.notify_user(
            user_id=leave.requester_id,
            title="Leave Request Update",
            message=f"Your leave request has been {new_status}.",
        )

        return LeaveRequestOutput.from_entity(updated)
