from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.application.use_cases.admin_config.i18n_sync import I18nSyncValidationError
from app.di.i18n_sync import provide_i18n_sync
from app.presentation.api.v1.sync_runtime import maybe_delay_for_sync_test, sync_execution_registry
from app.presentation.dependencies.auth_deps import get_current_user
from app.presentation.dependencies.db_deps import get_db
from app.presentation.schemas.i18n_sync_schema import I18nSyncRequest, I18nSyncResponse

router = APIRouter(prefix="/api/v1/admin/config", tags=["admin-config"])


@router.post("/i18n/sync", response_model=I18nSyncResponse)
async def sync_i18n(data: I18nSyncRequest | None = None, actor=Depends(get_current_user), db=Depends(get_db)):
    dry_run = data.dry_run if data else False
    entered = await sync_execution_registry.try_enter('i18n')
    if not entered:
        response = I18nSyncResponse(resource='i18n', created=0, updated=0, skipped=0, errors=['sync already in progress'], dry_run=dry_run)
        return JSONResponse(status_code=409, content=response.model_dump())

    use_case = provide_i18n_sync(db)
    try:
        await maybe_delay_for_sync_test()
        dto = await use_case.execute(actor, dry_run=dry_run)
    except I18nSyncValidationError as exc:
        response = I18nSyncResponse.from_dto(exc.summary)
        return JSONResponse(status_code=400, content=response.model_dump())
    finally:
        await sync_execution_registry.exit('i18n')
    return I18nSyncResponse.from_dto(dto)
