from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.use_cases.admin_config.menu_sync import MenuSyncValidationError
from app.di.menu_sync import provide_menu_sync
from app.presentation.dependencies.auth_deps import get_current_user
from app.presentation.dependencies.db_deps import get_db
from app.presentation.schemas.menu_sync_schema import MenuSyncRequest, MenuSyncResponse
from app.presentation.api.v1.sync_runtime import maybe_delay_for_sync_test, sync_execution_registry

router = APIRouter(prefix="/api/v1/admin/config", tags=["admin-config"])


@router.post("/menu/sync", response_model=MenuSyncResponse)
async def sync_menu(data: MenuSyncRequest | None = None, actor=Depends(get_current_user), db=Depends(get_db)):
    dry_run = data.dry_run if data else False
    entered = await sync_execution_registry.try_enter('menu')
    if not entered:
        response = MenuSyncResponse(resource='menu', created=0, updated=0, skipped=0, errors=['sync already in progress'], dry_run=dry_run)
        return JSONResponse(status_code=409, content=response.dict())

    use_case = provide_menu_sync(db)
    try:
        await maybe_delay_for_sync_test()
        dto = await use_case.execute(actor, dry_run=dry_run)
    except MenuSyncValidationError as exc:
        response = MenuSyncResponse(**exc.summary.dict())
        return JSONResponse(status_code=400, content=response.dict())
    finally:
        await sync_execution_registry.exit('menu')
    return dto
