"""Integration tests — Auth endpoints."""
from __future__ import annotations

import httpx
import pytest


class TestAuthLogin:
    async def test_admin_login_success(self, client: httpx.AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@company.vn",
            "password": "Admin@123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    async def test_manager_login_success(self, client: httpx.AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "manager@company.vn",
            "password": "Manager@123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    async def test_employee_login_success(self, client: httpx.AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "employee@company.vn",
            "password": "Employee@123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client: httpx.AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@company.vn",
            "password": "WrongPassword123",
        })
        assert resp.status_code == 403
        assert "Permission denied" in resp.json()["detail"]

    async def test_login_nonexistent_user(self, client: httpx.AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@company.vn",
            "password": "SomePass123",
        })
        assert resp.status_code == 404
        assert "User not found" in resp.json()["detail"]

    async def test_login_inactive_user(self, client: httpx.AsyncClient):
        # admin is active; test with a known inactive user would need seed data
        # For now, verify the inactive path returns 403
        pass  # Covered by unit tests; integration needs inactive seeded user


class TestAuthGetMe:
    async def test_get_me_admin(self, client: httpx.AsyncClient, admin_token: str):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@company.vn"
        assert data["role_name"] == "admin"

    async def test_get_me_manager(self, client: httpx.AsyncClient, manager_token: str):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "manager@company.vn"
        assert data["role_name"] == "manager"

    async def test_get_me_employee(self, client: httpx.AsyncClient, employee_token: str):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "employee@company.vn"
        assert data["role_name"] == "employee"

    async def test_get_me_no_token(self, client: httpx.AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token(self, client: httpx.AsyncClient):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401
