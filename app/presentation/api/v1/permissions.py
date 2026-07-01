# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Path

from app.presentation.schemas.permission_schema import PermissionCreateRequest, PermissionResponse, PermissionUpdateRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.permissions import provide_create_permission, provide_delete_permission, provide_list_permissions, provide_update_permission

router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])


@router.get("/", response_model=list[PermissionResponse])
async def list_permissions(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_list_permissions(db)
    dtos = await use_case.execute()
    return dtos


@router.post("/", response_model=PermissionResponse)
async def create_permission(data: PermissionCreateRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_create_permission(db)
    dto = await use_case.execute(actor, data.code, data.description)
    return dto


@router.put("/{id}", response_model=PermissionResponse)
async def update_permission(data: PermissionUpdateRequest, id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_update_permission(db)
    dto = await use_case.execute(actor, id, data.code, data.description)
    return dto


@router.delete("/{id}")
async def delete_permission(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_delete_permission(db)
    await use_case.execute(actor, id)
    return {"detail": "Permission deleted"}
