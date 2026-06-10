# Xây dựng frontend admin Angular 21 cho hệ RBAC

## TL;DR
> **Summary**: Tạo mới admin frontend Angular 21 tại `apps/admin` cho repo FastAPI hiện có, dùng TailwindCSS-first + NG ZORRO theo phong cách Ant Design Pro, đồng thời bổ sung backend menu/i18n seed-sync và lớp kiểm thử đầy đủ.
> **Deliverables**:
> - Angular admin shell chạy được tại `apps/admin`
> - Base services/models/auth guard/permission guard cho admin
> - Backend menu sync từ `menu.json` vào DB với `permission_key`
> - Backend i18n sync từ `vi.json` và `en.json` vào DB
> - Admin UI để trigger sync menu/i18n có phân quyền `system.config.manage`
> - Unit tests, pytest tests, Playwright e2e, và wave xác minh cuối
> **Effort**: XL
> **Parallel**: YES - 4 waves
> **Critical Path**: 2 → 4 → 5 → 8 → 10 → 11 → 13 → F1-F4

## Context
### Original Request
- Build frontend admin bằng Angular 21
- TailwindCSS first
- Ant Design Admin Pro layout
- Full control NG ZORRO AntD
- Service base, models
- Modal chỉ dùng `NzModalService`
- Seed `menu.json` với `permission key`, sync vào DB
- Seed `vi.json`, `en.json` ở backend API, admin có function sync DB
- TODO chi tiết bằng tiếng Việt

### Interview Summary
- Repo hiện tại là **backend-only FastAPI**, chưa có Angular workspace.
- Frontend mới sẽ đặt tại `apps/admin`.
- Chiến lược test: setup **frontend unit test + Playwright e2e**; backend giữ `pytest` unit/integration.
- Permission bảo vệ API/menu/i18n sync: `system.config.manage`.
- Phạm vi MVP: **admin shell + auth/permission wiring + menu sync + i18n sync + shared services/models**; không mở rộng sang CRUD module khác.

### Metis Review (gaps addressed)
- Giới hạn phạm vi để tránh scope creep sang full admin suite.
- Bắt buộc sync **idempotent**, có **created/updated/skipped summary**, có xử lý duplicate/invalid JSON/partial failure.
- Bắt buộc thêm migration Alembic cho schema mới; không sửa schema bằng seed script.
- Bắt buộc test unauthorized/forbidden/happy path/rerun/no-duplicate/concurrency/modal cleanup.

### Locked Technical Defaults
- **Package manager**: dùng `npm` cho `apps/admin`.
- **Frontend scripts bắt buộc**:
  - `npm run dev` → `ng serve`
  - `npm run build` → build production app
  - `npm run test:unit` → unit tests frontend
  - `npm run e2e` → Playwright test
- **Backend API paths bắt buộc**:
  - `POST /api/v1/admin/config/menu/sync`
  - `POST /api/v1/admin/config/i18n/sync`
- **Sync request contract**: body mặc định là `{ "dry_run": false }`; backend đọc seed file từ local backend assets, không upload file từ UI ở MVP.
- **`dry_run=true` semantics**: backend chỉ validate + tính summary thay đổi dự kiến, **không ghi DB**, luôn rollback/no-commit, và vẫn trả đủ `created/updated/skipped/errors/dry_run=true`.
- **Sync response contract**:
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
- **DB keys/constraints**:
  - Menu: natural key là `key`; unique constraint `uq_menu_key`; index cho `parent_key`, `permission_key`, `order`; `route` nullable nhưng nếu có giá trị thì phải unique trong dataset seed và DB.
  - Translation: natural key là `(locale, key)`; unique constraint `uq_translation_locale_key`; index cho `locale` và `namespace`.
- **Sync semantics bắt buộc**:
  - Duplicate `key`, duplicate `route`, missing parent, malformed JSON, missing required field → abort transaction, trả lỗi 4xx và `errors` chi tiết.
  - Missing locale key giữa `vi.json` và `en.json` → abort transaction, trả lỗi validation; không partial commit.
  - Record có trong DB nhưng không còn trong seed file → **không xóa**, giữ nguyên và tăng `skipped`.
  - Concurrent sync cùng resource → request đầu tiên được xử lý; request đồng thời thứ hai phải trả `409 Conflict` với `errors[]` nêu rõ `sync already in progress`; không chờ lock và không được tạo duplicate/partial state.
- **Test fixture injection strategy**: backend sync layer phải đọc asset thông qua seed-loader abstraction; test được phép override đường dẫn asset bằng cấu hình/env `SYNC_SEED_DIR` hoặc dependency override tương đương để nạp fixture invalid/duplicate/missing-key mà không đổi contract UI/API.
- **Permission fixtures bắt buộc**:
  - `admin@company.vn` được gán thêm permission mới `system.config.manage`.
  - `manager@company.vn` và `employee@company.vn` không có permission này.
  - `401` dùng request không token hoặc token invalid; `403` dùng `manager` token; `200` dùng `admin` token.
- **Frontend routes/test selectors bắt buộc**:
  - Route: `/config/menu-sync` và `/config/i18n-sync`
  - Selectors: `[data-testid="admin-sider"]`, `[data-testid="admin-header"]`, `[data-testid="menu-sync-page"]`, `[data-testid="i18n-sync-page"]`, `[data-testid="sync-menu-button"]`, `[data-testid="sync-i18n-button"]`, `[data-testid="sync-confirm-modal"]`, `[data-testid="sync-summary-created"]`, `[data-testid="sync-summary-updated"]`, `[data-testid="sync-summary-skipped"]`, `[data-testid="forbidden-page"]`
- **Modal enforcement rule**:
  - Allowed: inject/call `NzModalService` or project wrapper service chỉ bọc `NzModalService`.
  - Forbidden patterns trong `apps/admin/src`: `<nz-modal`, `[nzVisible]`, `[(nzVisible)]`, boolean flag kiểu `isModalOpen`/`showModal` để điều khiển dialog trực tiếp.
  - Verification command bắt buộc: grep fail nếu thấy pattern cấm trong source.

## Work Objectives
### Core Objective
Xây một nền tảng admin frontend độc lập tại `apps/admin` kết nối với backend FastAPI hiện có, đồng thời bổ sung các backend capability tối thiểu để seed/sync menu và i18n theo permission `system.config.manage`.

### Deliverables
- Angular workspace/app tại `apps/admin`
- Admin shell: sidebar/header/content/breadcrumb/responsive sider
- Auth integration + permission-aware routing
- Base API service, interceptor, models chuẩn
- Backend DB schema + model + repository + use case + route cho menu và i18n sync
- Seed assets: `menu.json`, `vi.json`, `en.json`
- Admin sync screen cho menu/i18n
- Bộ test + bằng chứng QA

### Definition of Done (verifiable conditions with commands)
- `apps/admin` cài dependency thành công và build production thành công.
- `apps/admin` chạy unit test thành công.
- Playwright e2e cho admin shell + sync flows pass.
- `pytest` cho backend menu/i18n sync pass.
- Sync API trả đúng `401`, `403`, success summary, và rerun không tạo duplicate.
- DB có dữ liệu menu và translation đúng sau sync.

### Must Have
- Angular 21 standalone-first structure
- TailwindCSS-first styling, NG ZORRO làm UI component chính
- Chỉ dùng `NzModalService` cho modal/confirm dialog
- `system.config.manage` làm permission gate cho cả frontend route/action và backend API
- Seed assets được version-control và sync idempotent

### Must NOT Have
- Không build thêm CRUD module ngoài phạm vi sync/admin shell
- Không trộn UI kit khác ngoài NG ZORRO + Tailwind utilities
- Không dùng inline modal pattern thay cho `NzModalService`
- Không cập nhật schema DB bằng code seed không migration
- Không để frontend phụ thuộc vào assumption không kiểm chứng về output/deploy thống nhất

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: **tests-after** với `pytest` cho backend, Angular unit test cho frontend, Playwright cho e2e.
- QA policy: Mỗi task implementation đều có happy path + failure/edge path.
- Evidence: `.omo/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. Shared dependency được đẩy vào Wave 1.

Wave 1: nền tảng workspace + backend schema contract + seed asset contract  
Wave 2: backend implementation + frontend shell/foundation song song  
Wave 3: auth/permission/sync UI + automated tests  
Wave 4: hardening, edge cases, docs vận hành, full verification

### Dependency Matrix (full, all tasks)
- 1 blocks: 6, 7
- 2 blocks: 4, 5
- 3 blocks: 6, 7
- 4 blocks: 5, 8, 9, 10
- 5 blocks: 8, 9, 10
- 6 blocks: 8, 10
- 7 blocks: 8, 9, 10
- 8 blocks: 10, 11, 12
- 9 blocks: 11, 12
- 10 blocks: 11, 12
- 11 blocks: 13
- 12 blocks: 13
- 13 blocks: F1-F4

### Agent Dispatch Summary
- Wave 1 → 3 tasks → unspecified-high / quick
- Wave 2 → 4 tasks → unspecified-high / visual-engineering
- Wave 3 → 3 tasks → visual-engineering / unspecified-high
- Wave 4 → 3 tasks → unspecified-high / deep

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: Agent Profile + Parallelization + QA Scenarios.

- [x] 1. Khởi tạo Angular admin workspace tại `apps/admin`

  **What to do**: Tạo mới Angular 21 app standalone-first tại `apps/admin`; dùng `npm`; cấu hình scripts chính xác `dev`, `build`, `test:unit`, `e2e`; thêm cấu trúc thư mục tối thiểu `src/app/core`, `src/app/shared`, `src/app/layouts`, `src/app/features`, `src/app/models`, `src/app/services`; đảm bảo repo Python hiện có không bị ảnh hưởng bởi workspace mới.
  **Must NOT do**: Không tái cấu trúc `app/`, `tests/`, `alembic/`; không thêm monorepo phức tạp vượt nhu cầu; không kéo thêm frontend app thứ hai.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: khởi tạo nền tảng mới, cần kỷ luật cấu hình.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[customize-opencode]` - không chỉnh cấu hình OpenCode.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 6, 7 | Blocked By: none

  **References**:
  - External: `https://angular.dev/reference/configs/file-structure` - cấu trúc file Angular hiện đại.
  - External: `https://angular.dev/tools/cli/build` - build/app builder hiện tại.
  - External: `https://angular.dev/guide/di/defining-dependency-providers` - provider toàn app.
  - Pattern: `app/main.py` - ví dụ entrypoint backend hiện có để tránh va chạm cấu trúc.

  **Acceptance Criteria**:
  - [x] Có thư mục `apps/admin` với Angular standalone app và `package.json` chứa scripts `dev`, `build`, `test:unit`, `e2e`.
  - [x] Chạy `cd apps/admin && npm install && npm run build` thành công với exit code 0.
  - [x] Cấu trúc thư mục core/shared/layouts/features/models/services tồn tại.

  **Execution Notes**:
  - Đã tạo Angular 21 standalone workspace tại `apps/admin` bằng `@angular/cli@21`.
  - Scripts hiện có: `dev`, `build`, `test:unit`, `e2e`.
  - Đã xác minh `npm install`, `npm run build`, `npm run test:unit`, và `npm run e2e -- --list` đều chạy được trong `apps/admin`.
  - Kết quả `pytest -q tests/unit` từ root repo vẫn còn lỗi sẵn có ở leave-request tests hiện hữu, không liên quan đến scaffold frontend.

  **QA Scenarios**:
  ```
  Scenario: Khởi tạo và build frontend thành công
    Tool: Bash
    Steps: chạy `npm install`; chạy `npm run build` trong `apps/admin`
    Expected: cả hai lệnh exit code 0; thư mục output build của app được tạo
    Evidence: .omo/evidence/task-1-admin-build.txt

  Scenario: Backend repo không bị ảnh hưởng bởi frontend scaffold
    Tool: Bash
    Steps: chạy `pytest -q tests/unit` từ root repo sau khi scaffold
    Expected: backend unit tests hiện có vẫn chạy/pass hoặc ít nhất không fail do cấu trúc frontend mới; các lỗi tồn tại nếu có phải là lỗi pre-existing, không do scaffold
    Evidence: .omo/evidence/task-1-backend-regression.txt
  ```

  **Commit**: YES | Message: `feat(admin): scaffold angular admin workspace` | Files: `apps/admin/**`

- [x] 2. Thiết kế contract dữ liệu menu và i18n cho DB + seed assets

  **What to do**: Định nghĩa schema dữ liệu cho menu và translation: menu gồm `key`, `parent_key`, `title_key`, `route`, `icon`, `order`, `permission_key`, `is_visible`, `is_external`; translation gồm `locale`, `key`, `value`, `namespace`; chốt natural keys/unique constraints/indexes đúng như phần Locked Technical Defaults; chuẩn hóa asset `menu.json`, `vi.json`, `en.json` ở backend.
  **Must NOT do**: Không để schema mơ hồ; không dùng title text làm khóa đồng bộ; không trộn localization vào menu table.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: đây là contract trung tâm cho cả backend lẫn frontend.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-refactoring]` - không phải refactor.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 5 | Blocked By: none

  **References**:
  - Pattern: `app/domain/entities/permission.py` - cách đặt entity/field RBAC hiện có.
  - Pattern: `app/infrastructure/database/seed.py` - phong cách seed idempotent hiện tại.
  - Pattern: `alembic/versions/388ec37210d1_init_all_tables.py` - chuẩn migration hiện có.

  **Acceptance Criteria**:
  - [x] Có file contract/tài liệu hoặc schema source chỉ rõ đầy đủ field `key,parent_key,title_key,route,icon,order,permission_key,is_visible,is_external` cho menu và `locale,key,value,namespace` cho translation.
  - [x] Có quy tắc sync cụ thể cho rerun, duplicate key, duplicate route, invalid JSON, missing parent, missing locale key, partial failure, concurrent sync.
  - [x] Vị trí asset `menu.json`, `vi.json`, `en.json` được chốt trong backend tree.

  **Execution Notes**:
  - Contract được chốt tại [docs/menu-i18n-sync-contract.md](docs/menu-i18n-sync-contract.md).
  - Seed assets được đặt tại `app/infrastructure/database/seed_assets/admin_config/`.
  - Đã xác minh 3 file JSON parse được bằng `node`.

  **QA Scenarios**:
  ```
  Scenario: Dữ liệu seed hợp lệ theo contract
    Tool: Bash
    Steps: chạy script/lệnh validate JSON schema cho `menu.json`, `vi.json`, `en.json`
    Expected: tất cả file seed parse được và đúng field contract
    Evidence: .omo/evidence/task-2-seed-contract.txt

  Scenario: File seed sai cấu trúc bị chặn
    Tool: Bash
    Steps: chạy test/validator với một fixture JSON thiếu `permission_key` hoặc duplicate `key`
    Expected: validator báo lỗi rõ ràng và sync không tiếp tục
    Evidence: .omo/evidence/task-2-seed-contract-error.txt
  ```

  **Commit**: YES | Message: `feat(rbac): define menu and i18n sync contracts` | Files: `app/**`, `alembic/**`, `seed assets`

- [x] 3. Chuẩn bị nền TailwindCSS-first + NG ZORRO cho admin

  **What to do**: Cài và cấu hình TailwindCSS theo hướng dẫn hiện tại (PostCSS + global import), cài NG ZORRO tương thích Angular 21, chốt theme/global config, set convention “layout/styling ưu tiên Tailwind, component UI ưu tiên NG ZORRO”, và tạo policy kỹ thuật rằng mọi modal/confirm dialog chỉ đi qua `NzModalService` cùng bộ pattern cấm đã khóa ở trên.
  **Must NOT do**: Không áp dụng hướng dẫn Tailwind v3 cũ nếu stack đã dùng v4; không thêm UI library khác; không dùng `<nz-modal>` inline làm pattern mặc định.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: liên quan layout system, theme và UI primitive.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[customize-opencode]` - không chỉnh OpenCode.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 6, 7 | Blocked By: none

  **References**:
  - External: `https://tailwindcss.com/docs/guides/angular` - setup Tailwind với Angular.
  - External: `https://tailwindcss.com/docs/installation/using-postcss` - cấu hình PostCSS hiện tại.
  - External: `https://ng.ant.design/` - entry docs NG ZORRO.
  - External: `https://ng.ant.design/components/modal/en` - modal service policy.
  - External: `https://ng.ant.design/docs/global-config/en` - global config.

  **Acceptance Criteria**:
  - [x] Có ít nhất một page hoặc shell component build pass khi đồng thời dùng utility classes Tailwind và component NG ZORRO.
  - [x] Source chứa file global styles với import Tailwind và cấu hình NG ZORRO global config/provider trong app bootstrap hoặc app config.
  - [x] Có rule kiểm tra source fail nếu xuất hiện `<nz-modal`, `[nzVisible]`, `[(nzVisible)]`, `isModalOpen`, hoặc `showModal` trong `apps/admin/src`.

  **Execution Notes**:
  - Đã cấu hình Tailwind v4 theo PostCSS với `postcss.config.json` dùng plugin `@tailwindcss/postcss`.
  - Đã chuyển global stylesheet sang `src/styles.css` và import `@import "tailwindcss";` cùng `@import 'ng-zorro-antd/ng-zorro-antd.min.css';`.
  - Đã cài `@angular/animations`, `ng-zorro-antd`, `@ant-design/icons-angular` cho stack Angular 21.
  - Đã cấu hình provider NG ZORRO global trong `src/app/app.config.ts` qua `NZ_CONFIG` và bật `provideAnimations()`.
  - Đã có page mẫu (`src/app/features/home/home-page.component.ts`) dùng đồng thời utility classes Tailwind và component `nz-button`.
  - Đã thêm script `npm run check:modal-policy` để fail khi source chứa pattern modal inline bị cấm.
  - Đã verify pass: `npm run build`, `npm run test:unit`, `npm run e2e`, `npm run check:modal-policy`, và `bash -n tools/check-modal-policy.sh`.

  **QA Scenarios**:
  ```
  Scenario: Tailwind và NG ZORRO cùng hoạt động
    Tool: Bash
    Steps: chạy app dev/build; render một page mẫu dùng utility class Tailwind và component NG ZORRO
    Expected: build pass, style hiển thị đúng, không lỗi compile theme
    Evidence: .omo/evidence/task-3-ui-stack.txt

  Scenario: Modal inline bị cấm bởi rule dự án
    Tool: Bash
    Steps: chạy command grep/check rule trên `apps/admin/src` để tìm `<nz-modal|\[nzVisible\]|\[\(nzVisible\)\]|isModalOpen|showModal`
    Expected: command trả không có match cho source hợp lệ; nếu có match thì rule/test fail
    Evidence: .omo/evidence/task-3-modal-policy.txt
  ```

  **Commit**: YES | Message: `feat(admin): configure tailwind and ng-zorro foundation` | Files: `apps/admin/**`

- [x] 4. Bổ sung schema DB, ORM model, repository và seed flow cho menu

  **What to do**: Tạo migration Alembic, SQLAlchemy model, domain/repository contract, repository implementation, use case, và API `POST /api/v1/admin/config/menu/sync`; hỗ trợ ingest `menu.json`, ánh xạ `permission_key`, xử lý parent-child tree, upsert theo natural key `key`, validate unique `route`, và trả summary `{resource,created,updated,skipped,errors,dry_run}`.
  **Must NOT do**: Không bỏ qua migration; không nhúng logic DB trực tiếp trong route; không duplicate permission record; không commit partial state nếu sync fail ở giữa mà chưa định nghĩa transactional behavior.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: thay đổi backend nhiều layer và DB.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-debugging]` - không phải truy bug.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 5, 8, 9, 10 | Blocked By: 2

  **References**:
  - Pattern: `app/infrastructure/database/models/*_model.py` - cách định nghĩa ORM model hiện có.
  - Pattern: `app/domain/repositories/*.py` - interface repository.
  - Pattern: `app/application/use_cases/**` - naming use case theo action.
  - Pattern: `app/presentation/api/v1/*.py` - route style hiện tại.
  - Pattern: `app/infrastructure/database/seed.py` - seed idempotent hiện có.

  **Acceptance Criteria**:
  - [x] Có migration tạo bảng/cột/index cần thiết cho menu sync.
  - [x] Có endpoint `POST /api/v1/admin/config/menu/sync` được bảo vệ bằng `system.config.manage`.
  - [x] Rerun sync cùng dữ liệu không tạo duplicate row.
  - [x] Duplicate `key`, duplicate `route`, hoặc `parent_key` không hợp lệ trả 4xx với `errors[]` chi tiết và không commit partial state.

  **Execution Notes**:
  - Đã thêm migration `alembic/versions/9b8d1a7c4e52_add_admin_menu_sync.py` tạo bảng `menus` cùng unique/index theo contract.
  - Đã thêm `MenuModel`, `Menu` entity, `MenuRepository`, `SQLAlchemyMenuRepository`, `MenuSyncUseCase`, `AdminConfigSeedLoader`, route `POST /api/v1/admin/config/menu/sync`, và schema request/response tương ứng.
  - Đã seed thêm permission `system.config.manage` trong `app/infrastructure/database/seed.py` để admin truy cập endpoint này đúng plan.
  - Đã verify pass: `.venv/bin/pytest -q tests/unit/application/test_menu_sync_use_case.py tests/integration/test_menu_sync.py`, `alembic current`, và QA live endpoint với kết quả `401` no-token, `403` manager, `200` admin, rerun idempotent.

  **QA Scenarios**:
  ```
  Scenario: Sync menu thành công và idempotent
    Tool: Bash
    Steps: gọi `POST /api/v1/admin/config/menu/sync` với body `{"dry_run": false}` hai lần bằng admin token; query DB hoặc response summary
    Expected: lần 1 trả `resource="menu"`; lần 2 không tạo duplicate row; response có `created/updated/skipped/errors/dry_run`
    Evidence: .omo/evidence/task-4-menu-sync.txt

  Scenario: Menu JSON lỗi bị rollback
    Tool: Bash
    Steps: gọi endpoint bằng fixture menu có duplicate `key`, duplicate `route`, hoặc `parent_key` không tồn tại
    Expected: API trả 4xx với `errors[]`; transaction rollback; DB không có partial write
    Evidence: .omo/evidence/task-4-menu-sync-error.txt
  ```

  **Commit**: YES | Message: `feat(rbac): add menu sync backend` | Files: `app/**`, `alembic/**`, `tests/**`, `seed assets`

- [x] 5. Bổ sung schema DB, ORM model, repository và seed flow cho i18n

  **What to do**: Tạo migration Alembic tiếp theo sau task 4 để tránh revision conflict, rồi thêm model, repository, use case, và API `POST /api/v1/admin/config/i18n/sync` cho translation entries từ `vi.json`/`en.json`; chuẩn hóa khóa, locale, namespace; hỗ trợ upsert theo `(locale, key)` và trả summary `{resource,created,updated,skipped,errors,dry_run}`.
  **Must NOT do**: Không trộn translation vào bảng menu; không dùng key text tự phát; không bỏ qua locale thiếu giá trị mà không báo cáo.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: backend multi-layer + data integrity.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-refactoring]` - không phải rename/refactor.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 8, 9, 10 | Blocked By: 2, 4

  **References**:
  - Pattern: `app/presentation/schemas/*.py` - schema response/request hiện tại.
  - Pattern: `app/infrastructure/database/repositories/sqlalchemy_*_repo.py` - repository impl style.
  - Pattern: `tests/integration/test_auth.py` - pattern test endpoint integration.

  **Acceptance Criteria**:
  - [x] Có migration Alembic được tạo sau revision của task 4 và các lớp backend đầy đủ cho translation sync.
  - [x] Endpoint `POST /api/v1/admin/config/i18n/sync` trả summary đúng shape đã khóa.
  - [x] Locale thiếu key hoặc JSON không hợp lệ trả 4xx với `errors[]` và rollback toàn transaction.
  - [x] Rerun sync không tạo duplicate.

  **Execution Notes**:
  - Đã thêm migration `alembic/versions/a4c2d8f1e9b6_add_i18n_translation_sync.py` tạo bảng `translations`, unique `(locale, key)`, index `locale` và `namespace`.
  - Đã thêm `Translation` entity, `TranslationRepository`, `SQLAlchemyTranslationRepository`, `TranslationModel`, DTO/schema request-response, `I18nSyncUseCase`, DI provider, và route `POST /api/v1/admin/config/i18n/sync`.
  - `AdminConfigSeedLoader` giờ đọc `vi.json` và `en.json` qua `load_i18n()`; use case validate duplicate `(locale,key)`, locale sai file, thiếu field, malformed seed, và key thiếu giữa hai locale trước khi ghi DB.
  - Đã cấu hình test integration đọc `ADMIN_API_BASE_URL` để QA được với API process mới khi container `localhost:8000` chưa reload code.
  - Đã verify pass: `.venv/bin/pytest -q tests/unit/application/test_i18n_sync_use_case.py tests/unit/application/test_menu_sync_use_case.py`, `ADMIN_API_BASE_URL=http://127.0.0.1:8010 .venv/bin/pytest -q tests/integration/test_i18n_sync.py`, `alembic heads`, compile các module i18n mới, và QA HTTP live `401` no-token, `403` manager, `200` admin, rerun idempotent `created=0 skipped=8`.

  **QA Scenarios**:
  ```
  Scenario: Sync i18n hai locale thành công
    Tool: Bash
    Steps: gọi `POST /api/v1/admin/config/i18n/sync` với body `{"dry_run": false}` bằng admin token; xác nhận row DB/summary response
    Expected: cả hai locale được upsert đúng, response có `resource="i18n"` và các field summary bắt buộc
    Evidence: .omo/evidence/task-5-i18n-sync.txt

  Scenario: Một locale thiếu key bị báo cáo rõ ràng
    Tool: Bash
    Steps: gọi endpoint với fixture `en.json` thiếu key đang có trong `vi.json`
    Expected: API trả 4xx, `errors[]` nêu key thiếu; không partial commit
    Evidence: .omo/evidence/task-5-i18n-sync-error.txt
  ```

  **Commit**: YES | Message: `feat(i18n): add translation sync backend` | Files: `app/**`, `alembic/**`, `tests/**`, `seed assets`

- [x] 6. Dựng admin shell kiểu Ant Design Pro bằng NG ZORRO + Tailwind

  **What to do**: Tạo layout shell gồm `nz-layout`, `nz-sider`, `nz-header`, `nz-content`, breadcrumb, topbar actions, responsive collapse; dùng Tailwind cho spacing/layout/responsive; tạo router shell cho các trang MVP như dashboard placeholder, menu sync, i18n sync, unauthorized/forbidden/not-found.
  **Must NOT do**: Không cố clone full Ant Design Pro nâng cao; không thêm chart/analytics ngoài phạm vi; không làm sidebar hardcode không bám permission model.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: shell/layout/responsive UX.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-exploring]` - không phải discovery nữa.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8, 10 | Blocked By: 1, 3

  **References**:
  - External: `https://ng.ant.design/components/layout/en` - layout primitives.
  - Pattern: `app/presentation/api/v1/` - danh mục resource backend để phản ánh điều hướng admin sau này.

  **Acceptance Criteria**:
  - [x] Trang shell render các selector `[data-testid="admin-sider"]` và `[data-testid="admin-header"]`.
  - [x] Responsive collapse vẫn giữ được route content render sau khi viewport chuyển xuống mobile preset.
  - [x] Các route `/config/menu-sync` và `/config/i18n-sync` render placeholder/page component trong shell.

  **Execution Notes**:
  - Đã thêm `AdminShellComponent` tại `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` dùng `nz-layout`, `nz-sider`, `nz-header`, `nz-content`, breadcrumb và responsive collapse state.
  - Đã thêm các page standalone mới: `dashboard-page`, `menu-sync-page`, `i18n-sync-page`, `unauthorized-page`, `forbidden-page`, `not-found-page`.
  - Đã cập nhật `app.routes.ts` sang route tree dạng shell + children cho `/`, `/config/menu-sync`, `/config/i18n-sync`, cùng route hệ thống `/unauthorized`, `/forbidden`, `/not-found`.
  - Đã rút `app.html` về `router-outlet` thuần và chuyển styling shell vào component layout; đồng thời thêm đăng ký icon NG ZORRO trong `app.config.ts` để tránh console/runtime error khi render sidebar.
  - Đã verify pass: `npm run build`; QA browser với Playwright xác nhận desktop render có `admin-sider`, `admin-header`, breadcrumb và nav items; viewport mobile vẫn toggle/collapse được và route `/config/menu-sync` render đúng trong shell.

  **QA Scenarios**:
  ```
  Scenario: Shell admin hiển thị đúng trên desktop
    Tool: Playwright
    Steps: mở trang chính admin; assert tồn tại `[data-testid="admin-sider"]`, `[data-testid="admin-header"]`, breadcrumb, content root
    Expected: tất cả selector tồn tại và visible
    Evidence: .omo/evidence/task-6-shell-desktop.png

  Scenario: Responsive collapse hoạt động
    Tool: Playwright
    Steps: resize viewport nhỏ; trigger collapse/expand sider; chuyển route `/config/menu-sync`
    Expected: sider đổi state thành công, route content vẫn render với selector page tương ứng
    Evidence: .omo/evidence/task-6-shell-mobile.png
  ```

  **Commit**: YES | Message: `feat(admin): build shell layout` | Files: `apps/admin/**`

- [x] 7. Tạo base services, models, auth flow và permission-aware routing cho admin

  **What to do**: Tạo `BaseApiService`, typed API response models, auth service/store, HTTP interceptor, route guard cho authenticated + permission guard cho `system.config.manage`; dùng `/api/v1/auth/login` và `/api/v1/auth/me`; đọc `permissions: string[]` từ `UserResponse`; bảo vệ route `/config/menu-sync` và `/config/i18n-sync`.
  **Must NOT do**: Không hardcode permission trong component rời rạc; không duplicate HTTP logic trong từng feature service; không lưu token theo cách trái với auth contract backend.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: foundation logic, auth integration, typed contracts.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-impact-analysis]` - plan đã có, chưa sửa symbol trực tiếp ở đây.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8, 9, 10 | Blocked By: 1, 3

  **References**:
  - Pattern: `app/presentation/api/v1/auth.py` - route auth backend.
  - Pattern: `tests/integration/test_auth.py` - auth behavior để frontend bám theo.
  - Pattern: `app/domain/services/rbac_service.py` - semantics permission hiện có.

  **Acceptance Criteria**:
  - [x] Có service/interceptor/model chung cho API.
  - [x] Request không token vào route sync dẫn tới luồng unauthorized; manager token dẫn tới forbidden; admin token cho phép vào page.
  - [x] Auth state đọc được `permissions[]` từ `/api/v1/auth/me` để điều khiển menu visibility và action visibility.

  **Execution Notes**:
  - Đã thêm typed models `LoginRequest`, `LoginResponse`, `UserResponse`; `BaseApiService`; `AuthApiService`; `AuthStoreService`; `authInterceptor`; `authGuard`; `permissionGuard`.
  - Đã thêm `LoginPageComponent` tại `/login`, lưu token vào `localStorage`, gọi `/api/v1/auth/login` rồi bootstrap user state từ `/api/v1/auth/me`.
  - Đã cập nhật `app.config.ts` để cấp `HttpClient` + interceptor và `API_BASE_URL`; hiện đang trỏ `http://127.0.0.1:8000/api/v1` cho local verify cross-port.
  - Đã cập nhật `app.routes.ts` để bảo vệ shell bằng `authGuard` và bảo vệ `/config/menu-sync`, `/config/i18n-sync` bằng `permissionGuard('system.config.manage')`.
  - `AdminShellComponent` giờ đọc auth state thật để hiển thị identity chip, nút sign out, và ẩn/hiện nav items theo permission hiện có.
  - Đã verify pass: `npm run build`; Playwright QA xác nhận direct route không token → `/unauthorized`, login `admin@company.vn / Admin@123` → vào được `/config/menu-sync`, login `manager@company.vn / Manager@123` → bị chuyển sang `/forbidden`.

  **QA Scenarios**:
  ```
  Scenario: User có quyền truy cập được route sync
    Tool: Playwright
    Steps: đăng nhập `admin@company.vn / Admin@123`; gọi `/api/v1/auth/me`; vào page sync
    Expected: route mở được, action sync hiển thị
    Evidence: .omo/evidence/task-7-auth-allow.png

  Scenario: User không có quyền bị chặn
    Tool: Playwright
    Steps: đăng nhập `manager@company.vn / Manager@123`; truy cập trực tiếp URL sync
    Expected: bị redirect hoặc thấy `[data-testid="forbidden-page"]`; không gọi sync action thành công
    Evidence: .omo/evidence/task-7-auth-deny.png
  ```

  **Commit**: YES | Message: `feat(admin): add base services and permission guards` | Files: `apps/admin/**`

- [x] 8. Xây màn hình admin sync menu và i18n với modal service policy

  **What to do**: Tạo các page/card/action cho sync menu và sync i18n; dùng `NzModalService` cho confirm modal trước khi sync, hiển thị summary `created/updated/skipped/errors`, loading state, success/error notification, và cho phép rerun; tách feature service gọi hai endpoint sync đã khóa; gắn selector test bắt buộc cho button/modal/summary.
  **Must NOT do**: Không trigger sync trực tiếp không confirm; không dùng modal boolean nội bộ; không để page truy cập được nếu thiếu permission.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: UI flow + modal/feedback.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[security-review]` - không phải audit bảo mật tổng thể.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 10, 11, 12 | Blocked By: 4, 5, 6, 7

  **References**:
  - External: `https://ng.ant.design/components/modal/en` - modal service usage.
  - External: `https://ng.ant.design/docs/global-config/en` - config feedback components.
  - Pattern: `app/presentation/api/v1/auth.py` - response handling style tương thích backend.

  **Acceptance Criteria**:
  - [x] Page `/config/menu-sync` render selector `[data-testid="menu-sync-page"]`; page `/config/i18n-sync` render selector `[data-testid="i18n-sync-page"]`.
  - [x] Nút `[data-testid="sync-menu-button"]` và `[data-testid="sync-i18n-button"]` luôn mở `[data-testid="sync-confirm-modal"]` trước khi gọi API.
  - [x] Sau sync thành công, UI render `[data-testid="sync-summary-created"]`, `[data-testid="sync-summary-updated"]`, `[data-testid="sync-summary-skipped"]`.

  **Execution Notes**:
  - Đã thêm `SyncSummary` model, `AdminConfigSyncService`, `SyncConfirmDialogComponent`, và `SyncResourcePanelComponent` để gom chung UI/action flow cho cả menu sync và i18n sync.
  - `MenuSyncPageComponent` và `I18nSyncPageComponent` giờ render panel thật với các selector `menu-sync-page`, `i18n-sync-page`, `sync-menu-button`, `sync-i18n-button`.
  - Flow confirm được triển khai qua `NzModalService.create(...)`; modal content chứa selector `data-testid="sync-confirm-modal"`, không dùng `<nz-modal>` inline hay boolean modal state.
  - Sau khi confirm, UI gọi backend sync endpoint tương ứng, render summary cards `created/updated/skipped`, và hiển thị inline success/error feedback.
  - Để verify cả menu + i18n qua UI, frontend hiện trỏ `API_BASE_URL` tới local backend process `http://127.0.0.1:8010/api/v1`; việc chuẩn hóa origin/proxy dev sẽ được chốt ở task 11.
  - Đã verify pass bằng Playwright manual QA: admin session mở `/config/menu-sync` và `/config/i18n-sync`, nút sync mở modal confirm, confirm thành công, summary xuất hiện với `created/updated/skipped` (`menu: 0/0/4`, `i18n: 0/0/8` trên rerun).

  **QA Scenarios**:
  ```
  Scenario: Sync UI happy path
    Tool: Playwright
    Steps: login admin; mở page sync; bấm nút sync; assert modal xuất hiện; confirm; chờ response
    Expected: modal mở/đóng đúng; request gửi tới đúng endpoint; ba selector summary xuất hiện với giá trị số
    Evidence: .omo/evidence/task-8-sync-ui.png

  Scenario: API lỗi hiển thị graceful error
    Tool: Playwright
    Steps: mock hoặc dùng fixture API trả 4xx/500; thực hiện flow sync
    Expected: UI hiện notification lỗi; loading kết thúc; modal cleanup hoàn tất; không xuất hiện summary success selector
    Evidence: .omo/evidence/task-8-sync-ui-error.png
  ```

  **Commit**: YES | Message: `feat(admin): add sync control pages` | Files: `apps/admin/**`

- [x] 9. Viết test backend cho menu/i18n sync và permission enforcement

  **What to do**: Bổ sung `pytest` unit/integration cho menu sync và i18n sync: unauthorized `401`, forbidden `403`, success summary, rerun idempotent, duplicate key, invalid JSON, missing locale key, concurrency/transaction behavior; dùng seed-loader abstraction với override `SYNC_SEED_DIR` hoặc dependency override tương đương để nạp fixture test lỗi; bám pattern test hiện có trong `tests/integration` và `tests/unit`.
  **Must NOT do**: Không chỉ test happy path; không test qua route mà bỏ trống use case; không để test phụ thuộc thứ tự chạy.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: test backend nhiều lớp và nhiều edge case.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-pr-review]` - không review PR.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 11, 12 | Blocked By: 4, 5, 7

  **References**:
  - Test: `tests/integration/test_auth.py` - integration route test pattern.
  - Test: `tests/integration/conftest.py` - fixture AsyncClient.
  - Test: `tests/unit/domain/test_rbac_service.py` - đơn vị test domain pattern.
  - Pattern: `pytest.ini` - test discovery config.

  **Acceptance Criteria**:
  - [x] Có test cho `401`, `403`, success, rerun no-duplicate, invalid payload.
  - [x] Có ít nhất một test chứng minh summary `created/updated/skipped/errors` đúng format.
  - [x] Các test mới chạy được bằng `DATABASE_URL=... .venv/bin/pytest tests/unit tests/integration -v` hoặc target chi tiết tương đương.

  **Execution Notes**:
  - Đã mở rộng `tests/integration/test_menu_sync.py` và `tests/integration/test_i18n_sync.py` với các case `invalid token -> 401`, `dry_run` summary shape, và assert đầy đủ các key `resource/created/updated/skipped/errors/dry_run`.
  - Đã thêm `tests/unit/application/test_admin_config_loader_integration.py` dùng `AdminConfigSeedLoader` thật + override `SYNC_SEED_DIR` để kiểm chứng fixture invalid JSON và missing locale key mà không đổi API contract.
  - Bộ unit hiện cover: fake use-case behavior (create/rerun/dry-run/permission), real seed-loader override behavior, malformed seed, duplicate locale key, missing cross-locale key.
  - Đã verify pass: `.venv/bin/pytest -q tests/unit/application/test_menu_sync_use_case.py tests/unit/application/test_i18n_sync_use_case.py tests/unit/application/test_admin_config_loader_integration.py` → `14 passed`; `ADMIN_API_BASE_URL=http://127.0.0.1:8010 .venv/bin/pytest -q tests/integration/test_menu_sync.py tests/integration/test_i18n_sync.py` → `10 passed`.

  **QA Scenarios**:
  ```
  Scenario: Chạy backend sync tests thành công
    Tool: Bash
    Steps: chạy pytest target cho menu/i18n sync unit + integration tests với `DATABASE_URL` như Makefile và `SYNC_SEED_DIR` trỏ tới fixture test khi cần
    Expected: tất cả test mới pass
    Evidence: .omo/evidence/task-9-pytest.txt

  Scenario: Unauthorized và forbidden được kiểm chứng rõ ràng
    Tool: Bash
    Steps: chạy riêng test cases `401` và `403` dùng no-token, invalid-token, manager-token
    Expected: route sync trả đúng mã lỗi theo fixture user/token
    Evidence: .omo/evidence/task-9-authz.txt
  ```

  **Commit**: YES | Message: `test(rbac): add sync api coverage` | Files: `tests/**`

- [x] 10. Viết frontend unit tests và Playwright e2e cho shell/auth/sync flows

  **What to do**: Setup frontend unit test runner và script chính xác `npm run test:unit`; viết test cho `BaseApiService`, auth/permission guards, modal policy nếu khả thi; setup Playwright cho login flow, permission guard, shell render, sync success/error, modal cleanup on route change; thêm script `npm run e2e`.
  **Must NOT do**: Không test boilerplate vô nghĩa; không bỏ e2e unauthorized/forbidden; không để Playwright phụ thuộc dữ liệu không seed được.

  **Recommended Agent Profile**:
  - Category: `visual-engineering` - Reason: UI/e2e focus với guard/service behavior.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-debugging]` - không phải bug hunt.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 11, 12 | Blocked By: 4, 5, 6, 7, 8

  **References**:
  - External: `https://angular.dev/tools/cli/build` - scripts/build assumptions.
  - Pattern: `tests/integration/conftest.py` - backend fixtures có thể tái dùng cho e2e env setup.

  **Acceptance Criteria**:
  - [x] Có unit tests cho guard/service quan trọng.
  - [x] Có Playwright specs cho shell render, authorized sync, forbidden sync, error UI.
  - [x] `npm run test:unit` và `npm run e2e` chạy được từ `apps/admin` với exit code 0 khi suite pass.

  **Execution Notes**:
  - Đã thêm unit tests: `src/app/services/auth-store.service.spec.ts`, `src/app/core/guards/auth.guard.spec.ts`; đồng thời cập nhật `src/app/app.spec.ts` cho shell mới.
  - Đã thay `e2e/admin.spec.ts` bằng các flow thật: render shell sau login, manager bị chặn route sync, menu sync thành công, i18n sync error UI, và modal cleanup khi đổi route.
  - `playwright.config.ts` giờ tự khởi động backend local `8010` và frontend `4200`, chạy tuần tự (`workers: 1`) để tránh state race khi thao tác chung DB/API.
  - Đã verify pass: `npm run test:unit` → `3 files / 6 tests passed`; `npm run e2e` → `5 passed`.

  **QA Scenarios**:
  ```
  Scenario: Frontend automated tests pass
    Tool: Bash
    Steps: chạy `npm run test:unit` và `npm run e2e` trong `apps/admin`
    Expected: cả hai command exit code 0 và log không có failed spec
    Evidence: .omo/evidence/task-10-frontend-tests.txt

  Scenario: Modal cleanup khi đổi route
    Tool: Playwright
    Steps: mở confirm modal sync; điều hướng khỏi page trước khi confirm hoàn tất
    Expected: modal được cleanup đúng, không còn overlay treo hoặc console error
    Evidence: .omo/evidence/task-10-modal-cleanup.png
  ```

  **Commit**: YES | Message: `test(admin): add ui guard and sync coverage` | Files: `apps/admin/**`

- [x] 11. Hardening edge cases, seed vận hành và tích hợp end-to-end

  **What to do**: Xử lý/cố định các edge case cuối: duplicate permission key, duplicate route, missing locale key, invalid JSON, parent-child permission mismatch, concurrent sync request, rollback semantics, và `dry_run=true` no-write semantics; chuẩn hóa script/command để seed + sync trong local/dev/test; cấu hình frontend gọi backend qua base URL/proxy rõ ràng cho local.
  **Must NOT do**: Không để behavior mập mờ khi sync đồng thời; không che giấu key lỗi; không bỏ qua dev-proxy/CORS nếu frontend cần gọi backend từ port khác.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: hardening cross-layer.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[security-research]` - không mở rộng sang audit bảo mật đầy đủ.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 13 | Blocked By: 8, 9, 10

  **References**:
  - Pattern: `app/main.py` - CORS/app wiring.
  - Pattern: `app/core/config.py` - config/env style.
  - Pattern: `docker-compose.yml` - local orchestration nếu cần test tích hợp.

  **Acceptance Criteria**:
  - [x] Duplicate/invalid/concurrent sync đều có response code cụ thể; riêng concurrent sync phải trả `409 Conflict` với `errors[]`.
  - [x] `dry_run=true` trả summary dự kiến nhưng không tạo bất kỳ DB write nào.
  - [x] Frontend dev server gọi `http://localhost:8000` hoặc proxy tương đương đã chốt mà không lỗi CORS trong local verify.
  - [x] Có command local/dev/test để tái lập full flow.

  **Execution Notes**:
  - Đã thêm `app/presentation/api/v1/sync_runtime.py` với `SyncExecutionRegistry` để chặn sync đồng thời theo từng resource (`menu`, `i18n`) một cách atomic, không block chờ lock.
  - `menu_sync.py` và `i18n_sync.py` giờ trả `409` với summary `{ errors: ["sync already in progress"] }` khi request thứ hai đến trong lúc request đầu đang chạy; đồng thời có hook `SYNC_TEST_DELAY_MS` để verify overlap deterministically ở local/test.
  - Dry-run semantics giữ nguyên ở use case layer và đã được giữ dưới route locking mới; unit tests + loader override tests vẫn pass sau hardening.
  - Frontend local wiring được chốt bằng explicit `API_BASE_URL = http://127.0.0.1:8010/api/v1` trong app config để dev/e2e gọi backend khác port mà không bị browser chặn CORS; phương án proxy Angular đã được thử nhưng dev-server stack hiện tại không áp dụng đúng cho API POST.
  - Đã verify pass: `.venv/bin/pytest -q tests/unit/application/test_sync_runtime.py tests/unit/application/test_menu_sync_use_case.py tests/unit/application/test_i18n_sync_use_case.py tests/unit/application/test_admin_config_loader_integration.py` → `15 passed`; `ADMIN_API_BASE_URL=http://127.0.0.1:8010 .venv/bin/pytest -q tests/integration/test_menu_sync.py tests/integration/test_i18n_sync.py` → `10 passed`; live concurrency probe trên backend `8012` trả một `200` và một `409` với body `sync already in progress`.

  **QA Scenarios**:
  ```
  Scenario: Concurrent sync không làm bẩn dữ liệu
    Tool: Bash
    Steps: bắn hai request sync gần đồng thời cho cùng resource bằng admin token
    Expected: dữ liệu DB không duplicate/corrupt; đúng một request commit, request còn lại trả `409 Conflict` với `errors[]` chứa thông báo sync đang chạy
    Evidence: .omo/evidence/task-11-concurrency.txt

  Scenario: Frontend gọi backend qua dev config thành công
    Tool: Playwright
    Steps: chạy backend ở `localhost:8000`, chạy `npm run dev` cho frontend; thao tác sync từ UI
    Expected: request đi đúng origin/proxy đã cấu hình và không bị browser chặn CORS
    Evidence: .omo/evidence/task-11-dev-proxy.png
  ```

  **Commit**: YES | Message: `fix(admin): harden sync edge cases` | Files: `app/**`, `apps/admin/**`, `tests/**`

- [x] 12. Chuẩn hóa tài liệu vận hành và command xác minh cho executor

  **What to do**: Ghi rõ command cài dependency, chạy backend/frontend, chạy migration, seed/sync, unit tests, Playwright, và build production; thêm hướng dẫn fixture user có/không có `system.config.manage`; ghi rõ vị trí `menu.json`, `vi.json`, `en.json`, cùng output mong đợi của API summary.
  **Must NOT do**: Không để câu chữ mơ hồ như “chạy test như bình thường”; không bỏ sót command cho CI/manual verify; không dùng command giả định ngoài repo state.

  **Recommended Agent Profile**:
  - Category: `writing` - Reason: tài liệu vận hành cần rõ, chính xác, thực thi được.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[gitnexus-cli]` - không thao tác index/CLI GitNexus.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 13 | Blocked By: 8, 9, 10

  **References**:
  - Pattern: `Makefile` - command style hiện có cho backend.
  - Pattern: `pytest.ini` - test target backend.
  - External: `https://angular.dev/tools/cli/build` - build command semantics.

  **Acceptance Criteria**:
  - [x] Có danh sách command copy-paste chạy được gồm `make up`, `make seed`, `npm install`, `npm run dev`, `npm run build`, `npm run test:unit`, `npm run e2e`, và lệnh pytest chi tiết.
  - [x] Có mô tả fixture/quyền cần dùng cho verify.
  - [x] Có expected output summary cho sync APIs.

  **Execution Notes**:
  - Đã thay `apps/admin/README.md` bằng runbook thực tế cho frontend: install, local backend `8010`, frontend dev `4200`, build/test/e2e/modal-policy, fixture user authz, protected routes, và response shape.
  - Đã thêm `docs/admin-sync-operations.md` chứa full operator checklist: `make up`, `make seed`, `alembic upgrade/current`, local uvicorn command, frontend commands, pytest targets, fixture user matrix, seed asset paths, API request/response examples, và concurrent sync probe.
  - Nội dung docs được bám đúng command đã chạy thật trong workspace thay vì boilerplate Angular CLI mặc định.

  **QA Scenarios**:
  ```
  Scenario: Command checklist chạy được tuần tự
    Tool: Bash
    Steps: thực thi lần lượt checklist command đã tài liệu hóa trên môi trường local/test
    Expected: không có bước mơ hồ hoặc thiếu prerequisite
    Evidence: .omo/evidence/task-12-command-checklist.txt

  Scenario: Tài liệu phân biệt rõ user có quyền và không có quyền
    Tool: Bash
    Steps: review markdown/checklist và map với fixture test thực tế
    Expected: executor có thể lặp lại đúng hai trường hợp authz mà không đoán thêm
    Evidence: .omo/evidence/task-12-authz-docs.txt
  ```

  **Commit**: YES | Message: `docs(admin): add execution and verification guide` | Files: `apps/admin/**`, `docs/**`, `README snippets if needed`

- [x] 13. Chạy full verification wave trước khi bàn giao cho user

  **What to do**: Chạy trọn bộ build/test/pytest/e2e và kiểm tra DB/API/UI evidence; tổng hợp kết quả theo checklist thành một báo cáo ngắn để làm đầu vào cho Final Verification Wave F1-F4.
  **Must NOT do**: Không bỏ qua failed test; không mark xong nếu còn flaky case; không thiếu evidence file cho task trước.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` - Reason: tổng hợp và xác minh cuối nhiều lớp.
  - Skills: `[]` - không cần skill riêng.
  - Omitted: `[momus]` - chỉ dùng nếu user chọn high accuracy review sau đó.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: F1, F2, F3, F4 | Blocked By: 11, 12

  **References**:
  - Pattern: `Makefile` - backend verification commands.
  - Pattern: `apps/admin` scripts - frontend verification commands sau khi được thêm.

  **Acceptance Criteria**:
  - [x] Build frontend pass.
  - [x] Frontend unit tests pass.
  - [x] Playwright e2e pass.
  - [x] Backend pytest sync tests pass.
  - [x] Evidence files tồn tại cho tất cả task đã định nghĩa.

  **Execution Notes**:
  - Đã chạy lại full verification sweep cuối cùng theo trạng thái code hiện tại.
  - Frontend: `npm run build`, `npm run test:unit`, `npm run e2e`, `npm run check:modal-policy` đều pass trong `apps/admin`.
  - Backend sync: `.venv/bin/pytest -q tests/unit/application/test_menu_sync_use_case.py tests/unit/application/test_i18n_sync_use_case.py tests/unit/application/test_admin_config_loader_integration.py tests/unit/application/test_sync_runtime.py` → `15 passed`; `ADMIN_API_BASE_URL=http://127.0.0.1:8010 .venv/bin/pytest -q tests/integration/test_menu_sync.py tests/integration/test_i18n_sync.py` → `10 passed`.
  - Manual browser/API QA đã được thực hiện trước đó trong cùng turn: unauthorized/forbidden/authorized route flows, menu sync UI, i18n sync UI, and concurrent sync `409` conflict probe.

  **QA Scenarios**:
  ```
  Scenario: Full verification pass
    Tool: Bash
    Steps: chạy toàn bộ command build/test/e2e/pytest theo checklist cuối
    Expected: tất cả pass, có evidence output đầy đủ
    Evidence: .omo/evidence/task-13-full-verify.txt

  Scenario: Nếu một lớp verify fail thì bàn giao bị chặn
    Tool: Bash
    Steps: cố tình chạy khi một test suite còn fail hoặc thiếu evidence
    Expected: quy trình báo fail và không được chuyển sang complete state
    Evidence: .omo/evidence/task-13-gate-fail.txt
  ```

  **Commit**: NO | Message: `n/a` | Files: `n/a`

## Final Verification Wave (MANDATORY — after ALL implementation tasks)
> 4 review agents run in PARALLEL. ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
> **Do NOT auto-proceed after verification. Wait for user's explicit approval before marking work complete.**
> **Never mark F1-F4 as checked before getting user's okay.** Rejection or user feedback -> fix -> re-run -> present again -> wait for okay.
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit 1: `feat(admin): scaffold angular admin workspace`
- Commit 2: `feat(rbac): add menu and i18n sync backend`
- Commit 3: `feat(admin): add sync dashboard and permission guards`
- Commit 4: `test(admin): add frontend and backend verification coverage`

## Success Criteria
- Admin shell render đúng cấu trúc và responsive.
- User không có `system.config.manage` không thể truy cập hoặc trigger sync.
- Menu/i18n sync chạy nhiều lần không tạo duplicate.
- Modal flow thống nhất qua `NzModalService`.
- Frontend/backend test suite chứng minh đúng happy path + failure path.
