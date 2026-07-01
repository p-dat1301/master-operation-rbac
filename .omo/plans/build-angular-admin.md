# Xây dựng Admin Frontend Angular 21

## TL;DR
> **Tóm tắt**: Xây dựng admin frontend Angular 21 đầy đủ tính năng (`frontend/admin/`) với TailwindCSS + ng-zorro-antd, layout Ant Design Pro, quản lý menu/i18n có thể chỉnh sửa đồng bộ với backend FastAPI, và các trang CRUD cho users, roles, permissions, và departments.
> **Bàn giao**: Angular admin SPA, backend Menu + Translation APIs, seed data, Alembic migrations
> **Nỗ lực**: Lớn
> **Song song**: CÓ - 6 giai đoạn
> **Đường găng**: Backend APIs (Giai đoạn 1) → Frontend Shell (Giai đoạn 3) → Trang CRUD (Giai đoạn 4-5)

## Bối cảnh

### Yêu cầu ban đầu
Xây dựng frontend admin với:
- Angular 21, TailwindCSS ưu tiên, Ant Design admin pro layout
- Kiểm soát hoàn toàn ng-zorro-antd (sử dụng component trực tiếp, không wrapper)
- Service base + models pattern
- Modal: chỉ sử dụng `NzModalService`
- Menu seed `menu.json` với permission key, đồng bộ vào DB
- i18n: seed `vi.json` + `en.json` trong backend API, admin xây dựng chức năng đồng bộ DB

### Tóm tắt phỏng vấn
- **Menu**: Admin frontend có trang Menu Management có thể chỉnh sửa. Backend seed `menu.json` vào DB khi khởi động. Frontend đọc menu từ API, có thể chỉnh sửa và đồng bộ lại.
- **i18n**: Backend seed `vi.json` + `en.json` vào DB. Admin frontend có trang i18n Management để xem/chỉnh sửa translations và đồng bộ vào DB. Frontend load translations từ API khi chạy.
- **Phạm vi**: Framework shell + đầy đủ trang CRUD cho Users, Roles, Permissions, Departments.
- **Cấu trúc dự án**: Thư mục con `frontend/admin/` trong monorepo.

### Metis Review (các khoảng trống đã xử lý)
- **Backend menu/i18n APIs chưa tồn tại** → Thêm vào Giai đoạn 1
- **Backend role/permission GET APIs chưa tồn tại** → Sẽ xây dựng nhanh trong Giai đoạn 1 (theo pattern `departments.py`)
- **Chưa có test infra frontend** → Bao gồm Angular test setup (Jasmine/Karma) trong Giai đoạn 2
- **Token refresh chưa xác định** → Quyết định: chuyển hướng đến login khi 401 (backend chưa hỗ trợ refresh token)
- **State management** → Quyết định: RxJS BehaviorSubject services (nhẹ, không cần NgRx cho quy mô này)
- **Thư viện i18n** → Quyết định: `@ngx-translate/core` với custom loader từ API (cho phép chỉnh sửa translation runtime)
- **Lọc menu theo permission** → Menu items được lọc bởi mảng `permissions` của user từ `/api/v1/auth/me`

## Mục tiêu công việc

### Mục tiêu cốt lõi
Bàn giao admin panel Angular 21 sẵn sàng production với:
1. JWT auth (login, guards, interceptors)
2. Ant Design Pro layout (sidebar có thể thu gọn, header, content, footer)
3. Menu động từ API với hiển thị theo permission
4. i18n runtime từ API với language switcher
5. Trang Menu Management (CRUD menu items, đồng bộ DB)
6. Trang i18n Management (CRUD translations, đồng bộ DB)
7. Trang CRUD User/Role/Permission/Department

### Bàn giao
1. `frontend/admin/` - Dự án Angular 21 với toàn bộ source code
2. Backend Menu API (`/api/v1/menus/*`)
3. Backend Translation API (`/api/v1/translations/*`)
4. Alembic migration cho bảng `menus` và `translations`
5. File seed: `app/infrastructure/database/seeds/menu.json`, `vi.json`, `en.json`
6. Cập nhật `seed.py` để seed menu + translations

### Định nghĩa hoàn thành
- [ ] Admin frontend build thành công (`ng build --configuration production`)
- [ ] Login hoạt động với backend JWT (`admin@company.vn` / `Admin@123`)
- [ ] Menu render từ API, được lọc theo permissions
- [ ] Language switcher (VI/EN) hoạt động trên tất cả trang
- [ ] Menu Management CRUD đồng bộ vào DB
- [ ] i18n Management CRUD đồng bộ vào DB
- [ ] Trang User/Role/Permission/Department có CRUD hoạt động với modals
- [ ] Tất cả modals sử dụng `NzModalService.create()` (không có `<nz-modal>` trong template)
- [ ] Tất cả thao tác async hiển thị trạng thái loading
- [ ] Backend APIs trả về JSON đúng và được ghi trong plan

### Phải có
- Angular 21 standalone components xuyên suốt
- TailwindCSS cho custom styling + ng-zorro-antd cho components
- Service base pattern: generic `ApiService<T>` với xử lý lỗi
- TypeScript models phản ánh backend entities
- `NzModalService` cho TẤT CẢ modals
- Reactive forms cho TẤT CẢ form inputs
- Route guards và hiển thị menu theo permission
- Toggle dark/light theme trên sidebar
- Responsive layout (sidebar thu gọn trên mobile)

### KHÔNG được có (rào chắn)
- Không wrapper/abstraction xung quanh ng-zorro components (dùng trực tiếp)
- Không template-driven forms
- Không `<nz-modal>` trong templates
- Không NgRx hay Akita (RxJS services là đủ)
- Không SSR (admin panel không cần SEO)
- Không e2e tests (chỉ unit tests trong giai đoạn này)
- Không trang quản lý task/leave/attendance (ngoài phạm vi)

## Chiến lược kiểm thử
> KHÔNG CẦN CAN THIỆP NGƯỜI - tất cả kiểm thử do agent thực hiện.
- **Quyết định test**: tests-after (Angular mặc định Jasmine/Karma) + agent QA scenarios
- **Chính sách QA**: Mỗi task có agent-executed scenarios
- **Bằng chứng**: `.omo/evidence/task-{N}-{slug}.{ext}`

## Chiến lược thực thi

### Các giai đoạn thực thi song song
> Mục tiêu: 5-8 task mỗi giai đoạn. Tách dependencies chung thành Giai đoạn-1 để tối đa song song.

**Giai đoạn 1: Nền tảng Backend** (4 task + 2 bổ sung nhanh)
API backend và schema database cho menu, i18n, roles, và permissions. Lưu ý: endpoints role/permission GET còn thiếu và sẽ được xây dựng nhanh trong tiên quyết của task 15 và 16.

**Giai đoạn 2: Thiết lập Frontend** (4 task)
Dự án Angular CLI, dependencies, core module, auth.

**Giai đoạn 3: Admin Shell** (3 task)
Layout, menu service, i18n service.

**Giai đoạn 4: Trang Quản lý** (4 task)
Menu management, i18n management, user CRUD, role CRUD.

**Giai đoạn 5: Trang Còn lại** (3 task)
Permission view, department CRUD, dashboard.

**Giai đoạn 6: Kiểm thử Cuối cùng** (4 task)
Compliance audit, code quality, manual QA, scope check.

### Ma trận phụ thuộc
| Task | Chặn | Bị chặn bởi |
|------|------|------------|
| B1-B4 (Backend) | F5-F14 | - |
| F1-F2 (Setup) | F3-F14 | - |
| F3 (Auth) | F5-F14 | F1-F2 |
| F4 (Models) | F5-F14 | - |
| F5 (Layout) | F8-F14 | F1-F4, B1-B4 |
| F6 (Menu svc) | F8, F5 | F1-F4, B1-B4 |
| F7 (i18n svc) | F9, F5 | F1-F4, B1-B4 |
| F8-F14 (Pages) | V1-V4 | F5-F7 |
| V1-V4 (Verify) | - | F8-F14 |

### Tóm tắt phân công Agent
| Giai đoạn | Tasks | Categories chính |
|-----------|-------|-----------------|
| 1 | 4 | quick + unspecified-high |
| 2 | 4 | visual-engineering + quick |
| 3 | 3 | visual-engineering |
| 4 | 4 | visual-engineering |
| 5 | 3 | visual-engineering |
| 6 | 4 | unspecified-high + deep |

## TODOs

### Giai đoạn 1: Nền tảng Backend

- [ ] 1. Tạo Alembic migration cho bảng `menus` và `translations`

  **Việc cần làm**: Tạo migration Alembic mới thêm hai bảng:
  - `menus` (id, key, parent_id, title_vi, title_en, icon, path, permission_code, sort_order, is_active, created_at, updated_at)
  - `translations` (id, key, language, value, module, created_at, updated_at) với ràng buộc duy nhất trên (key, language)
  **KHÔNG được làm**: KHÔNG sửa đổi bảng hiện có. KHÔNG xóa dữ liệu hiện có.

  **Agent Profile đề xuất**:
  - Category: `quick` - Lý do: thay đổi schema database, đã xác định rõ
  - Skills: [] - pure Alembic/SQLAlchemy

  **Song song**: Chạy song song: CÓ | Giai đoạn 1 | Chặn: 2, 3 | Bị chặn bởi: -

  **Tham chiếu**:
  - Pattern: `alembic/versions/388ec37210d1_init_all_tables.py` - theo style migration hiện có
  - Model: `app/infrastructure/database/models/permission_model.py` - theo style Mapped/mapped_column
  - Base: `app/infrastructure/database/base.py`

  **Tiêu chí chấp nhận**:
  - [ ] Migration file tồn tại tại `alembic/versions/{revision}_add_menus_and_translations.py`
  - [ ] `alembic upgrade head` thành công không lỗi
  - [ ] Bảng `menus` và `translations` tồn tại trong PostgreSQL với đúng cột
  - [ ] `alembic downgrade -1` xóa sạch cả hai bảng

  **Kịch bản QA**:
  ```
  Scenario: Migration áp dụng sạch sẽ
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation && docker-compose up -d db && alembic upgrade head
    Expected: Exit code 0, không có lỗi
    Evidence: .omo/evidence/task-1-migration.log

  Scenario: Bảng tạo với schema đúng
    Tool: Bash
    Steps: docker exec masterop_db psql -U postgres -d masterop -c "\dt menus translations"
    Expected: Cả hai bảng được liệt kê
    Evidence: .omo/evidence/task-1-tables.log
  ```

  **Commit**: CÓ | Message: `feat(db): add menus and translations tables` | Files: `alembic/versions/*_add_menus_and_translations.py`

- [ ] 2. Xây dựng backend Menu: model, entity, repository, schema, API routes

  **Việc cần làm**:
  1. Tạo `app/domain/entities/menu.py` - Menu dataclass với fields: id, key, parent_id, title_vi, title_en, icon, path, permission_code, sort_order, is_active, children (list)
  2. Tạo `app/infrastructure/database/models/menu_model.py` - SQLAlchemy model với self-referential relationship cho cấu trúc cây
  3. Tạo `app/infrastructure/database/repositories/sqlalchemy_menu_repo.py` - async CRUD repo
  4. Tạo `app/presentation/schemas/menu_schema.py` - Pydantic schemas: MenuResponse, MenuCreateRequest, MenuUpdateRequest
  5. Tạo `app/presentation/api/v1/menus.py` - FastAPI router với endpoints:
     - GET /api/v1/menus (list all, tree structure)
     - GET /api/v1/menus/{id}
     - POST /api/v1/menus (admin only - check `manage_org` permission)
     - PUT /api/v1/menus/{id}
     - DELETE /api/v1/menus/{id}
  6. Kết nối router trong `app/main.py`
  7. Tạo `app/domain/repositories/menu_repository.py` - abstract repo interface
  **KHÔNG được làm**: KHÔNG implement pagination cho menus (tập dữ liệu nhỏ). KHÔNG thêm search/filter phức tạp.

  **Agent Profile đề xuất**:
  - Category: `unspecified-high` - Lý do: phát triển backend API với clean architecture
  - Skills: [] - standard FastAPI/SQLAlchemy patterns

  **Song song**: Chạy song song: CÓ | Giai đoạn 1 | Chặn: 9, 12 | Bị chặn bởi: 1

  **Tham chiếu**:
  - Pattern: `app/infrastructure/database/models/permission_model.py` - theo style Mapped
  - Pattern: `app/infrastructure/database/repositories/sqlalchemy_permission_repo.py` - theo pattern repo
  - Pattern: `app/presentation/api/v1/departments.py` - theo pattern router
  - Pattern: `app/presentation/schemas/user_schema.py` - theo pattern schema
  - Entity: `app/domain/entities/permission.py` - theo style dataclass
  - Auth: `app/presentation/dependencies/auth_deps.py` - dùng `get_current_user`

  **Tiêu chí chấp nhận**:
  - [ ] GET /api/v1/menus trả về JSON dạng cây (children lồng nhau)
  - [ ] POST /api/v1/menus tạo menu item (test với admin token)
  - [ ] PUT /api/v1/menus/{id} cập nhật fields
  - [ ] DELETE /api/v1/menus/{id} xóa item và cascade xuống children (hoặc ngăn nếu có children)
  - [ ] Routes được bảo vệ bởi dependency `get_current_user`

  **Kịch bản QA**:
  ```
  Scenario: Liệt kê menus dạng cây
    Tool: Bash
    Steps: curl -s http://localhost:8000/api/v1/menus | python3 -m json.tool
    Expected: Trả về JSON array với children lồng nhau
    Evidence: .omo/evidence/task-2-list-menus.json

  Scenario: Tạo menu item
    Tool: Bash
    Steps: curl -s -X POST http://localhost:8000/api/v1/menus -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_TOKEN" -d '{"key":"users","title_vi":"Nguoi dung","title_en":"Users","path":"/admin/users","permission_code":"manage_org","sort_order":1}'
    Expected: Trả về menu đã tạo với id, status 200
    Evidence: .omo/evidence/task-2-create-menu.json
  ```

  **Commit**: CÓ | Message: `feat(api): add menu CRUD endpoints` | Files: `app/domain/entities/menu.py`, `app/domain/repositories/menu_repository.py`, `app/infrastructure/database/models/menu_model.py`, `app/infrastructure/database/repositories/sqlalchemy_menu_repo.py`, `app/presentation/schemas/menu_schema.py`, `app/presentation/api/v1/menus.py`, `app/main.py`

- [ ] 3. Xây dựng backend Translation/i18n: model, entity, repository, schema, API routes

  **Việc cần làm**:
  1. Tạo `app/domain/entities/translation.py` - Translation dataclass: id, key, language, value, module, created_at, updated_at
  2. Tạo `app/infrastructure/database/models/translation_model.py` - SQLAlchemy model với ràng buộc duy nhất trên (key, language)
  3. Tạo `app/infrastructure/database/repositories/sqlalchemy_translation_repo.py` - async CRUD repo với bulk operations
  4. Tạo `app/presentation/schemas/translation_schema.py` - Pydantic schemas: TranslationResponse, TranslationCreateRequest, TranslationUpdateRequest, TranslationBulkRequest
  5. Tạo `app/presentation/api/v1/translations.py` - FastAPI router với endpoints:
     - GET /api/v1/translations?language=vi (list theo language)
     - GET /api/v1/translations/{id}
     - POST /api/v1/translations (admin only)
     - PUT /api/v1/translations/{id}
     - DELETE /api/v1/translations/{id}
     - POST /api/v1/translations/sync (bulk upsert từ JSON payload - cho admin sync)
  6. Kết nối router trong `app/main.py`
  7. Tạo `app/domain/repositories/translation_repository.py` - abstract repo interface
  **KHÔNG được làm**: KHÔNG thêm fuzzy search. KHÔNG implement translation fallback logic trong backend (frontend xử lý).

  **Agent Profile đề xuất**:
  - Category: `unspecified-high` - Lý do: backend API với bulk sync feature
  - Skills: [] - standard FastAPI/SQLAlchemy patterns

  **Song song**: Chạy song song: CÓ | Giai đoạn 1 | Chặn: 10, 13 | Bị chặn bởi: 1

  **Tham chiếu**:
  - Pattern: `app/infrastructure/database/models/permission_model.py`
  - Pattern: `app/infrastructure/database/repositories/sqlalchemy_permission_repo.py`
  - Pattern: `app/presentation/api/v1/departments.py`
  - Pattern: `app/domain/entities/permission.py`

  **Tiêu chí chấp nhận**:
  - [ ] GET /api/v1/translations?language=vi trả về tất cả VI translations dạng key-value pairs
  - [ ] POST /api/v1/translations/sync chấp nhận array và upsert hàng loạt
  - [ ] Ràng buộc duy nhất ngăn chặn duplicate (key, language)
  - [ ] Routes được bảo vệ bởi `get_current_user`

  **Kịch bản QA**:
  ```
  Scenario: Đồng bộ translations hàng loạt
    Tool: Bash
    Steps: curl -s -X POST http://localhost:8000/api/v1/translations/sync -H "Content-Type: application/json" -H "Authorization: Bearer $ADMIN_TOKEN" -d '{"translations":[{"key":"users.title","language":"vi","value":"Nguoi dung","module":"admin"},{"key":"users.title","language":"en","value":"Users","module":"admin"}]}'
    Expected: Trả về success với count, status 200
    Evidence: .omo/evidence/task-3-sync-translations.json

  Scenario: Liệt kê VI translations
    Tool: Bash
    Steps: curl -s "http://localhost:8000/api/v1/translations?language=vi" | python3 -m json.tool
    Expected: Trả về array của translations với language="vi"
    Evidence: .omo/evidence/task-3-list-vi.json
  ```

  **Commit**: CÓ | Message: `feat(api): add translation CRUD and sync endpoints` | Files: `app/domain/entities/translation.py`, `app/domain/repositories/translation_repository.py`, `app/infrastructure/database/models/translation_model.py`, `app/infrastructure/database/repositories/sqlalchemy_translation_repo.py`, `app/presentation/schemas/translation_schema.py`, `app/presentation/api/v1/translations.py`, `app/main.py`

- [ ] 4. Tạo file seed (menu.json, vi.json, en.json) và cập nhật seed.py

  **Việc cần làm**:
  1. Tạo `app/infrastructure/database/seeds/menu.json` với cấu trúc menu ban đầu:
     - Dashboard (key: dashboard, path: /admin/dashboard, icon: dashboard, permission: null - hiển thị với tất cả)
     - System Management (key: system, icon: setting, children: Users, Roles, Permissions, Departments, Menu, i18n)
     - Mỗi menu item có permission_code khớp với permission codes hiện có (manage_org, etc.)
  2. Tạo `app/infrastructure/database/seeds/vi.json` với VI translations cho tất cả UI labels
  3. Tạo `app/infrastructure/database/seeds/en.json` với EN translations
  4. Cập nhật `app/infrastructure/database/seed.py` thêm hàm `_seed_menus()` và `_seed_translations()`
  5. Thêm gọi trong `seed_all()` cho menus và translations
  **KHÔNG được làm**: KHÔNG seed menu/translation data trong Alembic migration. Seeding phải tách biệt.

  **Agent Profile đề xuất**:
  - Category: `quick` - Lý do: file data và script update nhỏ
  - Skills: [] - chỉ định nghĩa data

  **Song song**: Chạy song song: CÓ | Giai đoạn 1 | Chặn: 9, 10 | Bị chặn bởi: 1

  **Tham chiếu**:
  - Seed: `app/infrastructure/database/seed.py` - theo pattern seed hiện có
  - Permissions: `app/infrastructure/database/seed.py:38-46` - tham chiếu permission codes cho menu
  - Menu API: `app/presentation/api/v1/menus.py` (từ task 2) - đảm bảo cấu trúc seed khớp API expectations

  **Tiêu chí chấp nhận**:
  - [ ] `menu.json` có ít nhất 7 item cấp cao bao gồm Dashboard, System Management với children
  - [ ] `vi.json` có ít nhất 50 translation keys bao phủ tất cả admin UI labels
  - [ ] `en.json` có keys khớp với giá trị tiếng Anh
  - [ ] `seed.py` chạy thành công và populate menus + translations tables

  **Kịch bản QA**:
  ```
  Scenario: Seed data populate đúng
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation && python -m app.infrastructure.database.seed
    Expected: In ra "[seed] menus OK" và "[seed] translations OK"
    Evidence: .omo/evidence/task-4-seed.log

  Scenario: Menu data trong DB
    Tool: Bash
    Steps: docker exec masterop_db psql -U postgres -d masterop -c "SELECT key, title_en, permission_code FROM menus ORDER BY sort_order"
    Expected: Hiển thị menu items với đúng keys và permissions
    Evidence: .omo/evidence/task-4-menu-db.log
  ```

  **Commit**: CÓ | Message: `feat(db): add menu and i18n seed data` | Files: `app/infrastructure/database/seeds/menu.json`, `app/infrastructure/database/seeds/vi.json`, `app/infrastructure/database/seeds/en.json`, `app/infrastructure/database/seed.py`

### Giai đoạn 2: Thiết lập Frontend

- [ ] 5. Khởi tạo dự án Angular 21 với TailwindCSS, ng-zorro-antd, ngx-translate

  **Việc cần làm**:
  1. Chạy `ng new frontend/admin --routing --style=scss --ssr=false` trong project root
  2. Thêm TailwindCSS: `npm install -D tailwindcss postcss autoprefixer` và tạo `tailwind.config.js`
  3. Thêm ng-zorro-antd: `ng add ng-zorro-antd` (chọn English hoặc VI locale)
  4. Thêm `@ngx-translate/core` và `@ngx-translate/http-loader` cho i18n
  5. Cấu hình `angular.json` proxy đến backend (`/api` → `http://localhost:8000`)
  6. Cập nhật `styles.scss` import Tailwind directives và ng-zorro theme
  7. Cập nhật `tsconfig.json` path aliases: `@core/*`, `@shared/*`, `@features/*`
  8. Tạo cấu trúc thư mục: `src/app/core/`, `src/app/shared/`, `src/app/features/`, `src/app/layout/`
  **KHÔNG được làm**: KHÔNG sử dụng Angular modules (NgModule). TẤT CẢ components phải standalone. KHÔNG cài NgRx hay state libraries khác.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: scaffolding frontend project
  - Skills: [] - standard Angular CLI setup

  **Song song**: Chạy song song: CÓ | Giai đoạn 2 | Chặn: 6, 7, 8, 9, 10, 11 | Bị chặn bởi: -

  **Tham chiếu**:
  - External: `https://ng.ant.design/docs/getting-started/en` - ng-zorro-antd setup guide
  - External: `https://tailwindcss.com/docs/guides/angular` - Tailwind + Angular guide
  - External: `https://github.com/ngx-translate/core` - ngx-translate setup

  **Tiêu chí chấp nhận**:
  - [ ] `ng serve` khởi động không lỗi trên port 4200
  - [ ] `ng build --configuration production` thành công
  - [ ] TailwindCSS utility classes hoạt động trong test component
  - [ ] ng-zorro button component render đúng
  - [ ] Path aliases resolve đúng trong imports

  **Kịch bản QA**:
  ```
  Scenario: Development server khởi động
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation/frontend/admin && npm install && ng serve --host 0.0.0.0 --port 4200 &
    Expected: Server khởi động, không có lỗi biên dịch, homepage truy cập được
    Evidence: .omo/evidence/task-5-ng-serve.log

  Scenario: Production build thành công
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation/frontend/admin && ng build --configuration production
    Expected: Exit code 0, thư mục dist/ được tạo
    Evidence: .omo/evidence/task-5-build.log
  ```

  **Commit**: CÓ | Message: `chore(admin): init Angular 21 project with Tailwind and ng-zorro` | Files: `frontend/admin/*`

- [ ] 6. Xây dựng Core module: base HTTP service, auth interceptor, error handler, loading interceptor

  **Việc cần làm**:
  1. Tạo `src/app/core/services/api.service.ts` - Generic base service:
     - `get<T>(url)`, `post<T>(url, body)`, `put<T>(url, body)`, `delete<T>(url)`
     - Base URL từ environment (`/api/v1`)
     - Xử lý lỗi: map HTTP errors sang thông báo thân thiện người dùng dùng `NzMessageService`
     - Loading state qua `BehaviorSubject<boolean>`
  2. Tạo `src/app/core/interceptors/auth.interceptor.ts` - Standalone interceptor:
     - Đọc token từ `localStorage.getItem('access_token')`
     - Thêm header `Authorization: Bearer ${token}`
     - Khi 401/403: clear token, chuyển hướng đến `/login`
  3. Tạo `src/app/core/interceptors/loading.interceptor.ts` - Show/hide global spinner
  4. Tạo `src/app/core/services/notification.service.ts` - Wrapper xung quanh `NzMessageService` và `NzNotificationService`
  5. Tạo `src/app/core/guards/auth.guard.ts` - Standalone route guard, kiểm tra token tồn tại
  6. Tạo `src/app/core/guards/permission.guard.ts` - Kiểm tra mảng `permissions` từ current user trước khi kích hoạt route
  7. Kết nối interceptors và guards trong `app.config.ts` dùng `provideHttpClient(withInterceptors([...]))`
  **KHÔNG được làm**: KHÔNG implement token refresh (backend chưa hỗ trợ). KHÔNG dùng `HttpClientModule` (deprecated, dùng `provideHttpClient`).

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: core Angular services và interceptors
  - Skills: [] - standard Angular patterns

  **Song song**: Chạy song song: CÓ | Giai đoạn 2 | Chặn: 7, 8, 9, 10, 11 | Bị chặn bởi: 5

  **Tham chiếu**:
  - Pattern: Angular 21 standalone interceptors qua `withInterceptors()`
  - Auth: `app/presentation/api/v1/auth.py` - backend auth endpoints
  - User: `app/presentation/schemas/user_schema.py` - user response shape cho guard logic

  **Tiêu chí chấp nhận**:
  - [ ] Auth interceptor thêm Bearer token vào tất cả API requests
  - [ ] Response 401 clear token và chuyển hướng đến `/login`
  - [ ] Permission guard chặn routes khi user thiếu permission
  - [ ] ApiService generic methods compile và type-safe
  - [ ] Loading state toggle trong khi HTTP requests

  **Kịch bản QA**:
  ```
  Scenario: Auth interceptor thêm token
    Tool: Bash
    Steps: ng test --include='**/auth.interceptor.spec.ts'
    Expected: Tests pass
    Evidence: .omo/evidence/task-6-interceptor-tests.log

  Scenario: Guard chuyển hướng unauthenticated
    Tool: Bash
    Steps: ng test --include='**/auth.guard.spec.ts'
    Expected: Tests pass
    Evidence: .omo/evidence/task-6-guard-tests.log
  ```

  **Commit**: CÓ | Message: `feat(admin): add core HTTP service, interceptors, and guards` | Files: `frontend/admin/src/app/core/*`

- [ ] 7. Xây dựng Auth service và trang Login

  **Việc cần làm**:
  1. Tạo `src/app/core/services/auth.service.ts`:
     - `login(credentials)` → POST /api/v1/auth/login, lưu token trong localStorage
     - `logout()` → clear token, chuyển hướng đến login
     - `getCurrentUser()` → GET /api/v1/auth/me, cache trong BehaviorSubject
     - `isAuthenticated$` → Observable<boolean>
     - `currentUser$` → Observable<User | null>
  2. Tạo `src/app/features/auth/login/login.component.ts` (standalone):
     - Reactive form với email + password validation
     - Dùng nz-form, nz-input, nz-button từ ng-zorro
     - Thành công: lưu token, load user, navigate đến `/admin/dashboard`
     - Lỗi: hiển thị nz-message error
     - TailwindCSS cho custom layout (card centered, gradient background)
  3. Tạo `src/app/features/auth/auth.routes.ts` - lazy-loaded routes cho auth
  4. Style login page với TailwindCSS (không inline styles)
  **KHÔNG được làm**: KHÔNG lưu password. KHÔNG dùng template-driven forms. KHÔNG dùng `<nz-modal>` cho login errors (dùng nz-message).

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: auth UI và service
  - Skills: [] - standard Angular auth patterns

  **Song song**: Chạy song song: CÓ | Giai đoạn 2 | Chặn: 9, 11 | Bị chặn bởi: 5, 6

  **Tham chiếu**:
  - Backend: `app/presentation/api/v1/auth.py` - login và me endpoints
  - Schema: `app/presentation/schemas/auth_schema.py` - LoginRequest/LoginResponse
  - Schema: `app/presentation/schemas/user_schema.py` - UserResponse
  - User entity: `app/domain/entities/user.py` - user fields

  **Tiêu chí chấp nhận**:
  - [ ] Login form validate email format và required fields
  - [ ] Login thành công lưu token và chuyển hướng đến dashboard
  - [ ] Login thất bại hiển thị thông báo lỗi
  - [ ] Auth service expose currentUser$ với permissions array
  - [ ] Logout clear state và chuyển hướng

  **Kịch bản QA**:
  ```
  Scenario: Login với admin credentials
    Tool: Bash
    Steps: curl -s -X POST http://localhost:8000/api/v1/auth/login -d '{"email":"admin@company.vn","password":"Admin@123"}' | jq '.access_token'
    Expected: Trả về JWT token hợp lệ
    Evidence: .omo/evidence/task-7-login-api.json

  Scenario: Trang Login render
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation/frontend/admin && ng serve &; sleep 10; curl -s http://localhost:4200/login | grep -i "login\|email\|password"
    Expected: HTML chứa login form elements
    Evidence: .omo/evidence/task-7-login-page.html
  ```

  **Commit**: CÓ | Message: `feat(admin): add auth service and login page` | Files: `frontend/admin/src/app/core/services/auth.service.ts`, `frontend/admin/src/app/features/auth/*`

- [ ] 8. Tạo shared models/interfaces và constants

  **Việc cần làm**:
  1. Tạo `src/app/shared/models/user.model.ts` - interface khớp `UserResponse`
  2. Tạo `src/app/shared/models/role.model.ts` - interface khớp `Role` entity
  3. Tạo `src/app/shared/models/permission.model.ts` - interface khớp `Permission` entity
  4. Tạo `src/app/shared/models/department.model.ts` - interface khớp `Department` entity
  5. Tạo `src/app/shared/models/menu.model.ts` - interface khớp `MenuResponse`
  6. Tạo `src/app/shared/models/translation.model.ts` - interface khớp `TranslationResponse`
  7. Tạo `src/app/shared/models/pagination.model.ts` - generic pagination interface
  8. Tạo `src/app/shared/models/api-response.model.ts` - standard API response wrapper
  9. Tạo `src/app/shared/constants/permissions.ts` - enum tất cả permission codes từ backend
  10. Tạo `src/app/shared/constants/routes.ts` - route path constants
  **KHÔNG được làm**: KHÔNG dùng classes với constructors cho models (dùng interfaces). KHÔNG duplicate backend logic trong frontend models.

  **Agent Profile đề xuất**:
  - Category: `quick` - Lý do: chỉ định nghĩa TypeScript types
  - Skills: [] - type definitions

  **Song song**: Chạy song song: CÓ | Giai đoạn 2 | Chặn: 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 | Bị chặn bởi: -

  **Tham chiếu**:
  - User: `app/presentation/schemas/user_schema.py` - UserResponse
  - Role: `app/domain/entities/role.py` - Role entity
  - Permission: `app/domain/entities/permission.py` - Permission entity
  - Department: `app/infrastructure/database/models/department_model.py` - DepartmentModel
  - Menu: `app/presentation/schemas/menu_schema.py` (từ task 2)
  - Translation: `app/presentation/schemas/translation_schema.py` (từ task 3)
  - Permissions: `app/infrastructure/database/seed.py:38-46` - permission codes

  **Tiêu chí chấp nhận**:
  - [ ] Tất cả interfaces compile không lỗi
  - [ ] Interfaces khớp chính xác backend response shapes
  - [ ] `permissions.ts` chứa tất cả 7 permission codes hiện có
  - [ ] Không có `any` types trong model files

  **Kịch bản QA**:
  ```
  Scenario: Models compile
    Tool: Bash
    Steps: cd /home/pdat/Documents/master-operation/frontend/admin && npx tsc --noEmit src/app/shared/models/*.ts
    Expected: Không có TypeScript errors
    Evidence: .omo/evidence/task-8-models-compile.log
  ```

  **Commit**: CÓ | Message: `feat(admin): add shared models and constants` | Files: `frontend/admin/src/app/shared/models/*`, `frontend/admin/src/app/shared/constants/*`

### Giai đoạn 3: Admin Shell

- [ ] 9. Xây dựng Admin Pro Layout shell (sidebar, header, content, footer)

  **Việc cần làm**:
  1. Tạo `src/app/layout/admin-layout/admin-layout.component.ts` (standalone):
     - Dùng `nz-layout`, `nz-sider`, `nz-header`, `nz-content`, `nz-footer` từ ng-zorro
     - Sidebar: có thể thu gọn (80px thu gọn, 256px mở rộng), dark theme, fixed position
     - Header: fixed, chứa logo, breadcrumbs, language switcher, user dropdown (profile, logout)
     - Content: vùng cuộn với padding, render `<router-outlet>`
     - Footer: copyright text tối thiểu
     - Responsive: sidebar ẩn trên mobile (`nzBreakpoint="lg"`)
  2. Tạo `src/app/layout/components/sidebar/sidebar.component.ts` - wrap nz-sider + nz-menu
  3. Tạo `src/app/layout/components/header/header.component.ts` - wrap nz-header content
  4. Tạo `src/app/layout/components/footer/footer.component.ts`
  5. Tạo `src/app/layout/layout.routes.ts` - lazy-loaded admin routes với auth guard
  6. Style với TailwindCSS cho spacing, flexbox, và custom colors. Dùng ng-zorro variables cho Ant Design theme colors.
  **KHÔNG được làm**: KHÔNG dùng fixed pixel widths cho responsive breakpoints (dùng Tailwind classes). KHÔNG inline styles.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: component layout phức tạp
  - Skills: [] - Angular + ng-zorro layout

  **Song song**: Chạy song song: CÓ | Giai đoạn 3 | Chặn: 12-18 | Bị chặn bởi: 5, 6, 7, 8

  **Tham chiếu**:
  - External: `https://ng.ant.design/components/layout/en` - nz-layout docs
  - External: `https://ng.ant.design/components/menu/en` - nz-menu docs
  - Pattern: Ant Design Pro layout (Header + Sider + Content pattern)

  **Tiêu chí chấp nhận**:
  - [ ] Layout render với sidebar, header, content, footer
  - [ ] Sidebar thu gọn/mở rộng với animation
  - [ ] Mobile responsive: sidebar ẩn tại lg breakpoint
  - [ ] Header hiển thị user name từ auth service
  - [ ] Router outlet hoạt động trong content area
  - [ ] Không có console errors

  **Kịch bản QA**:
  ```
  Scenario: Layout render sau login
    Tool: Bash
    Steps: ng serve; curl -s http://localhost:4200/admin/dashboard | grep -E "sidebar|header|content"
    Expected: Layout elements có trong DOM
    Evidence: .omo/evidence/task-9-layout.html

  Scenario: Sidebar thu gọn
    Tool: Bash
    Steps: npx playwright-core screenshot --viewport-size=1280,720 http://localhost:4200/admin/dashboard collapsed.png
    Expected: Screenshot hiển thị sidebar thu gọn
    Evidence: .omo/evidence/task-9-collapsed.png
  ```

  **Commit**: CÓ | Message: `feat(admin): add admin pro layout shell` | Files: `frontend/admin/src/app/layout/*`

- [ ] 10. Xây dựng Menu service và sidebar menu động

  **Việc cần làm**:
  1. Tạo `src/app/core/services/menu.service.ts`:
     - `getMenuTree()` → GET /api/v1/menus, trả về Observable<MenuItem[]>
     - `createMenu(data)`, `updateMenu(id, data)`, `deleteMenu(id)` → CRUD
     - `syncMenu(data)` → POST /api/v1/menus/sync (nếu backend hỗ trợ bulk sync, nếu không thì gọi từng cái)
     - Menu state qua BehaviorSubject<MenuItem[]>
  2. Cập nhật sidebar component dùng `menu.service`:
     - Load menu tree từ API khi init
     - Render với `nz-menu` (nz-submenu cho nested items)
     - Lọc menu items theo permissions của user (so sánh `permission_code` với mảng `permissions` của user)
     - Highlight active item dựa trên route hiện tại
     - Thu gọn/mở rộng submenus
  3. Tạo `src/app/shared/pipes/has-permission.pipe.ts` - pipe kiểm tra user có permission không
  **KHÔNG được làm**: KHÔNG hardcode menu items. KHÔNG render menu items user không có permission.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: service + UI integration
  - Skills: [] - Angular + ng-zorro menu

  **Song song**: Chạy song song: CÓ | Giai đoạn 3 | Chặn: 12 | Bị chặn bởi: 2, 4, 5, 6, 8

  **Tham chiếu**:
  - Backend: `app/presentation/api/v1/menus.py` (từ task 2)
  - Menu model: `src/app/shared/models/menu.model.ts` (từ task 8)
  - Auth service: `src/app/core/services/auth.service.ts` (từ task 7)
  - ng-zorro: `https://ng.ant.design/components/menu/en`

  **Tiêu chí chấp nhận**:
  - [ ] Menu load từ `/api/v1/menus` khi page load
  - [ ] Nested submenus render đúng (System Management → Users, Roles, etc.)
  - [ ] Menu items không có `permission_code` hiển thị với tất cả
  - [ ] Menu items có `permission_code` bị ẩn nếu user thiếu permission
  - [ ] Active menu item khớp route hiện tại
  - [ ] Sidebar thu gọn chỉ hiển thị icons (không text)

  **Kịch bản QA**:
  ```
  Scenario: Menu load từ API
    Tool: Bash
    Steps: curl -s http://localhost:4200/admin/dashboard | grep -i "users\|roles\|dashboard"
    Expected: Menu items hiển thị trong rendered HTML
    Evidence: .omo/evidence/task-10-menu-loaded.html

  Scenario: Lọc permission hoạt động
    Tool: Bash
    Steps: Log in as employee (không có manage_org permission), kiểm tra System Management menu có bị ẩn không
    Expected: System Management section không hiển thị
    Evidence: .omo/evidence/task-10-perm-filter.html
  ```

  **Commit**: CÓ | Message: `feat(admin): add menu service and dynamic sidebar` | Files: `frontend/admin/src/app/core/services/menu.service.ts`, `frontend/admin/src/app/layout/components/sidebar/*`, `frontend/admin/src/app/shared/pipes/has-permission.pipe.ts`

- [ ] 11. Xây dựng i18n service, custom loader, và language switcher

  **Việc cần làm**:
  1. Tạo `src/app/core/services/translation-loader.service.ts` - implements TranslateLoader:
     - `getTranslation(lang)` → GET /api/v1/translations?language={lang}
     - Trả về Observable với key-value object cho ngx-translate
  2. Cấu hình `ngx-translate` trong `app.config.ts`:
     - Default language: 'vi'
     - Supported: ['vi', 'en']
     - Dùng custom TranslationLoader thay vì default HTTP loader
  3. Tạo `src/app/core/services/i18n.service.ts`:
     - `loadTranslations(lang)` → fetch từ API và set trong ngx-translate
     - `currentLang$` → BehaviorSubject
     - `getCurrentLang()`, `setLanguage(lang)`
     - `translate(key)` → wrapper xung quanh ngx-translate instant
  4. Thêm language switcher vào header component (nz-select hoặc nz-dropdown với VI/EN flags)
  5. Tạo `src/app/features/i18n/i18n-management.component.ts` (basic page để test i18n)
  **KHÔNG được làm**: KHÔNG dùng static JSON files cho translations (phải load từ API). KHÔNG dùng Angular built-in i18n (`$localize`) - dùng ngx-translate cho runtime switching.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: i18n service + UI integration
  - Skills: [] - ngx-translate + Angular

  **Song song**: Chạy song song: CÓ | Giai đoạn 3 | Chặn: 13 | Bị chặn bởi: 3, 4, 5, 6, 8

  **Tham chiếu**:
  - Backend: `app/presentation/api/v1/translations.py` (từ task 3)
  - Translation model: `src/app/shared/models/translation.model.ts` (từ task 8)
  - ngx-translate: `https://github.com/ngx-translate/core`

  **Tiêu chí chấp nhận**:
  - [ ] Translations load từ `/api/v1/translations?language=vi` khi app init
  - [ ] Language switcher đổi language và reload translations
  - [ ] Tất cả UI strings hardcoded dùng `translate` pipe hoặc service
  - [ ] Fallback sang key name nếu translation missing
  - [ ] Default language là Vietnamese ('vi')

  **Kịch bản QA**:
  ```
  Scenario: VI translations load
    Tool: Bash
    Steps: curl -s http://localhost:8000/api/v1/translations?language=vi | head -5
    Expected: Trả về VI key-value pairs
    Evidence: .omo/evidence/task-11-vi-translations.json

  Scenario: Language switch trên UI
    Tool: Bash
    Steps: ng serve; curl -s http://localhost:4200/admin/dashboard | grep -i "nguoi dung\|dashboard"
    Expected: Vietnamese text có trong rendered HTML
    Evidence: .omo/evidence/task-11-lang-switch.html
  ```

  **Commit**: CÓ | Message: `feat(admin): add i18n service and language switcher` | Files: `frontend/admin/src/app/core/services/translation-loader.service.ts`, `frontend/admin/src/app/core/services/i18n.service.ts`, `frontend/admin/src/app/features/i18n/i18n-management.component.ts`, `frontend/admin/src/app/layout/components/header/*`

### Giai đoạn 4: Trang Quản lý

- [ ] 12. Xây dựng trang Menu Management (tree table, CRUD modals, sync to DB)

  **Việc cần làm**:
  1. Tạo `src/app/features/menu/menu-management.component.ts` (standalone):
     - Dùng `nz-table` với tree data (hoặc nested expansion rows) hiển thị menu tree
     - Columns: key, title (vi/en), path, permission_code, sort_order, is_active, actions
     - Actions mỗi row: Edit, Delete
     - Top action: Add menu item (mở modal), Sync to DB (gửi tree hiện tại đến API)
  2. Tạo `src/app/features/menu/components/menu-form-modal.component.ts`:
     - Dùng `NzModalService.create()` mở modal với form component
     - Form fields: key, title_vi, title_en, path, icon (nz-select với ant design icon names), permission_code (nz-select với permission codes), parent_id (nz-tree-select hoặc nz-select), sort_order, is_active
     - Reactive form với validators
     - Khi submit: gọi menuService.create() hoặc update()
  3. Tạo `src/app/features/menu/menu.routes.ts` - lazy-loaded route
  4. Tất cả modals qua `NzModalService.create()` - KHÔNG BAO GIỜ dùng `<nz-modal>` trong template
  **KHÔNG được làm**: KHÔNG dùng `<nz-modal>` trong template. KHÔNG cho phép circular parent references. KHÔNG xóa menu items có children không có xác nhận.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: trang CRUD phức tạp với tree data
  - Skills: [] - Angular + ng-zorro table + modals

  **Song song**: Chạy song song: CÓ | Giai đoạn 4 | Chặn: - | Bị chặn bởi: 9, 10

  **Tham chiếu**:
  - Menu service: `src/app/core/services/menu.service.ts` (từ task 10)
  - Menu model: `src/app/shared/models/menu.model.ts` (từ task 8)
  - Permission constants: `src/app/shared/constants/permissions.ts` (từ task 8)
  - ng-zorro table: `https://ng.ant.design/components/table/en` (tree data example)
  - ng-zorro modal: `https://ng.ant.design/components/modal/en` (NzModalService section)

  **Tiêu chí chấp nhận**:
  - [ ] Menu tree hiển thị đúng với hierarchy parent-child
  - [ ] Add menu item modal tạo item mới trong DB
  - [ ] Edit menu item modal cập nhật fields trong DB
  - [ ] Delete xóa item (với xác nhận)
  - [ ] Sync button gửi full menu tree đến backend và refresh sidebar
  - [ ] Tất cả modals dùng `NzModalService.create()`
  - [ ] Form validate required fields trước khi submit

  **Kịch bản QA**:
  ```
  Scenario: Tạo menu item qua modal
    Tool: interactive_bash
    Steps: Mở Menu Management → Click Add → Điền form → Submit → Verify row xuất hiện
    Expected: Menu item mới hiển thị trong table và sidebar cập nhật
    Evidence: .omo/evidence/task-12-create-menu.png

  Scenario: Xóa menu với xác nhận
    Tool: interactive_bash
    Steps: Click Delete trên menu item → Xác nhận → Verify đã xóa
    Expected: Item đã xóa, sidebar cập nhật
    Evidence: .omo/evidence/task-12-delete-menu.png
  ```

  **Commit**: CÓ | Message: `feat(admin): add menu management page` | Files: `frontend/admin/src/app/features/menu/*`

- [ ] 13. Xây dựng trang i18n Management (key-value table, CRUD modals, sync to DB)

  **Việc cần làm**:
  1. Tạo `src/app/features/i18n/i18n-management.component.ts` (standalone):
     - Dùng `nz-table` với filter và sort
     - Columns: key, language (VI/EN badge), value, module, actions
     - Lọc theo language (nz-select)
     - Search theo key (nz-input-search)
     - Actions: Edit, Delete
     - Top actions: Add translation, Sync from JSON (upload vi.json/en.json và bulk sync), Export to JSON
  2. Tạo `src/app/features/i18n/components/translation-form-modal.component.ts`:
     - Modal form với fields: key, language (nz-select), value (nz-textarea), module (nz-select)
     - Reactive form với unique key+language validation
     - Khi submit: gọi translationService.create/update
  3. Tạo `src/app/core/services/translation.service.ts`:
     - CRUD methods cho translations API
     - `syncBulk(data)` → POST /api/v1/translations/sync
     - `exportToJson(language)` → tải file JSON
  4. Cập nhật `i18n-management.component.ts` từ task 11 thành trang management đầy đủ
  5. Tất cả modals qua `NzModalService.create()`
  **KHÔNG được làm**: KHÔNG cho phép duplicate key+language. KHÔNG dùng `<nz-modal>` trong template.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: table + modal CRUD
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 4 | Chặn: - | Bị chặn bởi: 9, 11

  **Tham chiếu**:
  - Translation API: `app/presentation/api/v1/translations.py` (từ task 3)
  - Translation model: `src/app/shared/models/translation.model.ts` (từ task 8)
  - ng-zorro table: `https://ng.ant.design/components/table/en`
  - ng-zorro modal: `https://ng.ant.design/components/modal/en`

  **Tiêu chí chấp nhận**:
  - [ ] Table hiển thị tất cả translations với language filter hoạt động
  - [ ] Add translation modal tạo entry mới
  - [ ] Edit modal cập nhật value
  - [ ] Delete xóa translation
  - [ ] Sync bulk upload JSON và refresh table
  - [ ] Language switcher trong header vẫn hoạt động sau khi chỉnh sửa translations
  - [ ] Tất cả modals dùng `NzModalService.create()`

  **Kịch bản QA**:
  ```
  Scenario: Thêm translation mới
    Tool: interactive_bash
    Steps: Mở i18n Management → Add → key="test.hello", lang="vi", value="Xin chao" → Submit
    Expected: Row xuất hiện, language switcher hiển thị translation mới nếu được dùng
    Evidence: .omo/evidence/task-13-add-translation.png

  Scenario: Bulk sync từ JSON
    Tool: Bash
    Steps: curl -s -X POST http://localhost:8000/api/v1/translations/sync -H "Authorization: Bearer $ADMIN_TOKEN" -d @app/infrastructure/database/seeds/vi.json
    Expected: Response success, table refresh
    Evidence: .omo/evidence/task-13-bulk-sync.json
  ```

  **Commit**: CÓ | Message: `feat(admin): add i18n management page` | Files: `frontend/admin/src/app/features/i18n/*`, `frontend/admin/src/app/core/services/translation.service.ts`

- [ ] 14. Xây dựng trang User CRUD (table, create/edit modals)

  **Việc cần làm**:
  1. Tạo `src/app/features/users/user-management.component.ts`:
     - `nz-table` với pagination (server-side, backend hiện trả về tất cả)
     - Columns: employee_code, email, full_name, role_name, department, is_active, actions
     - Filters: search theo name/email, lọc theo role, lọc theo department
     - Actions: View, Edit, Toggle active/inactive
     - Top action: Add User (mở modal)
  2. Tạo `src/app/features/users/components/user-form-modal.component.ts`:
     - Modal form: employee_code, email, full_name, password (create only), role_name (nz-select), department_id (nz-select từ departments API), is_active
     - Reactive form với email validation, required fields
     - Khi submit: gọi userService.create() hoặc update()
  3. Tạo `src/app/core/services/user.service.ts`:
     - `getUsers()`, `getUser(id)`, `createUser(data)`, `updateUser(id, data)`, `toggleActive(id)`
     - Map đến `/api/v1/users/*`
  4. Tạo `src/app/features/users/user.routes.ts` - lazy-loaded
  5. Tất cả modals qua `NzModalService.create()`
  **KHÔNG được làm**: KHÔNG cho phép chỉnh sửa employee_code sau khi tạo. KHÔNG hiển thị hashed_password trong UI.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: trang CRUD standard
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 4 | Chặn: - | Bị chặn bởi: 9, 8

  **Tham chiếu**:
  - Backend: `app/presentation/api/v1/users.py`
  - User schema: `app/presentation/schemas/user_schema.py`
  - User entity: `app/domain/entities/user.py`
  - Department API: `app/presentation/api/v1/departments.py`

  **Tiêu chí chấp nhận**:
  - [ ] Table liệt kê tất cả users từ `/api/v1/users`
  - [ ] Add user modal tạo user với hashed password trên backend
  - [ ] Edit modal cập nhật fields cho phép
  - [ ] Toggle active/inactive hoạt động
  - [ ] Filters search theo name/email đúng
  - [ ] Tất cả modals dùng `NzModalService.create()`

  **Kịch bản QA**:
  ```
  Scenario: Tạo user
    Tool: interactive_bash
    Steps: Mở Users → Add → Điền form → Submit
    Expected: User mới xuất hiện trong table, có thể login với credentials
    Evidence: .omo/evidence/task-14-create-user.png

  Scenario: Toggle user active status
    Tool: interactive_bash
    Steps: Click toggle trên user row → Xác nhận
    Expected: User status thay đổi, login bị chặn nếu inactive
    Evidence: .omo/evidence/task-14-toggle-user.png
  ```

  **Commit**: CÓ | Message: `feat(admin): add user management CRUD` | Files: `frontend/admin/src/app/features/users/*`, `frontend/admin/src/app/core/services/user.service.ts`

- [ ] 15. Xây dựng trang Role CRUD (table, create/edit modals, permission assignment)

  **Tiên quyết**: Backend GET /api/v1/roles và GET /api/v1/permissions endpoints CHƯA tồn tại. Xây dựng trước theo pattern trong `app/presentation/api/v1/departments.py` dùng `SQLAlchemyRoleRepository` và `SQLAlchemyPermissionRepository`. Thêm schemas và kết nối trong `app/main.py`.

  **Việc cần làm**:
  1. Tạo `src/app/features/roles/role-management.component.ts`:
     - `nz-table` liệt kê roles
     - Columns: name, display_name, permissions (tag list), actions
     - Actions: Edit (permissions), Delete
     - Top action: Add Role
  2. Tạo `src/app/features/roles/components/role-form-modal.component.ts`:
     - Modal form: name, display_name
     - Permission assignment: `nz-checkbox-group` hoặc custom multi-select với tất cả permissions
     - Hiển thị permissions dưới dạng tags với descriptions
     - Khi submit: gọi roleService.create/update
  3. Tạo `src/app/core/services/role.service.ts`:
     - CRUD cho roles + get permissions list
     - Map đến backend role/permission APIs
  4. Tạo `src/app/features/roles/role.routes.ts` - lazy-loaded
  5. Tất cả modals qua `NzModalService.create()`
  **KHÔNG được làm**: KHÔNG cho phép xóa role "admin" (hoặc cảnh báo mạnh). KHÔNG duplicate permission list logic (fetch từ backend).

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: CRUD với many-to-many relation
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 4 | Chặn: - | Bị chặn bởi: 9, 8

  **Tham chiếu**:
  - Role entity: `app/domain/entities/role.py`
  - Permission entity: `app/domain/entities/permission.py`
  - RolePermission entity: `app/domain/entities/role_permission.py`
  - Role repo: `app/infrastructure/database/repositories/sqlalchemy_role_repo.py`
  - ng-zorro checkbox: `https://ng.ant.design/components/checkbox/en`
  - ng-zorro tag: `https://ng.ant.design/components/tag/en`

  **Tiêu chí chấp nhận**:
  - [ ] Table liệt kê roles với permissions được gán
  - [ ] Add role modal tạo role với permissions được chọn
  - [ ] Edit modal cập nhật role name và permission set
  - [ ] Permission assignment dùng checkboxes cho tất cả permissions khả dụng
  - [ ] Xóa role admin bị chặn hoặc cảnh báo mạnh
  - [ ] Tất cả modals dùng `NzModalService.create()`

  **Kịch bản QA**:
  ```
  Scenario: Tạo role với permissions
    Tool: interactive_bash
    Steps: Mở Roles → Add → Name="test_role" → Chọn permissions → Submit
    Expected: Role xuất hiện với đúng permission tags
    Evidence: .omo/evidence/task-15-create-role.png

  Scenario: Chỉnh sửa role permissions
    Tool: interactive_bash
    Steps: Edit role → Bỏ chọn một số permissions → Submit
    Expected: Tags cập nhật, user với role này mất permissions bỏ chọn
    Evidence: .omo/evidence/task-15-edit-role.png
  ```

  **Commit**: CÓ | Message: `feat(admin): add role management CRUD` | Files: `frontend/admin/src/app/features/roles/*`, `frontend/admin/src/app/core/services/role.service.ts`

### Giai đoạn 5: Trang Còn lại

- [ ] 16. Xây dựng trang Permission view/management

  **Tiên quyết**: Backend GET /api/v1/permissions endpoint CHƯA tồn tại. Xây dựng trước theo pattern `departments.py` dùng `SQLAlchemyPermissionRepository`. Thêm schema và kết nối trong `app/main.py`.

  **Việc cần làm**:
  1. Tạo `src/app/features/permissions/permission-management.component.ts`:
     - `nz-table` liệt kê tất cả permissions (chủ yếu read-only)
     - Columns: code, description, roles đang dùng permission này (tag list)
     - Search/filter theo code hoặc description
     - Tùy chọn: Add custom permission (nếu backend hỗ trợ dynamic permissions)
     - Hiển thị roles nào có mỗi permission
  2. Tạo `src/app/core/services/permission.service.ts`:
     - `getPermissions()`, `getPermission(id)`
     - Map đến backend permission endpoints (có thể cần thêm GET endpoint nếu thiếu)
  3. Tạo `src/app/features/permissions/permission.routes.ts` - lazy-loaded
  **KHÔNG được làm**: KHÔNG cho phép xóa system permissions (đã seed). KHÔNG implement permission editing không có backend support.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: read-only table với references
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 5 | Chặn: - | Bị chặn bởi: 9, 8

  **Tham chiếu**:
  - Permission entity: `app/domain/entities/permission.py`
  - Permission model: `app/infrastructure/database/models/permission_model.py`
  - RolePermission: `app/infrastructure/database/models/role_permission_model.py`

  **Tiêu chí chấp nhận**:
  - [ ] Table liệt kê tất cả permissions từ backend
  - [ ] Hiển thị roles nào có mỗi permission
  - [ ] Search lọc theo code/description
  - [ ] Read-only cho system permissions

  **Kịch bản QA**:
  ```
  Scenario: Xem permissions
    Tool: Bash
    Steps: curl -s http://localhost:4200/admin/permissions | grep -i "manage_org\|create_task"
    Expected: Permission codes hiển thị trong rendered HTML
    Evidence: .omo/evidence/task-16-permissions.html
  ```

  **Commit**: CÓ | Message: `feat(admin): add permission management page` | Files: `frontend/admin/src/app/features/permissions/*`, `frontend/admin/src/app/core/services/permission.service.ts`

- [ ] 17. Xây dựng trang Department CRUD (tree table)

  **Việc cần làm**:
  1. Tạo `src/app/features/departments/department-management.component.ts`:
     - `nz-table` với tree structure (parent departments)
     - Columns: name, level, parent department, employee count, actions
     - Actions: Edit, Delete
     - Top action: Add Department
     - Hiển thị department hierarchy trực quan
  2. Tạo `src/app/features/departments/components/department-form-modal.component.ts`:
     - Modal form: name, parent_id (nz-tree-select hiển thị dept hierarchy), level (auto-calculated từ parent)
     - Reactive form
  3. Tạo `src/app/core/services/department.service.ts`:
     - `getDepartments()`, `getDepartmentTree()`, `createDepartment(data)`, `updateDepartment(id, data)`, `deleteDepartment(id)`
     - Map đến `/api/v1/departments/*`
  4. Tạo `src/app/features/departments/department.routes.ts` - lazy-loaded
  5. Tất cả modals qua `NzModalService.create()`
  **KHÔNG được làm**: KHÔNG cho phép circular parent references. KHÔNG xóa departments có employees không reassigning.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: tree table CRUD
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 5 | Chặn: - | Bị chặn bởi: 9, 8

  **Tham chiếu**:
  - Department API: `app/presentation/api/v1/departments.py`
  - Department model: `app/infrastructure/database/models/department_model.py`
  - Department entity: `app/domain/entities/department.py`
  - Department tree service: `app/domain/services/department_tree.py`

  **Tiêu chí chấp nhận**:
  - [ ] Table hiển thị department tree với hierarchy parent-child
  - [ ] Add department modal tạo với parent đúng
  - [ ] Edit modal cập nhật department name/parent
  - [ ] Delete bị chặn nếu department có employees
  - [ ] Tất cả modals dùng `NzModalService.create()`

  **Kịch bản QA**:
  ```
  Scenario: Tạo department
    Tool: interactive_bash
    Steps: Mở Departments → Add → Name="QA Team", Parent="Engineering" → Submit
    Expected: Department xuất hiện trong tree
    Evidence: .omo/evidence/task-17-create-dept.png
  ```

  **Commit**: CÓ | Message: `feat(admin): add department management CRUD` | Files: `frontend/admin/src/app/features/departments/*`, `frontend/admin/src/app/core/services/department.service.ts`

- [ ] 18. Xây dựng trang Dashboard/Welcome

  **Việc cần làm**:
  1. Tạo `src/app/features/dashboard/dashboard.component.ts`:
     - Welcome message với user name từ auth service
     - Quick stats cards (total users, active users, total departments - dùng APIs hiện có)
     - Recent activity placeholder (có thể để trống bây giờ)
     - Dùng nz-card, nz-statistic, nz-grid cho layout
     - Style với TailwindCSS
  2. Tạo `src/app/features/dashboard/dashboard.routes.ts` - lazy-loaded
  3. Đặt làm default route sau login (`/admin` chuyển hướng đến `/admin/dashboard`)
  4. Thêm route trong `layout.routes.ts`
  **KHÔNG được làm**: KHÔNG implement charts phức tạp trong giai đoạn này. KHÔNG thêm real-time data.

  **Agent Profile đề xuất**:
  - Category: `visual-engineering` - Lý do: trang dashboard đơn giản
  - Skills: [] - Angular + ng-zorro

  **Song song**: Chạy song song: CÓ | Giai đoạn 5 | Chặn: - | Bị chặn bởi: 9, 7

  **Tham chiếu**:
  - ng-zorro card: `https://ng.ant.design/components/card/en`
  - ng-zorro statistic: `https://ng.ant.design/components/statistic/en`
  - Auth service: `src/app/core/services/auth.service.ts` (từ task 7)

  **Tiêu chí chấp nhận**:
  - [ ] Dashboard hiển thị welcome message với full name của user
  - [ ] Stats cards hiển thị data từ APIs
  - [ ] Responsive grid layout
  - [ ] Không có console errors

  **Kịch bản QA**:
  ```
  Scenario: Dashboard render
    Tool: Bash
    Steps: curl -s http://localhost:4200/admin/dashboard | grep -i "welcome\|dashboard\|users"
    Expected: Dashboard elements hiển thị
    Evidence: .omo/evidence/task-18-dashboard.html
  ```

  **Commit**: CÓ | Message: `feat(admin): add dashboard page` | Files: `frontend/admin/src/app/features/dashboard/*`

## Giai đoạn Kiểm thử Cuối cùng (BẮT BUỘC — sau TẤT CẢ tasks implementation)
> 4 review agents chạy SONG SONG. TẤT CẢ phải PHÊ DUYỆT. Trình bày kết quả consolidated cho user và nhận "okay" rõ ràng trước khi hoàn thành.
> **KHÔNG tự động tiếp tục sau kiểm thử. Chờ phản hồi rõ ràng của user trước khi đánh dấu hoàn thành.**
> **Không bao giờ đánh dấu F1-F4 là checked trước khi nhận okay của user.** Từ chối hoặc feedback của user → fix → re-run → trình bày lại → chờ okay.
- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check — deep

### F1. Plan Compliance Audit

**Việc cần làm**: Xác minh mỗi task trong plan được implement đúng như đã chỉ định:
- Angular 21 standalone components dùng xuyên suốt?
- TailwindCSS + ng-zorro đều có mặt?
- TẤT CẢ modals dùng NzModalService.create() (grep `<nz-modal` trong templates - phải ZERO matches)?
- TẤT CẢ forms là reactive (không có `ngModel` trong forms)?
- Menu load từ API với permission filtering?
- i18n load từ API qua ngx-translate?
- Backend APIs cho menu và translations tồn tại và trả về đúng shapes?
- Seed files populate đúng?

**Tiêu chí chấp nhận**:
- [ ] `grep -r "<nz-modal" frontend/admin/src/` trả về zero matches
- [ ] `grep -r "ngModel" frontend/admin/src/app/features/` trả về zero matches trong form contexts
- [ ] `grep -r "standalone: false" frontend/admin/src/` trả về zero matches
- [ ] Tất cả backend API endpoints từ tasks 1-4 respond đúng

### F2. Code Quality Review

**Việc cần làm**: Review code cho Angular best practices:
- Không memory leak (unsubscribe từ subscriptions)
- Xử lý lỗi đúng trong tất cả services
- Naming conventions nhất quán
- Không có `any` types trong business logic
- Sử dụng OnPush change detection đúng chỗ
- Chỉ Tailwind classes, không inline styles
- Tổ chức file đúng

**Tiêu chí chấp nhận**:
- [ ] Không có `any` types trong service files
- [ ] Tất cả BehaviorSubjects có `.complete()` hoặc được quản lý qua `takeUntilDestroy()`
- [ ] Không inline styles trong component templates
- [ ] File naming nhất quán (kebab-case)

### F3. Real Manual QA

**Việc cần làm**: End-to-end smoke tests:
1. Login với admin → xem dashboard
2. Navigate đến mỗi trang qua sidebar
3. Tạo user → verify trong list
4. Chỉnh sửa permissions của role → verify thay đổi
5. Thêm menu item → verify trong sidebar
6. Thêm translation → verify trong UI
7. Switch language VI/EN → verify text thay đổi
8. Logout → chuyển hướng đến login
9. Thử truy cập /admin không có token → bị guard chặn

**Tiêu chí chấp nhận**:
- [ ] Tất cả 9 smoke tests pass
- [ ] Không có console errors trong khi test
- [ ] Screenshots captured cho mỗi trang chính

### F4. Scope Fidelity Check

**Việc cần làm**: Xác minh ranh giới phạm vi:
- IN scope items có mặt: auth, layout, menu mgmt, i18n mgmt, user/role/permission/dept CRUD
- OUT of scope items KHÔNG có mặt: task/leave/attendance mgmt, NgRx, SSR

**Tiêu chí chấp nhận**:
- [ ] Tất cả in-scope features đã implement
- [ ] Không có out-of-scope features được thêm
- [ ] Không có extra dependencies ngoài plan

## Chiến lược Commit

- Wave 1 commits: Backend features (`feat(api): ...`, `feat(db): ...`)
- Wave 2 commits: Project setup (`chore(admin): ...`, `feat(admin): ...`)
- Wave 3-5 commits: Frontend features (`feat(admin): ...`)
- Final verification: Fix commits (`fix(admin): ...`) nếu có issues
- Final commit: `feat(admin): complete admin panel v1`

## Tiêu chí Thành công

1. **Chức năng**: Admin frontend chạy trên port 4200, kết nối backend trên 8000
2. **Auth**: Login/logout hoạt động với JWT, guards bảo vệ routes
3. **Menu**: Menu động từ API, được lọc theo permissions, có thể chỉnh sửa qua trang management
4. **i18n**: VI/EN language switcher, translations load từ API, có thể chỉnh sửa qua trang management
5. **CRUD**: Trang Users, Roles, Permissions, Departments có create/read/update/delete hoạt động
6. **UI/UX**: Ant Design Pro layout, responsive, styling nhất quán, loading states trên tất cả async ops
7. **Chất lượng Code**: Standalone components, reactive forms, NzModalService cho tất cả modals, không có `any` types
8. **Backend**: Menu và Translation APIs hoạt động đầy đủ với seed data
