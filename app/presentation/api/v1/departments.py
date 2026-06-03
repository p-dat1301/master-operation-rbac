from fastapi import APIRouter, Depends

from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.infrastructure.database.repositories.sqlalchemy_department_repo import SQLAlchemyDepartmentRepository

router = APIRouter(prefix="/api/v1/departments", tags=["departments"])


@router.get("/")
async def list_departments(db=Depends(get_db), actor=Depends(get_current_user)):
    repo = SQLAlchemyDepartmentRepository(db)
    depts = await repo.find_all()
    return [d.__dict__ for d in depts]
