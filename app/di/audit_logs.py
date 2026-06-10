from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.audit_log.list_audit_logs import ListAuditLogsUseCase
from app.domain.services.rbac_service import RBACService


def provide_list_audit_logs(db: AsyncSession) -> ListAuditLogsUseCase:
    from app.infrastructure.database.repositories.sqlalchemy_audit_log_repo import SQLAlchemyAuditLogRepository

    audit_log_repo = SQLAlchemyAuditLogRepository(db)
    rbac = RBACService()
    return ListAuditLogsUseCase(audit_log_repo=audit_log_repo, rbac_service=rbac)
