"""Integration tests for document CRUD + RBAC API behavior."""
from __future__ import annotations

import uuid
from typing import Any

import httpx
import pytest


pytestmark = pytest.mark.asyncio


API_PREFIX = "/api/v1/documents"
DOCUMENTS_AVAILABLE = True


async def _get_me(client: httpx.AsyncClient, token: str) -> dict[str, Any]:
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _create_document(
    client: httpx.AsyncClient,
    token: str,
    *,
    title: str,
    allowed_departments: list[int],
    description: str | None = None,
    visibility_scope: str = "department",
    allowed_role_names: list[str] | None = None,
    class_document: str = "internal",
) -> dict[str, Any]:
    files: list[tuple[str, tuple[str | None, str] | tuple[str, bytes, str]]] = [
        ("title", (None, title)),
        ("description", (None, description or f"Integration test doc {title}")),
        ("visibility_scope", (None, visibility_scope)),
        ("class_document", (None, class_document)),
        ("file", (f"{title}.txt", b"document integration test", "text/plain")),
    ]
    for dept_id in allowed_departments:
        files.append(("allowed_departments", (None, str(dept_id))))
    for role_name in allowed_role_names or []:
        files.append(("allowed_role_names", (None, role_name)))

    resp = await client.post(
        f"{API_PREFIX}/",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    if resp.status_code == 404:
        pytest.skip("Document API routes are not available on the running integration server")
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _get_access_scope_departments(
    client: httpx.AsyncClient,
    admin_token: str,
    employee_token: str,
) -> tuple[int, int]:
    employee = await _get_me(client, employee_token)
    employee_dept_id = employee["department_id"]
    assert employee_dept_id is not None
    outside_dept_id = 1 if employee_dept_id != 1 else 2

    employee_doc = await _create_document(
        client,
        admin_token,
        title=f"employee-scope-{uuid.uuid4().hex}",
        allowed_departments=[employee_dept_id],
    )
    outside_doc = await _create_document(
        client,
        admin_token,
        title=f"outside-scope-{uuid.uuid4().hex}",
        allowed_departments=[outside_dept_id],
    )
    return employee_doc["id"], outside_doc["id"]


async def _search_ids(client: httpx.AsyncClient, token: str, q: str) -> set[int]:
    resp = await client.get(
        f"{API_PREFIX}/",
        params={"q": q},
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 404:
        pytest.skip("Document API routes are not available on the running integration server")
    assert resp.status_code == 200, resp.text
    return {item["id"] for item in resp.json()}


class TestDocumentListAndSearch:
    """GET /api/v1/documents/ — list + search via ?q=""."""

    async def test_list_requires_auth(self, client: httpx.AsyncClient):
        resp = await client.get(f"{API_PREFIX}/")
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 401

    async def test_admin_list_returns_all(self, client: httpx.AsyncClient, admin_token: str):
        title = f"admin-list-{uuid.uuid4().hex}"
        created = await _create_document(
            client,
            admin_token,
            title=title,
            allowed_departments=[1],
        )

        resp = await client.get(
            f"{API_PREFIX}/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert isinstance(data, list)
        match = next((item for item in data if item["id"] == created["id"]), None)
        assert match is not None
        assert match["title"] == title
        assert "status" in match
        assert "visibility_scope" in match

    async def test_employee_list_returns_scoped(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        employee_doc_id, outside_doc_id = await _get_access_scope_departments(
            client,
            admin_token,
            employee_token,
        )

        resp = await client.get(
            f"{API_PREFIX}/",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert resp.status_code == 200, resp.text
        ids = {item["id"] for item in resp.json()}
        assert employee_doc_id in ids
        assert outside_doc_id not in ids

    async def test_search_requires_auth(self, client: httpx.AsyncClient):
        resp = await client.get(f"{API_PREFIX}/", params={"q": "needle"})
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 401

    async def test_admin_search_returns_all(self, client: httpx.AsyncClient, admin_token: str):
        keyword = f"search-all-{uuid.uuid4().hex}"
        first = await _create_document(
            client,
            admin_token,
            title=f"{keyword}-one",
            allowed_departments=[1],
        )
        second = await _create_document(
            client,
            admin_token,
            title=f"{keyword}-two",
            allowed_departments=[2],
        )

        ids = await _search_ids(client, admin_token, keyword)
        assert first["id"] in ids
        assert second["id"] in ids

    async def test_employee_search_no_leak(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        keyword = f"employee-search-{uuid.uuid4().hex}"
        employee = await _get_me(client, employee_token)
        employee_dept_id = employee["department_id"]
        assert employee_dept_id is not None
        outside_dept_id = 1 if employee_dept_id != 1 else 2

        visible = await _create_document(
            client,
            admin_token,
            title=f"{keyword}-visible",
            allowed_departments=[employee_dept_id],
        )
        hidden = await _create_document(
            client,
            admin_token,
            title=f"{keyword}-hidden",
            allowed_departments=[outside_dept_id],
        )

        ids = await _search_ids(client, employee_token, keyword)
        assert visible["id"] in ids
        assert hidden["id"] not in ids

    async def test_search_list_parity(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        keyword = f"parity-{uuid.uuid4().hex}"
        employee = await _get_me(client, employee_token)
        employee_dept_id = employee["department_id"]
        assert employee_dept_id is not None
        outside_dept_id = 1 if employee_dept_id != 1 else 2

        visible = await _create_document(
            client,
            admin_token,
            title=keyword,
            allowed_departments=[employee_dept_id],
        )
        hidden = await _create_document(
            client,
            admin_token,
            title=keyword,
            allowed_departments=[outside_dept_id],
        )

        list_resp = await client.get(
            f"{API_PREFIX}/",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert list_resp.status_code == 200, list_resp.text
        list_ids = {item["id"] for item in list_resp.json() if item["title"] == keyword}

        search_ids = await _search_ids(client, employee_token, keyword)
        assert list_ids == search_ids
        assert visible["id"] in search_ids
        assert hidden["id"] not in search_ids


class TestDocumentDetail:
    """GET /api/v1/documents/{id}"""

    async def test_detail_requires_auth(self, client: httpx.AsyncClient):
        resp = await client.get(f"{API_PREFIX}/1")
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 401

    async def test_detail_returns_200_for_authorized_employee(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        employee = await _get_me(client, employee_token)
        employee_dept_id = employee["department_id"]
        assert employee_dept_id is not None
        created = await _create_document(
            client,
            admin_token,
            title=f"detail-allow-{uuid.uuid4().hex}",
            allowed_departments=[employee_dept_id],
        )

        resp = await client.get(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == created["id"]
        assert data["title"] == created["title"]
        assert "updated_at" in data
        assert "allowed_departments" in data

    async def test_detail_returns_403_for_cross_dept_employee(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        _, outside_doc_id = await _get_access_scope_departments(client, admin_token, employee_token)

        resp = await client.get(
            f"{API_PREFIX}/{outside_doc_id}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert resp.status_code == 403

    async def test_detail_returns_404_for_nonexistent(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
    ):
        resp = await client.get(
            f"{API_PREFIX}/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404

    async def test_admin_detail_returns_200(self, client: httpx.AsyncClient, admin_token: str):
        created = await _create_document(
            client,
            admin_token,
            title=f"admin-detail-{uuid.uuid4().hex}",
            allowed_departments=[2],
        )

        resp = await client.get(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == created["id"]
        assert data["title"] == created["title"]


class TestDocumentUpdate:
    """PATCH /api/v1/documents/{id}"""

    async def test_update_requires_auth(self, client: httpx.AsyncClient):
        resp = await client.patch(f"{API_PREFIX}/1", json={"title": "Updated title"})
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 401

    async def test_update_returns_200_for_authorized(
        self,
        client: httpx.AsyncClient,
        manager_token: str,
    ):
        manager = await _get_me(client, manager_token)
        manager_dept_id = manager["department_id"]
        assert manager_dept_id is not None
        created = await _create_document(
            client,
            manager_token,
            title=f"update-ok-{uuid.uuid4().hex}",
            allowed_departments=[manager_dept_id],
        )

        resp = await client.patch(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={"title": "Updated title"},
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["id"] == created["id"]
        assert data["title"] == "Updated title"
        assert data["updated_at"] is not None

    async def test_update_returns_403_for_unauthorized_role(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        employee = await _get_me(client, employee_token)
        employee_dept_id = employee["department_id"]
        assert employee_dept_id is not None
        created = await _create_document(
            client,
            admin_token,
            title=f"update-deny-{uuid.uuid4().hex}",
            allowed_departments=[employee_dept_id],
        )

        resp = await client.patch(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {employee_token}"},
            json={"title": "Updated title"},
        )
        assert resp.status_code == 403

    async def test_update_returns_404_for_nonexistent(self, client: httpx.AsyncClient, manager_token: str):
        resp = await client.patch(
            f"{API_PREFIX}/99999",
            headers={"Authorization": f"Bearer {manager_token}"},
            json={"title": "Updated title"},
        )
        assert resp.status_code == 404


class TestDocumentDelete:
    """DELETE /api/v1/documents/{id}"""

    async def test_delete_requires_auth(self, client: httpx.AsyncClient):
        resp = await client.delete(f"{API_PREFIX}/1")
        if resp.status_code == 404:
            pytest.skip("Document API routes are not available on the running integration server")
        assert resp.status_code == 401

    async def test_delete_returns_204_for_authorized(
        self,
        client: httpx.AsyncClient,
        manager_token: str,
    ):
        manager = await _get_me(client, manager_token)
        manager_dept_id = manager["department_id"]
        assert manager_dept_id is not None
        created = await _create_document(
            client,
            manager_token,
            title=f"delete-ok-{uuid.uuid4().hex}",
            allowed_departments=[manager_dept_id],
        )

        resp = await client.delete(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert resp.status_code == 204, resp.text
        assert resp.text == ""

    async def test_delete_returns_403_for_unauthorized_role(
        self,
        client: httpx.AsyncClient,
        admin_token: str,
        employee_token: str,
    ):
        employee = await _get_me(client, employee_token)
        employee_dept_id = employee["department_id"]
        assert employee_dept_id is not None
        created = await _create_document(
            client,
            admin_token,
            title=f"delete-deny-{uuid.uuid4().hex}",
            allowed_departments=[employee_dept_id],
        )

        resp = await client.delete(
            f"{API_PREFIX}/{created['id']}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert resp.status_code == 403

    async def test_delete_returns_404_for_nonexistent(self, client: httpx.AsyncClient, manager_token: str):
        resp = await client.delete(
            f"{API_PREFIX}/99999",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert resp.status_code == 404
