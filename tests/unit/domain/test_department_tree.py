from app.domain.entities.department import Department
from app.domain.services.department_tree import DepartmentTreeService


def make_depts():
    # L1 company
    return [
        Department(id=1, name="Company", level=1, parent_id=None),
        Department(id=2, name="Division A", level=2, parent_id=1),
        Department(id=3, name="Division B", level=2, parent_id=1),
        Department(id=4, name="Team X", level=3, parent_id=2),
        Department(id=5, name="Team Y", level=3, parent_id=2),
        Department(id=6, name="Group 1", level=4, parent_id=4),
    ]


def test_get_descendants_and_is_ancestor():
    depts = make_depts()
    svc = DepartmentTreeService()

    desc_div_a = svc.get_descendants(2, depts)
    assert {4, 5, 6}.issubset(desc_div_a)

    assert svc.is_ancestor_of(2, 6, depts)
    assert not svc.is_ancestor_of(4, 2, depts)


def test_get_path_to_root_and_get_dept_and_descendants():
    depts = make_depts()
    svc = DepartmentTreeService()

    path = svc.get_path_to_root(6, depts)
    assert path[0] == 6 and path[-1] == 1

    group_and_desc = svc.get_dept_and_descendants(4, depts)
    assert {4, 6} == group_and_desc
