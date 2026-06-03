from fastapi import APIRouter, Depends

from app.presentation.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/api/v1/audit_logs", tags=["audit_logs"])


@router.get("/")
async def list_audit_logs(actor=Depends(get_current_user)):
    # Placeholder: requires AuditLogRepository integration
    return []
