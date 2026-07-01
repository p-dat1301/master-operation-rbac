from __future__ import annotations

from typing import Literal

from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.department_tree import DepartmentTreeService


AttendanceScope = Literal["all", "department", "self"]
TaskScope = Literal["all", "department", "self"]
LeaveRequestScope = Literal["all", "department", "self"]
DocumentScope = Literal["all", "department", "self"]
DocumentScopeDepartmentTreeService = DepartmentTreeService

# Vai trò đặc biệt được coi là "super-admin" — bỏ qua kiểm tra permission_code.
_SUPERADMIN_ROLES: frozenset[str] = frozenset({"admin"})


class RBACService:
    """Pure synchronous domain service — kiểm tra quyền từ actor.permissions.

    Không có I/O, không có DB, không có ORM.
    Tập quyền ``actor.permissions`` đã được Eager-Load tại Repository trước
    khi Use Case được gọi (Passport / Rich Domain Entity pattern).

    Độ phức tạp kiểm tra: O(1) — set membership lookup trên RAM.
    """

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def has_permission(self, actor: User, permission_code: str) -> bool:
        """Trả về ``True`` nếu actor có quyền ``permission_code``.

        Quy tắc:
        1. Tài khoản bị khoá (``is_active=False``) → luôn từ chối.
        2. Vai trò ``admin`` → luôn chấp nhận (super-admin bypass).
        3. Các vai trò còn lại → kiểm tra membership trong ``actor.permissions``.
        """
        if not actor.is_active:
            return False
        if actor.role_name in _SUPERADMIN_ROLES:
            return True
        return permission_code in actor.permissions

    def require_permission(self, actor: User, permission_code: str) -> None:
        """Raise ``PermissionDenied`` nếu actor không có quyền.

        Tiện ích để Use Case gọi trực tiếp thay vì ``if not has_permission``.
        """
        if not self.has_permission(actor, permission_code):
            raise PermissionDenied(
                f"Role '{actor.role_name}' lacks permission '{permission_code}'."
            )

    def list_permissions(self, actor: User) -> set[str]:
        """Trả về tập quyền hiện tại của actor (copy, không mutate)."""
        if actor.role_name in _SUPERADMIN_ROLES:
            # admin bypass — trả về set của chính actor; caller không cần
            # biết toàn bộ permission universe.
            return set(actor.permissions)
        return set(actor.permissions)

    # ------------------------------------------------------------------
    # Scope helpers
    # ------------------------------------------------------------------

    def get_task_scope(self, actor: User) -> TaskScope:
        """Phạm vi task được phép thao tác."""
        if actor.role_name in ("admin", "bod"):
            return "all"
        if actor.role_name == "manager":
            return "department"
        return "self"

    def get_leave_request_scope(self, actor: User) -> LeaveRequestScope:
        """Phạm vi đơn xin nghỉ được phép xem."""
        if actor.role_name in ("admin", "bod"):
            return "all"
        if self.has_permission(actor, "approve_leave"):
            return "department"
        return "self"

    def get_attendance_scope(self, actor: User) -> AttendanceScope:
        """Phạm vi dữ liệu chấm công được phép xem."""
        if self.has_permission(actor, "view_attendance_all"):
            return "all"
        if self.has_permission(actor, "view_attendance_dept"):
            return "department"
        return "self"

    def get_document_scope(self, actor: User) -> DocumentScope:
        """Phạm vi tài liệu được phép thao tác.

        Manager trả về ``department``; use case layer sẽ dùng
        ``DepartmentTreeService.get_dept_and_descendants`` để mở rộng cây phòng ban.
        """
        if actor.role_name in ("admin", "bod"):
            return "all"
        if actor.role_name == "manager":
            return "department"
        return "self"

    # ------------------------------------------------------------------
    # Composite business rule
    # ------------------------------------------------------------------

    def can_approve_leave_for(
        self,
        actor: User,
        is_ancestor: bool,
    ) -> bool:
        """Kiểm tra actor có thể duyệt đơn xin nghỉ của requester không.

        - Phải có permission ``approve_leave``.
        - ``admin`` / ``bod``: luôn True (nếu có permission — admin bypass).
        - ``manager``: True khi phòng ban của requester nằm trong nhánh
          quản lý của actor (``is_ancestor=True``).
        - ``employee``: False.
        """
        if not self.has_permission(actor, "approve_leave"):
            return False
        if actor.role_name in ("admin", "bod"):
            return True
        return is_ancestor
