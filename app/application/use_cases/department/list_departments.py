from app.application.dtos.department import DepartmentOutput
from app.domain.repositories.department_repository import DepartmentRepository


class ListDepartmentsUseCase:
    """Use case liệt kê tất cả phòng ban."""

    def __init__(self, dept_repo: DepartmentRepository) -> None:
        self.dept_repo = dept_repo

    async def execute(self) -> list[DepartmentOutput]:
        depts = await self.dept_repo.find_all()
        return [DepartmentOutput.from_entity(d) for d in depts]
