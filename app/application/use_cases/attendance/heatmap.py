from app.application.dtos.attendance import AttendanceOutput, HeatmapFilterInput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.attendance_repository import AttendanceRepository
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


class GetHeatmapUseCase:
    """Use case lấy dữ liệu chấm công (heatmap) theo scope của actor."""

    def __init__(
        self,
        attendance_repo: AttendanceRepository,
        dept_repo: DepartmentRepository,
        rbac_service: RBACService,
        dept_tree_service: DepartmentTreeService,
    ) -> None:
        self.attendance_repo = attendance_repo
        self.dept_repo = dept_repo
        self.rbac_service = rbac_service
        self.dept_tree_service = dept_tree_service

    async def execute(self, actor: User, filters: HeatmapFilterInput) -> list[AttendanceOutput]:
        scope = self.rbac_service.get_attendance_scope(actor)

        if scope == "all":
            records = await self.attendance_repo.list_by_date_range(
                filters.start_date, filters.end_date
            )
        elif scope == "department" and actor.department_id is not None:
            all_depts = await self.dept_repo.find_all()
            dept_ids = self.dept_tree_service.get_dept_and_descendants(
                actor.department_id, all_depts
            )
            records = await self.attendance_repo.list_by_departments(dept_ids)
        else:
            if filters.user_id is not None and filters.user_id != actor.id:
                raise PermissionDenied("You can only view your own attendance")
            records = await self.attendance_repo.list_by_user(actor.id)

        return [AttendanceOutput.from_entity(r) for r in records]
