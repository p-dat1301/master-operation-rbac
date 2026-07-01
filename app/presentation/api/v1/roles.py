# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Path

from app.presentation.schemas.role_schema import RoleCreateRequest, RoleResponse, RoleUpdateRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.roles import provide_create_role, provide_delete_role, provide_list_roles, provide_update_role

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("/", response_model=list[RoleResponse])
async def list_roles(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_list_roles(db)
    dtos = await use_case.execute()
    return [RoleResponse.from_dto(d) for d in dtos]


@router.post("/", response_model=RoleResponse)
async def create_role(data: RoleCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_create_role(db)
    dto = await use_case.execute(actor, data.name, data.display_name)
    return RoleResponse.from_dto(dto)


@router.put("/{id}", response_model=RoleResponse)
async def update_role(data: RoleUpdateRequest, id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_update_role(db)
    dto = await use_case.execute(actor, id, data.name, data.display_name)
    return RoleResponse.from_dto(dto)


@router.delete("/{id}")
async def delete_role(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_delete_role(db)
    await use_case.execute(actor, id)
    return {"detail": "Role deleted"}
