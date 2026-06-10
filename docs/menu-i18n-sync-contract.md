# Menu and i18n sync contract

## Purpose
This document freezes the backend contract for admin menu and i18n seed assets before the sync implementation exists.

## Seed asset location

The backend seed assets live under:

- `app/infrastructure/database/seed_assets/admin_config/menu.json`
- `app/infrastructure/database/seed_assets/admin_config/vi.json`
- `app/infrastructure/database/seed_assets/admin_config/en.json`

These files are read by the future sync loader and must remain version-controlled.

## Menu schema

Natural key: `key`

Required fields:

- `key`: string, unique, stable identifier for the menu node
- `parent_key`: string or null, references another menu `key`
- `title_key`: string, i18n lookup key for the display title
- `route`: string or null, app route path
- `icon`: string or null, icon token
- `order`: integer, display order among siblings
- `permission_key`: string or null, permission gate for visibility/action control
- `is_visible`: boolean
- `is_external`: boolean

Indexes and constraints:

- unique constraint: `uq_menu_key`
- index: `parent_key`
- index: `permission_key`
- index: `order`
- route values, when present, must be unique within the seed dataset and database

## Translation schema

Natural key: `(locale, key)`

Required fields:

- `locale`: string, for example `vi` or `en`
- `key`: string, stable translation key
- `value`: string, translated text
- `namespace`: string, logical group for the translation key

Indexes and constraints:

- unique constraint: `uq_translation_locale_key`
- index: `locale`
- index: `namespace`

## Sync rules

The sync implementation must follow these rules:

- rerun is idempotent and must not create duplicates
- duplicate `key` in menu data aborts the transaction and returns validation errors
- duplicate `route` in menu data aborts the transaction and returns validation errors
- missing parent reference aborts the transaction and returns validation errors
- malformed JSON aborts the transaction and returns validation errors
- missing required fields aborts the transaction and returns validation errors
- missing locale key between `vi.json` and `en.json` aborts the transaction and returns validation errors
- rows already present in the DB but absent from the seed files are kept and counted as `skipped`
- concurrent sync for the same resource returns `409 Conflict` with `sync already in progress`
- `dry_run=true` validates and computes the summary only; it must not persist any change

## Expected response shape

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
