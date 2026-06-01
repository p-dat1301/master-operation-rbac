from app.domain.entities.department import Department
from app.domain.entities.user import User
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


def test_cycle_does_not_infinite_loop_in_descendants_and_path():
    depts = [
        Department(id=1, name="Root", level=1, parent_id=3),
        Department(id=2, name="Branch", level=2, parent_id=1),
        Department(id=3, name="Leaf", level=3, parent_id=2),
    ]

    svc = DepartmentTreeService()

    descendants = svc.get_descendants(1, depts)
    path = svc.get_path_to_root(1, depts)

    assert descendants == {2, 3}
    assert path == [1, 3, 2]


def test_rbac_with_empty_role_and_empty_permissions():
    user = User(
        id=1,
        employee_code="EMP0001",
        email="user@example.com",
        full_name="User One",
        role_name="",
        permissions=set(),
    )

    svc = RBACService()

    assert svc.has_permission(user, "anything") is False
    assert svc.get_attendance_scope(user) == "self"