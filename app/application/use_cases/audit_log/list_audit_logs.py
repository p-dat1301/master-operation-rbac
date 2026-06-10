from app.application.dtos.audit_log import AuditLogOutput
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.repositories.audit_log_repository import AuditLogRepository
from app.domain.services.rbac_service import RBACService


class ListAuditLogsUseCase:
    """Use case lấy audit logs — chỉ admin/member mới có quyền xem."""

    def __init__(
        self,
        audit_log_repo: AuditLogRepository,
        rbac_service: RBACService,
    ) -> None:
        self.audit_log_repo = audit_log_repo
        self.rbac_service = rbac_service

    async def execute(self, actor: User) -> list[AuditLogOutput]:
        if not self.rbac_service.has_permission(actor, "view_audit_logs"):
            raise PermissionDenied("You do not have permission to view audit logs")

        records = await self.audit_log_repo.list_recent(limit=100)
        return [AuditLogOutput.from_entity(r) for r in records]
