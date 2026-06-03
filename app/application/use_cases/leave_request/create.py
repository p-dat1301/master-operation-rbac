from app.application.dtos.leave_request import LeaveRequestCreateInput, LeaveRequestOutput
from app.domain.entities.leave_request import LeaveRequest
from app.domain.entities.user import User
from app.domain.repositories.leave_request_repository import LeaveRequestRepository


class CreateLeaveRequestUseCase:
    """Use case tạo đơn xin nghỉ."""

    def __init__(self, leave_repo: LeaveRequestRepository) -> None:
        self.leave_repo = leave_repo

    async def execute(self, actor: User, data: LeaveRequestCreateInput) -> LeaveRequestOutput:
        leave_entity = LeaveRequest(
            id=0,
            requester_id=actor.id,
            leave_type=data.leave_type,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            status="pending",
            department_id=actor.department_id,
        )
        created = await self.leave_repo.create(leave_entity)
        return LeaveRequestOutput.from_entity(created)
