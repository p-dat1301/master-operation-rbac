# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends

from app.presentation.schemas.audit_log_schema import AuditLogResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.audit_logs import provide_list_audit_logs

router = APIRouter(prefix="/api/v1/audit_logs", tags=["audit_logs"])


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_list_audit_logs(db)
    dtos = await use_case.execute(actor)
    return dtos
