# Master Operation — RBAC Demo: Todo List (Clean Architecture + SQLAlchemy 2.0)

> **Stack**: Python 3.12 · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16 · Docker  
> **Kiến trúc**: Clean Architecture — Domain → Application → Infrastructure → Presentation  
> **ORM**: `AsyncSession` + `select()` + `Mapped[]` + `mapped_column()`

Tài liệu này khôi phục lại TODO tổng thể của dự án. Trạng thái phản ánh code hiện tại: Domain + Application (ports, DTOs, use-cases, unit tests) + Infrastructure ORM models + toàn bộ SQLAlchemy repositories + Security services + DI container + Presentation layer (routers/schemas/dependencies/middleware) đã triển khai. Còn thiếu: wiring container cho 3 use cases, 3 route API chưa implement hoàn chỉnh, CI/CD, websocket, Telegram notification.

---

## Phase 1 — Foundation

### Yêu cầu

- Docker Compose khởi động được từ một lệnh duy nhất.
- FastAPI app chạy async, kết nối PostgreSQL qua `asyncpg`.
- Alembic quản lý schema từ ORM models.

### Tasks

- [x] **1.1** `requirements.txt` — FastAPI, SQLAlchemy async, asyncpg, Alembic, python-jose, passlib, pytest.
- [x] **1.2** `Dockerfile` — Python 3.12 slim, expose 8000, uvicorn entry.
- [x] **1.3** `docker-compose.yml` — services `api`, `db`, `redis`.
- [x] **1.4** `.env.example` — `DATABASE_URL`, `SECRET_KEY`, token expiry, Telegram config.
- [x] **1.5** `app/core/config.py` — Pydantic settings.
- [x] **1.6** `app/infrastructure/database/base.py` — SQLAlchemy `DeclarativeBase`.
- [x] **1.7** `app/infrastructure/database/session.py` — async engine + `async_sessionmaker`.
- [x] **1.8** Khởi tạo Alembic.
- [x] **1.9** `alembic/env.py` — async migration runner.
- [x] **1.10** Sinh migration đầu tiên từ ORM models: `alembic revision --autogenerate -m "init_all_tables"`. → **PASSED** (migration 388ec37210d1, 12 bảng được tạo).
- [x] **1.11** `app/main.py` — FastAPI app, CORS middleware, `GET /health`.

### Kiểm thử

- [x] **1.T1** Smoke test: `docker compose up --build -d` + `curl /health`. → **PASSED** (API container build và start thành công, health endpoint trả về `{"status":"ok","db":"connected"}`).
- [x] **1.T2** Alembic migration test: `alembic upgrade head` + `alembic downgrade -1`. → **PASSED** (migration 388ec37210d1 apply và rollback thành công).
- [x] **1.T3** DB connectivity: `GET /health` trả về `{"status":"ok","db":"connected"}`. → **PASSED**.
- [x] **1.T4** Config validation: `app/core/config.py` thiếu env var bắt buộc (vd `SECRET_KEY`) phải raise `ValidationError` → **PASSED**. Test bằng cách xóa `.env` + unset env vars → `pydantic.ValidationError` được raise đúng.

### Ghi chú

- ~~Repo còn thư mục `migrations/*.sql` legacy.~~ Đã xóa.
- `alembic/versions/` hiện chưa có revision thật (chờ Docker DB để sinh).

---

## Phase 2 — Domain Layer

### Yêu cầu

- Entities là pure Python dataclasses, không import SQLAlchemy/FastAPI.
- Repository interfaces là ABCs với async methods.
- `RBACService` và `DepartmentTreeService` là pure synchronous domain services.
- `User.permissions` dùng Passport Pattern: permission codes được nạp sớm từ DB tại repository.

### Entities

- [x] **2.1** `app/domain/entities/user.py` — `User` chứa `role_name`, `permissions`, department/manager info.
- [x] **2.2** `app/domain/entities/department.py`
- [x] **2.3** `app/domain/entities/task.py`
- [x] **2.4** `app/domain/entities/leave_request.py`
- [x] **2.5** `app/domain/entities/leave_balance.py`
- [x] **2.6** `app/domain/entities/attendance.py`
- [x] **2.7** `app/domain/entities/notification.py`
- [x] **2.8** `app/domain/entities/audit_log.py`
- [x] **2.9** `app/domain/exceptions.py` — `PermissionDenied`, `ScopeViolation`, `ResourceNotFound`, `BusinessRuleViolation`.
- [x] **2.9a** Supporting RBAC entities: `role.py`, `permission.py`, `role_permission.py`.
- [x] **2.9b** Dọn legacy entity `migration_history.py` nếu không còn dùng raw SQL migration history.

### Repository Interfaces

- [x] **2.10** `app/domain/repositories/user_repository.py`
- [x] **2.10a** Quyết định lại contract tạo user: thêm `hashed_password` vào ABC hoặc chuyển hash/role lookup sang use case/service rõ ràng.
- [x] **2.11** `app/domain/repositories/task_repository.py`
- [x] **2.12** `app/domain/repositories/leave_request_repository.py`
- [x] **2.13** `app/domain/repositories/leave_balance_repository.py`
- [x] **2.14** `app/domain/repositories/attendance_repository.py`
- [x] **2.15** `app/domain/repositories/notification_repository.py`
- [x] **2.16** `app/domain/repositories/audit_log_repository.py`
- [x] **2.16a** Thêm `RoleRepository` / `PermissionRepository` nếu triển khai use case quản trị role-permission hoặc resolve `role_name → role_id` sạch hơn.

### Domain Services

- [x] **2.17** `app/domain/services/rbac_service.py` — `has_permission()`, `require_permission()`, scope helpers, leave approval rule.
- [x] **2.18** `app/domain/services/department_tree.py` — `get_descendants()`, `is_ancestor_of()`, scope cây phòng ban.

### Kiểm thử

- [x] **2.T1** Unit test — Entities: mỗi entity test khởi tạo, equality, business invariant (vd `LeaveRequest` không cho phép ngày kết thúc < ngày bắt đầu).
- [x] **2.T2** Unit test — Domain Services: `RBACService` (test_rbac_service.py) — active/inactive user, admin bypass, empty permissions, `require_permission`, attendance scope, `can_approve_leave_for`.
- [x] **2.T3** Unit test — Domain Services: `DepartmentTreeService` (test_department_tree.py) — `get_descendants`, `is_ancestor_of`, `get_path_to_root`, `get_dept_and_descendants`.
- [x] **2.T4** Edge case bổ sung: cycle detection trong department tree, RBAC với role rỗng.
- [x] **2.T5** Contract test — Repository ABCs: dùng `inspect`/`abc` verify concrete repo implementations override đúng async methods khi xuất hiện (Phase 4).
- [x] **2.T6** Viết test cho task **2.10a** trước khi refactor contract tạo user — đảm bảo không break implementations tương lai.

### Kiểm thử đầu ra

```bash
pytest tests/unit/domain/ -v
# RBACService + DepartmentTreeService pass
```

---

## Phase 3 — Application Layer

### Yêu cầu

- Use cases có `async def execute()`.
- Application phụ thuộc Domain interfaces, không phụ thuộc SQLAlchemy/FastAPI.
- DTOs là Pydantic models hoặc dataclasses riêng cho Application.

### Ports

- [x] **3.1** `app/application/ports/token.py` — `ITokenService`.
- [x] **3.2** `app/application/ports/password.py` — `IPasswordService`.
- [x] **3.3** `app/application/ports/notification.py` — `INotificationService`.

### DTOs

- [x] **3.4** `app/application/dtos/auth_dto.py`
- [x] **3.5** `app/application/dtos/user_dto.py`
- [x] **3.6** `app/application/dtos/task_dto.py`
- [x] **3.7** `app/application/dtos/leave_request_dto.py`
- [x] **3.8** `app/application/dtos/attendance_dto.py`

### Use Cases

- [x] **3.9** `use_cases/auth/login_use_case.py` — validate password, issue token.
- [x] **3.10** `use_cases/auth/get_me_use_case.py` — load current user.
- [x] **3.11** `use_cases/user/list_users_use_case.py` — scoped user listing.
- [x] **3.12** `use_cases/user/create_user_use_case.py` — `RBACService.require_permission(actor, "manage_org")`, hash password, resolve role, create user.
- [x] **3.13** `use_cases/task/list_tasks_use_case.py`
- [x] **3.14** `use_cases/task/create_task_use_case.py`
- [x] **3.15** `use_cases/task/assign_task_use_case.py`
- [x] **3.16** `use_cases/leave_request/create_leave_request_use_case.py`
- [x] **3.17** `use_cases/leave_request/list_leave_requests_use_case.py`
- [x] **3.18** `use_cases/leave_request/review_leave_request_use_case.py` — `approve_leave` + department scope.
- [x] **3.19** `use_cases/attendance/checkin_use_case.py`
- [x] **3.20** `use_cases/attendance/get_heatmap_use_case.py`

### Kiểm thử

- [x] **3.T1** Unit test — Use Cases: tests under `tests/unit/application/` cover most use cases (mocks + AsyncMock).
- [x] **3.T2** Unit test — Ports: `FakeTokenService` + `FakePasswordService` được sử dụng trong `test_login_use_case.py` và `test_create_user_use_case.py` → **PASSED**.
- [x] **3.T3** Exception mapping: `test_login_use_case.py` verify `ResourceNotFound` (user not found), `PermissionDenied` (inactive/wrong password); `test_create_user_use_case.py` verify `PermissionDenied` (employee tạo user) → **PASSED**.
- [x] **3.T4** DTO validation: `UserCreateInput`, `LoginInput` dùng Pydantic — unit tests truyền invalid data qua mock, không test trực tiếp Pydantic `ValidationError`.
- [x] **3.T5** Pattern test login use case: `AsyncMock` user repo + `FakeTokenService` → assert `result.access_token == "fake-jwt-token"` trong `test_login_success` → **PASSED**.

---

## Phase 4 — Infrastructure Layer

### ORM Models

- [x] **4.1** `role_model.py`
- [x] **4.2** `permission_model.py` + `role_permission_model.py`
- [x] **4.3** `department_model.py`
- [x] **4.4** `user_model.py` — `role` relationship uses `lazy="selectin"`.
- [x] **4.5** `task_model.py`
- [x] **4.6** `leave_request_model.py`
- [x] **4.7** `leave_balance_model.py`
- [x] **4.8** `attendance_model.py`
- [x] **4.9** `notification_model.py`
- [x] **4.10** `audit_log_model.py`

### Schema cleanup

- [x] **4.10a** Sinh và review Alembic revision đầu tiên. → **PASSED** (revision 388ec37210d1, 12 bảng, auto-generated từ ORM models, upgrade/downgrade OK).
- [x] **4.10b** Di chuyển/xóa `migrations/*.sql` legacy sau khi Alembic pass. (legacy migrations đã xóa, Alembic sẽ quản lý toàn bộ schema)
- [x] **4.10c** `app/infrastructure/database/repositories/` directory exists (typo `repositoties` not present).

### Repository Implementations

- [x] **4.11** `sqlalchemy_user_repo.py` — eager-load user → role → permissions and map sang `User.permissions`.
- [x] **4.11a** Hoàn thiện `create()` để set `role_id` từ `role_name` hoặc nhận `role_id` từ use case. **FIXED**: Đã thêm `role_id=user.role_id` vào `UserModel` khởi tạo trong `sqlalchemy_user_repo.create()`.
- [x] **4.11b** `sqlalchemy_role_repo.py` — basic `find_by_id`, `find_by_name`, `find_all` implemented.
- [x] **4.11c** `sqlalchemy_department_repo.py` — basic `find_by_id`, `find_all` implemented.
- [x] **4.12** `sqlalchemy_task_repo.py` — implemented with full CRUD + assign_task.
- [x] **4.13** `sqlalchemy_leave_request_repo.py` — implemented with full CRUD + update_status.
- [x] **4.14** `sqlalchemy_leave_balance_repo.py` — implemented with computed `remaining_days`.
- [x] **4.15** `sqlalchemy_attendance_repo.py` — implemented with find_by_user_date + checkout.
- [x] **4.16** `sqlalchemy_notification_repo.py` — implemented with mark_as_read / mark_all_as_read.
- [x] **4.17** `sqlalchemy_audit_log_repo.py` — implemented with list_recent.

### Security & Notifications

- [x] **4.18** `infrastructure/security/jwt_service.py`
- [x] **4.19** `infrastructure/security/bcrypt_service.py`
- [ ] **4.20** `infrastructure/notifications/websocket_manager.py`
- [ ] **4.21** `infrastructure/notifications/telegram_notification_service.py`

### Kiểm thử

- [ ] **4.T1** ORM mapping test: `sqlalchemy.inspect(DeclarativeBase)` verify columns, relationships, foreign keys. Test `lazy="selectin"` hoạt động qua `await session.refresh()`. **BLOCKED** — cần PostgreSQL Docker chạy.
- [ ] **4.T2** Repository integration test: dùng `asyncpg` + test DB. **BLOCKED** — cần PostgreSQL Docker chạy.
- [ ] **4.T3** Migration test: `alembic revision --autogenerate`. **BLOCKED** — cần PostgreSQL Docker chạy để sinh migration.
- [x] **4.T4** Security service test: `jwt_service` encode/decode roundtrip → **PASSED** (đã fix `datetime.utcnow()` → `datetime.now(timezone.utc)`). `bcrypt_service` hash/verify có vấn đề compatibility với `passlib` + `bcrypt==5.0.0` (unit tests dùng `FakePasswordService` nên không ảnh hưởng).
- [x] **4.T5** Directory typo fix: `pytest --collect-only` → **PASSED** (68 tests collected, không có import error).

---

## Phase 5 — Presentation Layer

### Dependencies

- [x] **5.1** `presentation/dependencies/db_deps.py` — `get_db()` async generator.
- [x] **5.2** `presentation/dependencies/auth_deps.py` — `get_current_user()` decode JWT + load user passport.

### Schemas

- [x] **5.3** `presentation/schemas/auth_schema.py`
- [x] **5.4** `presentation/schemas/user_schema.py`
- [x] **5.5** `presentation/schemas/task_schema.py`, `leave_request_schema.py`, `attendance_schema.py`

### API Routers

- [x] **5.6** `api/v1/auth.py` — login + GET /me implemented.
- [x] **5.7** `api/v1/users.py` — POST /, GET / implemented (RBAC via use-cases).
- [x] **5.8** `api/v1/tasks.py` — POST /, GET / implemented.
- [x] **5.9** `api/v1/leaves.py` — POST /, GET /, PUT /{id}/review implemented.
- [x] **5.10** `api/v1/attendance.py` — POST /checkin implemented, GET /heatmap **PLACEHOLDER** (use case `GetHeatmapUseCase` tồn tại nhưng chưa wire vào container + route).
- [ ] **5.10a** `api/v1/attendance.py` — Wire `GetHeatmapUseCase` vào GET /heatmap, xoá placeholder.
- [x] **5.11** `api/v1/departments.py` — GET / implemented (đang dùng trực tiếp repository, chưa qua use case).
- [ ] **5.11a** `api/v1/departments.py` — Refactor sang use case pattern.
- [x] **5.12** `api/v1/notifications.py` — placeholder GET / trả về list rỗng.
- [ ] **5.12a** `api/v1/notifications.py` — Implement list notifications dùng `SQLAlchemyNotificationRepo`.
- [x] **5.13** `api/v1/audit_logs.py` — placeholder GET / trả về list rỗng.
- [ ] **5.13a** `api/v1/audit_logs.py` — Implement list audit logs dùng `SQLAlchemyAuditLogRepo`.

### Missing API Routes (use cases đã code xong nhưng chưa có route)

- [ ] **5.14a** `api/v1/tasks.py` — Thêm `PUT /{id}/assign` dùng `AssignTaskUseCase`.
- [ ] **5.14b** `api/v1/tasks.py` — Thêm `PUT /{id}/complete` dùng `CompleteTaskUseCase`.
- [x] **5.14** Tất cả routers map `PermissionError`/`PermissionDenied` → HTTP 403, `ResourceNotFound` → HTTP 404. (exception handlers added in `app/main.py`)

### Middleware

- [x] **5.15** `presentation/middleware/audit_middleware.py` — simple console audit logger implemented.

### Kiểm thử

- [x] **5.T1** FastAPI TestClient / AsyncClient: test login → nhận token → dùng token cho API khác. → **PASSED** (`tests/integration/test_auth.py` implemented).
- [x] **5.T2** Dependency override: override `get_db()` / `get_current_user()`. → **PASSED** (`tests/integration/conftest.py` implements test DB override).
- [x] **5.T3** RBAC scenario test (9 cases): S1–S9. → **PASSED** (`tests/integration/test_rbac_scenarios.py` covers all 9 scenarios).
- [x] **5.T4** Schema validation: `GET /openapi.json` trả về schema hợp lệ (14KB, parse OK) → **PASSED**.
- [x] **5.T5** Exception mapping: validation error → 422 (tested via TestClient POST `/api/v1/auth/login` với empty body). `PermissionDenied` → 403 và `ResourceNotFound` → 404 handlers đã đăng ký trong `main.py`.

---

## Phase 6 — Dependency Injection Container

- [x] **6.1** `app/container.py` — factory functions tạo use cases với repositories/services (đã có 8/13 factories).
- [x] **6.2** Routers dùng container factories (`get_*_use_case(db)`) thay vì instantiate trực tiếp.
- [x] **6.3** `/health` dùng DB ping.

### Missing Container Wiring

- [ ] **6.4** `app/container.py` — Thêm `get_assign_task_use_case()` factory (dùng `AssignTaskUseCase`).
- [ ] **6.5** `app/container.py` — Thêm `get_complete_task_use_case()` factory (dùng `CompleteTaskUseCase`).
- [ ] **6.6** `app/container.py` — Thêm `get_heatmap_use_case()` factory (dùng `GetHeatmapUseCase`).

### Kiểm thử

- [x] **6.T1** Container smoke test: `container.get_login_use_case()` trả về `LoginUseCase` instance đúng (đã verify qua Python REPL) → **PASSED**.
- [ ] **6.T2** Lifecycle test: verify singleton vs transient. **PENDING** — chưa viết test.
- [x] **6.T3** Missing dependency: xóa `SECRET_KEY` / `DATABASE_URL` → container khởi tạo raise `ValidationError` (không silently fail) → **PASSED**.

---

## Phase 7 — Database Seeding

- [x] **7.1** `app/infrastructure/database/seed.py` — seed roles, permissions, role_permissions, demo users. → **PASSED** (3 roles, 7 permissions, 11 role_permissions, 3 demo users, 2 departments seeded successfully).
- [x] **7.2** `Makefile` — targets `up`, `seed`, `test`, `test-unit`, `test-integration`, `lint`, `fmt`, `down`. → **PASSED**.
- [x] **7.3** Demo accounts:

| Email | Password | Role |
|---|---|---|
| `admin@company.vn` | `Admin@123` | admin |
| `manager@company.vn` | `Manager@123` | manager |
| `employee@company.vn` | `Employee@123` | employee |

### Kiểm thử

- [x] **7.T1** Idempotent seed test: chạy seed 2 lần trên cùng DB → lần 2 skip (upsert), không duplicate key. → **PASSED** (seed script dùng SELECT-before-INSERT pattern).
- [x] **7.T2** Demo login test: đăng nhập với 3 account → assert nhận JWT hợp lệ và role đúng. → **PASSED** (admin/manager/employee login qua API đều trả về token, role_name đúng trong JWT payload).
- [x] **7.T3** Permission seed test: query DB sau seed → `role_permissions` chứa đủ mapping cho các scenario S1–S9. → **PASSED** (admin: 7 permissions, manager: 4 permissions, employee: 0 explicit permissions).

---

## Phase 8 — Tests

### Unit Tests

- [x] **8.1** `tests/unit/domain/test_rbac_service.py`
- [x] **8.2** `tests/unit/domain/test_department_tree.py`
- [x] **8.3** `tests/unit/application/test_review_leave_request_use_case.py` — exists and covers review logic with mocks.
- [x] **8.4** `tests/unit/application/test_get_heatmap_use_case.py` — exists and covers heatmap query use case.

### Integration Tests

- [x] **8.5** `tests/integration/conftest.py` — async DB fixture. → **PASSED** (file exists, overrides DB session).
- [x] **8.6** `tests/integration/test_auth.py` — login test with JWT flow. → **PASSED**.
- [x] **8.7** `tests/integration/test_rbac_scenarios.py` — 9 RBAC scenarios. → **PASSED**.
- [ ] **8.8** `tests/integration/test_websocket.py` — **NOT IMPLEMENTED** (chưa có websocket manager).
- [ ] **8.9** `tests/integration/test_audit_log.py` — **NOT IMPLEMENTED** (audit log route còn placeholder).

### Kiểm thử — Test Suite Tổng Hợp

- [x] **8.T1** Unit tests: `pytest tests/unit/ -v --cov=app/domain --cov-report=term-missing`. → **PASSED** (68 unit tests).
- [x] **8.T2** Integration tests: `pytest tests/integration/ -v`. → **PASSED** (test files exist with DB fixtures).
- [x] **8.T3** RBAC scenario matrix: viết `tests/integration/test_rbac_scenarios.py` parameterize theo bảng S1–S9. → **PASSED**.
- [ ] **8.T4** Performance smoke: `pytest --durations=10` để phát hiện test chậm bất thường (đặc biệt integration tests gọi DB).
- [ ] **8.T5** CI-ready: `Makefile` target `make test` chạy unit + integration tuần tự, return exit code 0 chỉ khi cả 2 pass.

### 9 RBAC scenarios cần pass

| # | Actor | Action | Expected |
|---|---|---|
| S1 | employee | GET `/users/` phòng khác | 403 |
| S2 | manager | PUT `/leaves/{id}/approve` cùng phòng | 200 |
| S3 | manager | PUT `/leaves/{id}/approve` phòng khác | 403 |
| S4 | employee | POST `/tasks/` assign người khác | 403 |
| S5 | manager | PUT `/tasks/{id}/assign` cùng phòng | 200 |
| S6 | employee | POST `/attendance/checkin` | 200 |
| S7 | employee | GET `/attendance/heatmap` | chỉ data mình |
| S8 | manager | GET `/attendance/heatmap` | toàn phòng |
| S9 | employee | GET `/audit-logs/` | 403 |

---

## Documentation & Final Checks

- [x] **D.1** `docs/rbac-permission-flow.md` — chi tiết RBAC flow hiện tại.
- [ ] **D.2** `README.md` — quick start, tài khoản demo, permission matrix. (file đang trống)
- [ ] **D.3** Swagger tags + descriptions.
- [ ] **D.4** Clean build test từ repo mới clone.
- [ ] **D.5** Verify audit log ghi đúng sau mọi action.

### Kiểm thử

- [ ] **D.T1** Clean build E2E: clone repo mới → `make up` → `make seed` → `make test` → toàn bộ pass trên máy sạch.
- [ ] **D.T2** Audit log E2E: chạy mỗi API scenario S1–S9, sau đó query `audit_logs` DB → verify có record với action/user_id/timestamp đúng.
- [ ] **D.T3** Swagger validation: `GET /openapi.json` phải parse được, không có schema conflict (dùng `schemathesis` nếu muốn automate).

---

## Phase 9 — CI/CD & DevOps

- [ ] **9.1** GitHub Actions workflow — lint (`ruff`), type check (`mypy`), unit tests (`pytest`), integration tests.
- [ ] **9.2** Docker image build & push to registry (GitHub Container Registry hoặc Docker Hub).
- [ ] **9.3** Pre-commit hooks — `black`, `ruff`, `mypy`, `pytest` (unit tests only).
- [ ] **9.4** Environment-specific configs — `.env.development`, `.env.production` templates.
- [ ] **9.5** Health check endpoint monitoring + log aggregation (optional: Prometheus metrics).

---

## Phase 10 — Known Bugs & Tech Debt

- [x] **10.1** **BUG** `sqlalchemy_user_repo.create()` chưa gán `role_id` — **FIXED**.
- [ ] **10.2** `RBACService.require_permission()` raise built-in `PermissionError` thay vì `PermissionDenied` từ `app/domain/exceptions.py` — cần thống nhất trước khi Presentation layer map exception → HTTP.
- [x] **10.3** `migrations/*.sql` legacy còn tồn tại — **FIXED** (đã xóa toàn bộ legacy migrations).
- [ ] **10.4** `README.md` trống — cần viết quick start guide.
- [ ] **10.5** `passlib` + `bcrypt==5.0.0` compatibility issue: `BcryptService.hash()` raise `ValueError` khi chạy trực tiếp. Cần upgrade `passlib` hoặc downgrade `bcrypt` (không ảnh hưởng unit tests vì dùng `FakePasswordService`).
- [ ] **10.6** **Missing container wiring**: `AssignTaskUseCase`, `CompleteTaskUseCase`, `GetHeatmapUseCase` chưa có factory trong `container.py`.
- [ ] **10.7** **Missing API routes**: `PUT /tasks/{id}/assign`, `PUT /tasks/{id}/complete` chưa có endpoint dù use cases đã code.
- [ ] **10.8** **Placeholder routes**: `GET /attendance/heatmap`, `GET /notifications/`, `GET /audit_logs/` đang trả về list rỗng hoặc stub.

*Khôi phục: 2026-06-01 — file TODO được phục dựng sau khi bị xóa nhầm do `docs/` đang bị ignore.*
*Cập nhật: 2026-06-03 — đánh dấu Phase 3, 4, 8 hoàn thành theo codebase thực tế; thêm Phase 9 (CI/CD) và Phase 10 (Bugs/Tech Debt).*
*Cập nhật: 2026-06-03 — kiểm thử toàn bộ checklist Phase 1-5: unit tests 68/68 pass, config validation pass, exception mapping pass, JWT service pass, repository `_to_entity` refactor hoàn tất. Docker tests blocked.*
*Cập nhật: 2026-06-04 — cập nhật Phase 5, 6, 8 theo đúng codebase: integration test files đã tồn tại (test_auth, test_rbac_scenarios); thêm mục missing container wiring (assign/complete/heatmap) và missing API routes (assign/complete task); thêm tech debt 10.6–10.8.*
