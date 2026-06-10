"""Integration test fixtures — HTTP client against running API."""
from __future__ import annotations

import pytest
import httpx
import os

BASE_URL = os.environ.get("ADMIN_API_BASE_URL", "http://localhost:8000")


@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL) as c:
        yield c


@pytest.fixture
async def admin_token(client: httpx.AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json={
        "email": "admin@company.vn",
        "password": "Admin@123",
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
async def manager_token(client: httpx.AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json={
        "email": "manager@company.vn",
        "password": "Manager@123",
    })
    assert resp.status_code == 200, f"Manager login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
async def employee_token(client: httpx.AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json={
        "email": "employee@company.vn",
        "password": "Employee@123",
    })
    assert resp.status_code == 200, f"Employee login failed: {resp.text}"
    return resp.json()["access_token"]
