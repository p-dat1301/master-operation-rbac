# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends

from app.presentation.schemas.department_schema import DepartmentResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.departments import provide_list_departments

router = APIRouter(prefix="/api/v1/departments", tags=["departments"])


@router.get("/", response_model=list[DepartmentResponse])
async def list_departments(db=Depends(get_db), actor=Depends(get_current_user)):
    use_case = provide_list_departments(db)
    dtos = await use_case.execute()
    return dtos
