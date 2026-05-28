"""Unit tests cho RBACService — Pure Synchronous Domain Service.

Không cần DB, không cần asyncio, không mock.
Chỉ khởi tạo User mock với permissions set giả lập → test O(1) logic.
"""
import pytest
from app.domain.entities.user import User
from app.domain.services.rbac_service import RBACService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc() -> RBACService:
    return RBACService()


def make_user(
    role_name: str,
    permissions: set[str],
    is_active: bool = True,
    user_id: int = 1,
    department_id: int = 1,
) -> User:
    """Factory helper: tạo User mock không cần DB."""
    return User(
        id=user_id,
        employee_code=f"EMP{user_id:04d}",
        email=f"user{user_id}@example.com",
        full_name=f"User {user_id}",
        role_name=role_name,
        permissions=permissions,
        department_id=department_id,
        is_active=is_active,
    )


# ---------------------------------------------------------------------------
# Test: has_permission
# ---------------------------------------------------------------------------

class TestHasPermission:
    def test_active_user_with_permission(self, svc):
        user = make_user("manager", {"approve_leave", "view_personnel"})
        assert svc.has_permission(user, "approve_leave") is True

    def test_active_user_without_permission(self, svc):
        user = make_user("employee", {"view_attendance_self"})
        assert svc.has_permission(user, "approve_leave") is False

    def test_inactive_user_denied_always(self, svc):
        """Tài khoản bị khoá không được phép dù có permission trong set."""
        user = make_user("manager", {"approve_leave"}, is_active=False)
        assert svc.has_permission(user, "approve_leave") is False

    def test_admin_bypass_without_explicit_permission(self, svc):
        """admin không cần khai báo permission cụ thể — super-admin bypass."""
        admin = make_user("admin", set())  # set rỗng
        assert svc.has_permission(admin, "manage_org") is True
        assert svc.has_permission(admin, "view_audit_log") is True
        assert svc.has_permission(admin, "any_future_permission") is True

    def test_admin_inactive_still_denied(self, svc):
        admin = make_user("admin", set(), is_active=False)
        assert svc.has_permission(admin, "manage_org") is False

    def test_unknown_role_with_matching_permission(self, svc):
        """Role không nằm trong danh sách hardcode nhưng DB cấp quyền vẫn pass."""
        user = make_user("custom_role", {"report:read"})
        assert svc.has_permission(user, "report:read") is True

    def test_empty_permissions(self, svc):
        user = make_user("employee", set())
        assert svc.has_permission(user, "view_personnel") is False


# ---------------------------------------------------------------------------
# Test: require_permission
# ---------------------------------------------------------------------------

class TestRequirePermission:
    def test_raises_on_missing(self, svc):
        user = make_user("employee", {"view_attendance_self"})
        with pytest.raises(PermissionError, match="approve_leave"):
            svc.require_permission(user, "approve_leave")

    def test_no_raise_on_present(self, svc):
        user = make_user("manager", {"approve_leave"})
        svc.require_permission(user, "approve_leave")  # không raise


# ---------------------------------------------------------------------------
# Test: get_attendance_scope
# ---------------------------------------------------------------------------

class TestAttendanceScope:
    def test_admin_all(self, svc):
        admin = make_user("admin", set())
        assert svc.get_attendance_scope(admin) == "all"

    def test_manager_department(self, svc):
        manager = make_user("manager", {"view_attendance_dept", "view_attendance_self"})
        assert svc.get_attendance_scope(manager) == "department"

    def test_employee_self(self, svc):
        emp = make_user("employee", {"view_attendance_self"})
        assert svc.get_attendance_scope(emp) == "self"

    def test_bod_all(self, svc):
        bod = make_user("bod", {"view_attendance_all", "view_attendance_dept", "view_attendance_self"})
        assert svc.get_attendance_scope(bod) == "all"


# ---------------------------------------------------------------------------
# Test: can_approve_leave_for
# ---------------------------------------------------------------------------

class TestCanApproveLeavFor:
    def test_manager_can_approve_subordinate(self, svc):
        manager = make_user("manager", {"approve_leave"})
        assert svc.can_approve_leave_for(manager, is_ancestor=True) is True

    def test_manager_cannot_approve_outside_scope(self, svc):
        manager = make_user("manager", {"approve_leave"})
        assert svc.can_approve_leave_for(manager, is_ancestor=False) is False

    def test_bod_can_approve_any(self, svc):
        bod = make_user("bod", {"approve_leave"})
        assert svc.can_approve_leave_for(bod, is_ancestor=False) is True

    def test_employee_cannot_approve(self, svc):
        emp = make_user("employee", {"view_attendance_self"})
        assert svc.can_approve_leave_for(emp, is_ancestor=True) is False

    def test_admin_bypass_approve(self, svc):
        admin = make_user("admin", set())
        assert svc.can_approve_leave_for(admin, is_ancestor=False) is True
