# Admin sync operations guide

## 1. Boot local stack

```bash
make up
make seed
```

## 2. Apply migrations explicitly when needed

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop \
SECRET_KEY=dev-secret \
.venv/bin/alembic upgrade head
```

Check current revision:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop \
SECRET_KEY=dev-secret \
.venv/bin/alembic current
```

## 3. Backend local process for admin/frontend verification

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop \
SECRET_KEY=dev-secret \
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Health check:

```bash
curl http://127.0.0.1:8010/health
```

Expected:

```json
{"status":"ok","db":"connected"}
```

## 4. Frontend install / dev / build

```bash
cd apps/admin
npm install
npm run dev -- --host 127.0.0.1 --port 4200
npm run build
```

## 5. Frontend automated verification

```bash
cd apps/admin
npm run test:unit
npm run e2e
npm run check:modal-policy
```

## 6. Backend sync tests

```bash
.venv/bin/pytest -q \
  tests/unit/application/test_menu_sync_use_case.py \
  tests/unit/application/test_i18n_sync_use_case.py \
  tests/unit/application/test_admin_config_loader_integration.py \
  tests/unit/application/test_sync_runtime.py

ADMIN_API_BASE_URL=http://127.0.0.1:8010 \
.venv/bin/pytest -q \
  tests/integration/test_menu_sync.py \
  tests/integration/test_i18n_sync.py
```

## 7. Fixture users and expected authorization

| User | Password | Expected |
|---|---|---|
| `admin@company.vn` | `Admin@123` | allowed on menu/i18n sync |
| `manager@company.vn` | `Manager@123` | authenticated, but `403` / forbidden route |
| `employee@company.vn` | `Employee@123` | authenticated, but no sync permission |
| no token | n/a | `401` / unauthorized route |

Required permission for sync APIs and sync routes:

- `system.config.manage`

## 8. Seed asset locations

- `app/infrastructure/database/seed_assets/admin_config/menu.json`
- `app/infrastructure/database/seed_assets/admin_config/vi.json`
- `app/infrastructure/database/seed_assets/admin_config/en.json`

Test override path:

- `SYNC_SEED_DIR=/path/to/fixture-dir`

## 9. Sync API endpoints

- `POST /api/v1/admin/config/menu/sync`
- `POST /api/v1/admin/config/i18n/sync`

Default request body:

```json
{
  "dry_run": false
}
```

Expected response shape:

```json
{
  "resource": "menu|i18n",
  "created": 0,
  "updated": 0,
  "skipped": 0,
  "errors": [],
  "dry_run": false
}
```

## 10. Example API verification

Admin login:

```bash
curl -X POST http://127.0.0.1:8010/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.vn","password":"Admin@123"}'
```

Admin i18n sync:

```bash
TOKEN="<admin access token>"
curl -X POST http://127.0.0.1:8010/api/v1/admin/config/i18n/sync \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

Concurrent sync probe:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop \
SECRET_KEY=dev-secret \
SYNC_TEST_DELAY_MS=500 \
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8012
```

Then fire two requests at once; expected outcome:

- one request `200`
- one request `409`
- `errors = ["sync already in progress"]` on the rejected request

## 11. What has been verified in this workspace

- frontend build
- frontend unit tests
- Playwright shell/auth/sync e2e
- backend menu/i18n unit + integration tests
- live menu sync and i18n sync through the browser
- live concurrent sync conflict response
