import pytest

from app.agentic.contracts.access_policy import Classification, VisibilityScope
from app.domain.entities.department import Department
from app.domain.entities.document import Document, DocumentClassification, DocumentStatus, DocumentVisibility
from app.domain.entities.user import User
from app.domain.services.document_access_policy import build_document_policy, evaluate_document_access


def make_user(
    role_name: str,
    *,
    is_active: bool = True,
    user_id: int = 1,
    department_id: int | None = 1,
) -> User:
    return User(
        id=user_id,
        employee_code=f"EMP{user_id:04d}",
        email=f"user{user_id}@example.com",
        full_name=f"User {user_id}",
        role_name=role_name,
        permissions=set(),
        department_id=department_id,
        is_active=is_active,
    )


def make_document(
    *,
    visibility_scope: DocumentVisibility,
    allowed_departments: set[int] | None = None,
    allowed_role_names: set[str] | None = None,
    uploaded_by: int = 99,
    classification: DocumentClassification = DocumentClassification.INTERNAL,
) -> Document:
    return Document(
        id=1,
        title="Policy",
        store_bucket="bucket",
        store_object_key="object",
        path_filename="policy.pdf",
        size_byte=128,
        status=DocumentStatus.UPLOADED,
        uploaded_by=uploaded_by,
        visibility_scope=visibility_scope,
        class_document=classification,
        allowed_role_names=allowed_role_names or set(),
        allowed_departments=allowed_departments or set(),
    )


@pytest.fixture
def departments() -> list[Department]:
    return [
        Department(id=1, name="Company", level=1),
        Department(id=2, name="Division A", level=2, parent_id=1),
        Department(id=3, name="Division B", level=2, parent_id=1),
        Department(id=4, name="Team A1", level=3, parent_id=2),
    ]


class TestBuildDocumentPolicy:
    def test_maps_document_fields_to_access_policy_metadata(self):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={4, 2},
            allowed_role_names={"employee", "manager"},
            uploaded_by=7,
            classification=DocumentClassification.CONFIDENTIAL,
        )

        policy = build_document_policy(document)

        assert policy.classification is Classification.CONFIDENTIAL
        assert policy.visibility_scope is VisibilityScope.DEPARTMENT
        assert policy.allowed_roles == ("employee", "manager")
        assert policy.department_id == 2
        assert policy.owner_id == 7
        assert policy.policy_version == "access-policy-v1"


class TestEvaluateDocumentAccess:
    def test_employee_same_department_allowed(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={2},
        )
        actor = make_user("employee", department_id=2)

        assert evaluate_document_access(document, actor, departments) is True

    def test_employee_other_department_denied(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={2},
        )
        actor = make_user("employee", department_id=3)

        assert evaluate_document_access(document, actor, departments) is False

    def test_manager_own_department_allowed(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={2},
        )
        actor = make_user("manager", department_id=2)

        assert evaluate_document_access(document, actor, departments) is True

    def test_manager_descendant_department_allowed(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={4},
        )
        actor = make_user("manager", department_id=2)

        assert evaluate_document_access(document, actor, departments) is True

    def test_manager_unrelated_department_denied(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={3},
        )
        actor = make_user("manager", department_id=2)

        assert evaluate_document_access(document, actor, departments) is False

    def test_admin_always_allowed(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.ROLE,
            allowed_role_names={"employee"},
        )
        actor = make_user("admin", department_id=3)

        assert evaluate_document_access(document, actor, departments) is True

    def test_bod_always_allowed(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.OWNER,
            uploaded_by=999,
        )
        actor = make_user("bod", department_id=3)

        assert evaluate_document_access(document, actor, departments) is True

    def test_inactive_user_denied(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.DEPARTMENT,
            allowed_departments={2},
        )
        actor = make_user("admin", is_active=False, department_id=2)

        assert evaluate_document_access(document, actor, departments) is False

    def test_manager_subtree_scope_allowed_for_manager(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.MANAGER_SUBTREE,
            allowed_departments={4},
        )
        actor = make_user("manager", department_id=2)

        assert evaluate_document_access(document, actor, departments) is True

    def test_manager_subtree_scope_denied_for_employee(self, departments):
        document = make_document(
            visibility_scope=DocumentVisibility.MANAGER_SUBTREE,
            allowed_departments={4},
        )
        actor = make_user("employee", department_id=4)

        assert evaluate_document_access(document, actor, departments) is False
