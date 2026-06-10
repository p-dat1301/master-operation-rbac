# Admin frontend runbook

## Prerequisites

- Backend database available on `localhost:5432`
- Python dependencies installed in repo root `.venv`
- Node dependencies installed in `apps/admin`

## Install

```bash
make up
make seed
cd apps/admin && npm install
```

## Start local backend for frontend work

The admin app is currently verified against the local backend process on `8010`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop \
SECRET_KEY=dev-secret \
../../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

## Start frontend dev server

```bash
npm run dev -- --host 127.0.0.1 --port 4200
```

Open `http://127.0.0.1:4200/login`.

## Frontend commands

```bash
npm run build
npm run test:unit
npm run e2e
npm run check:modal-policy
```

## Auth fixtures for local verify

Allowed admin account:

- `admin@company.vn / Admin@123`
- Has permission: `system.config.manage`

Denied accounts:

- `manager@company.vn / Manager@123` → authenticated but forbidden on sync routes
- `employee@company.vn / Employee@123` → authenticated but forbidden on sync routes

## Protected routes

- `/config/menu-sync`
- `/config/i18n-sync`

Expected behavior:

- no token → `/unauthorized`
- manager token → `/forbidden`
- admin token → route allowed

## Sync API summary shape

Both sync screens expect:

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

For the full backend + frontend operator checklist, see `docs/admin-sync-operations.md`.
