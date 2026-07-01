"""SQLAlchemy ORM models package.

Tất cả models được import tại đây để Alembic autogenerate có thể phát hiện
đầy đủ schema khi chạy ``alembic revision --autogenerate``.
"""
from app.infrastructure.database.models.role_model import RoleModel
from app.infrastructure.database.models.permission_model import PermissionModel
from app.infrastructure.database.models.role_permission_model import RolePermissionModel
from app.infrastructure.database.models.department_model import DepartmentModel
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.task_model import TaskModel
from app.infrastructure.database.models.leave_request_model import LeaveRequestModel
from app.infrastructure.database.models.leave_balance_model import LeaveBalanceModel
from app.infrastructure.database.models.attendance_model import AttendanceModel
from app.infrastructure.database.models.notification_model import NotificationModel
from app.infrastructure.database.models.audit_log_model import AuditLogModel
from app.infrastructure.database.models.menu_model import MenuModel
from app.infrastructure.database.models.translation_model import TranslationModel
from app.infrastructure.database.models.document_model import DocumentModel
from app.agentic.adapters.storage.models import (
    AgenticChunkEmbeddingModel,
    AgenticChunkModel,
    AgenticDocumentModel,
    RagConversationModel,
    RagTurnModel,
)

__all__ = [
    "RoleModel",
    "PermissionModel",
    "RolePermissionModel",
    "DepartmentModel",
    "UserModel",
    "TaskModel",
    "LeaveRequestModel",
    "LeaveBalanceModel",
    "AttendanceModel",
    "NotificationModel",
    "AuditLogModel",
    "MenuModel",
    "TranslationModel",
    "DocumentModel",
    "AgenticDocumentModel",
    "AgenticChunkModel",
    "AgenticChunkEmbeddingModel",
    "RagConversationModel",
    "RagTurnModel",
]

