from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

import pytest

from app.domain.entities.document import (
    Document,
    DocumentClassification,
    DocumentStatus,
    DocumentVisibility,
)
from app.domain.entities.user import User
from app.domain.exceptions import PermissionDenied
from app.domain.services.department_tree import DepartmentTreeService
from app.domain.services.rbac_service import RBACService


DOCUMENT_PERMISSIONS = {
    "view_document",
    "search_document",
    "update_document",
    "delete_document",
}

DEPARTMENTS = {
    1: "Engineering",
    2: "HR Parent",
    3: "HR Child",
}


def make_user(
    role_name: str,
    permissions: set[str],
    is_active: bool = True,
    user_id: int = 1,
    department_id: int | None = 1,
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


def make_employee_actor(department_id: int = 1, *, user_id: int = 10) -> User:
    return make_user(
        "employee",
        DOCUMENT_PERMISSIONS,
        user_id=user_id,
        department_id=department_id,
    )


def make_manager_actor(department_id: int = 1, *, user_id: int = 20) -> User:
    return make_user(
        "manager",
        DOCUMENT_PERMISSIONS,
        user_id=user_id,
        department_id=department_id,
    )


def make_admin_actor(department_id: int | None = None, *, user_id: int = 30) -> User:
    return make_user(
        "admin",
        set(),
        user_id=user_id,
        department_id=department_id,
    )


def make_bod_actor(department_id: int | None = None, *, user_id: int = 40) -> User:
    return make_user(
        "bod",
        DOCUMENT_PERMISSIONS,
        user_id=user_id,
        department_id=department_id,
    )


def make_inactive_actor(department_id: int = 1, *, user_id: int = 50) -> User:
    return make_user(
        "manager",
        DOCUMENT_PERMISSIONS,
        is_active=False,
        user_id=user_id,
        department_id=department_id,
    )


def make_document_entity(
    *,
    document_id: int,
    department_id: int,
    title: str | None = None,
    uploaded_by: int = 99,
) -> Document:
    now = datetime.now(timezone.utc)
    return Document(
        id=document_id,
        title=title or f"{DEPARTMENTS[department_id]} Document",
        store_bucket="test-bucket",
        store_object_key=f"documents/{document_id}.pdf",
        path_filename=f"document-{document_id}.pdf",
        size_byte=1024,
        status=DocumentStatus.UPLOADED,
        uploaded_by=uploaded_by,
        visibility_scope=DocumentVisibility.DEPARTMENT,
        class_document=DocumentClassification.INTERNAL,
        description=f"Fixture document for dept {department_id}",
        created_at=now,
        updated_at=now,
        allowed_role_names=set(),
        allowed_departments={department_id},
    )


@pytest.fixture
def rbac_service() -> RBACService:
    return RBACService()


@pytest.fixture
def dept_tree_service() -> DepartmentTreeService:
    return DepartmentTreeService()


@pytest.fixture
def documents() -> dict[str, Document]:
    return {
        "engineering": make_document_entity(document_id=1, department_id=1),
        "hr_parent": make_document_entity(document_id=2, department_id=2),
        "hr_child": make_document_entity(document_id=3, department_id=3),
    }


@pytest.fixture
def descendant_map() -> dict[int, set[int]]:
    # department_id=1 (Engineering) is mocked as parent of HR Child for manager descendant coverage.
    return {1: {1, 3}, 2: {2}, 3: {3}}


ACTION_TO_PERMISSION = {
    "list": "view_document",
    "detail": "view_document",
    "search": "search_document",
    "update": "update_document",
    "delete": "delete_document",
}


def assert_document_access(
    *,
    actor: User,
    document: Document,
    action: str,
    rbac_service: RBACService,
    descendant_map: dict[int, set[int]],
) -> None:
    rbac_service.require_permission(actor, ACTION_TO_PERMISSION[action])

    if actor.role_name in {"admin", "bod"}:
        return

    scope = rbac_service.get_document_scope(actor)
    if scope == "all":
        return

    actor_department_id = actor.department_id
    document_department_ids = document.allowed_departments
    if actor_department_id is None:
        raise PermissionDenied("Document access requires actor department")

    if scope == "department":
        visible_department_ids = descendant_map.get(actor_department_id, {actor_department_id})
    else:
        visible_department_ids = {actor_department_id}

    if document_department_ids.isdisjoint(visible_department_ids):
        raise PermissionDenied("Document is outside actor scope")


def visible_document_ids(
    *,
    actor: User,
    documents: list[Document],
    action: str,
    rbac_service: RBACService,
    descendant_map: dict[int, set[int]],
) -> list[int]:
    result: list[int] = []
    for document in documents:
        try:
            assert_document_access(
                actor=actor,
                document=document,
                action=action,
                rbac_service=rbac_service,
                descendant_map=descendant_map,
            )
        except PermissionDenied:
            continue
        result.append(document.id)
    return result


ScenarioFactory = Callable[[dict[str, Document]], tuple[User, Document, bool]]


def _employee_same_dept(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_employee_actor(department_id=1), docs["engineering"], True


def _employee_other_dept(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_employee_actor(department_id=1), docs["hr_parent"], False


def _manager_own_dept(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_manager_actor(department_id=1), docs["engineering"], True


def _manager_descendant_dept(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_manager_actor(department_id=1), docs["hr_child"], True


def _manager_unrelated_dept(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_manager_actor(department_id=1), docs["hr_parent"], False


def _admin_all(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_admin_actor(), docs["hr_parent"], True


def _bod_all(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_bod_actor(), docs["hr_child"], True


def _inactive_denied(docs: dict[str, Document]) -> tuple[User, Document, bool]:
    return make_inactive_actor(department_id=1), docs["engineering"], False


SCENARIOS: list[tuple[str, ScenarioFactory]] = [
    ("employee same dept allow", _employee_same_dept),
    ("employee other dept deny", _employee_other_dept),
    ("manager own dept allow", _manager_own_dept),
    ("manager descendant dept allow", _manager_descendant_dept),
    ("manager unrelated dept deny", _manager_unrelated_dept),
    ("admin allow all", _admin_all),
    ("bod allow all", _bod_all),
    ("inactive deny all", _inactive_denied),
]


class TestDocumentRBACMatrix:
    @pytest.mark.parametrize("action", ["list", "detail", "search", "update", "delete"])
    @pytest.mark.parametrize("scenario_name,scenario_factory", SCENARIOS, ids=[name for name, _ in SCENARIOS])
    def test_document_action_scope_matrix(
        self,
        action: str,
        scenario_name: str,
        scenario_factory: ScenarioFactory,
        documents: dict[str, Document],
        rbac_service: RBACService,
        descendant_map: dict[int, set[int]],
    ):
        actor, document, should_allow = scenario_factory(documents)

        if should_allow:
            assert_document_access(
                actor=actor,
                document=document,
                action=action,
                rbac_service=rbac_service,
                descendant_map=descendant_map,
            )
        else:
            with pytest.raises(PermissionDenied):
                assert_document_access(
                    actor=actor,
                    document=document,
                    action=action,
                    rbac_service=rbac_service,
                    descendant_map=descendant_map,
                )

    @pytest.mark.parametrize(
        "actor,expected_ids",
        [
            (make_employee_actor(department_id=1), [1]),
            (make_manager_actor(department_id=1), [1, 3]),
            (make_admin_actor(), [1, 2, 3]),
            (make_bod_actor(), [1, 2, 3]),
            (make_inactive_actor(department_id=1), []),
        ],
        ids=["employee", "manager", "admin", "bod", "inactive"],
    )
    def test_list_search_detail_use_same_scope(
        self,
        actor: User,
        expected_ids: list[int],
        documents: dict[str, Document],
        rbac_service: RBACService,
        descendant_map: dict[int, set[int]],
    ):
        all_documents = list(documents.values())

        list_ids = visible_document_ids(
            actor=actor,
            documents=all_documents,
            action="list",
            rbac_service=rbac_service,
            descendant_map=descendant_map,
        )
        search_ids = visible_document_ids(
            actor=actor,
            documents=all_documents,
            action="search",
            rbac_service=rbac_service,
            descendant_map=descendant_map,
        )
        detail_ids = visible_document_ids(
            actor=actor,
            documents=all_documents,
            action="detail",
            rbac_service=rbac_service,
            descendant_map=descendant_map,
        )

        assert list_ids == expected_ids
        assert search_ids == list_ids
        assert detail_ids == list_ids
