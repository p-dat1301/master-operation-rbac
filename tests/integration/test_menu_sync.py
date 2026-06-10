import httpx


async def test_menu_sync_no_token_returns_401(client: httpx.AsyncClient):
    resp = await client.post("/api/v1/admin/config/menu/sync", json={"dry_run": False})

    assert resp.status_code == 401


async def test_menu_sync_manager_returns_403(client: httpx.AsyncClient, manager_token: str):
    resp = await client.post(
        "/api/v1/admin/config/menu/sync",
        json={"dry_run": False},
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    assert resp.status_code == 403


async def test_menu_sync_invalid_token_returns_401(client: httpx.AsyncClient):
    resp = await client.post(
        "/api/v1/admin/config/menu/sync",
        json={"dry_run": False},
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert resp.status_code == 401


async def test_menu_sync_admin_success_and_idempotent(client: httpx.AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}

    first = await client.post("/api/v1/admin/config/menu/sync", json={"dry_run": False}, headers=headers)
    second = await client.post("/api/v1/admin/config/menu/sync", json={"dry_run": False}, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["resource"] == "menu"
    assert set(first.json()) == {"resource", "created", "updated", "skipped", "errors", "dry_run"}
    assert second.json()["created"] == 0
    assert second.json()["errors"] == []


async def test_menu_sync_dry_run_returns_summary_shape(client: httpx.AsyncClient, admin_token: str):
    resp = await client.post(
        "/api/v1/admin/config/menu/sync",
        json={"dry_run": True},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["dry_run"] is True
    assert set(resp.json()) == {"resource", "created", "updated", "skipped", "errors", "dry_run"}
