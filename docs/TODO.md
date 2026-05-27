# Master Operation — RBAC Demo: Todo List (Clean Architecture)

> **Stack**: Python 3.12 · FastAPI · PostgreSQL 16 · Docker  
> **Kiến trúc**: Clean Architecture — Domain → Application → Infrastructure → Presentation

---

## Phase 1 — Foundation

### Yêu cầu
- Docker Compose khởi động được toàn bộ hệ thống từ một lệnh duy nhất
- FastAPI app chạy, kết nối được PostgreSQL, SQL migration files sẵn sàng
- Cấu hình load từ `.env`, không hardcode secrets

### Tasks
- [ ] **1.1** `requirements.txt` — fastapi, sqlalchemy, alembic, python-jose, passlib, websockets, pytest-asyncio
- [ ] **1.2** `Dockerfile` — python:3.12-slim, expose 8000, uvicorn entry
- [ ] **1.3** `docker-compose.yml` — services: `api` (port 8000), `db` PostgreSQL 16, `redis`
- [ ] **1.4** `.env.example` — DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES=15
- [ ] **1.5** `app/core/config.py` — Settings class (pydantic-settings), bao gồm `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- [ ] **1.6** `app/infrastructure/database/session.py` — engine, SessionLocal, Base
- [ ] **1.7** Tạo thư mục `migrations/` với cấu trúc SQL files (thay Alembic):
  - `migrations/010_create_migration_history.sql` — bảng tracking chạy migration
  - `migrations/001_create_roles.sql`
  - `migrations/002_create_permissions.sql`
  - `migrations/003_create_role_permissions.sql`
  - `migrations/004_create_departments.sql` — có index `parent_id`, CHECK level 1-4
  - `migrations/005_create_users.sql` — có index email, department_id, role_id
  - `migrations/006_create_tasks.sql` — có index assignee, department
  - `migrations/007_create_leave_requests.sql` — thêm `leave_type`, `rejection_reason`; CONSTRAINT end_date >= start_date
  - `migrations/008_create_attendances.sql` — thêm `ip_address`, `total_minutes`, `notes`; UNIQUE (user_id, date)
  - `migrations/009_create_audit_logs.sql` — JSONB details, BIGSERIAL id, index created_at DESC
  - `migrations/011_create_leave_balances.sql` — UNIQUE(user_id, year), computed remaining_days
  - `migrations/012_create_notifications.sql` — index (recipient_id, is_read) cho unread query
- [ ] **1.8** `migrations/run_migrations.sh` — script chạy theo thứ tự, skip nếu đã applied (idempotent)
- [ ] **1.9** `app/main.py` — FastAPI app, CORS middleware, `GET /health`

### Kiểm thử đầu ra
```bash
# 1. Build và khởi động
docker-compose up --build -d

# 2. Chạy SQL migrations theo thứ tự
docker-compose exec api bash migrations/run_migrations.sh
# → 010 → 001 → 002 → ... → 009, mọi file phải in "✓ Applied"

# 3. Xác nhận 12 tables tạo đúng
docker-compose exec db psql -U postgres -d masterop -c "\dt"
# → roles, permissions, role_permissions, departments, users,
#   tasks, leave_requests, leave_balances, attendances,
#   audit_logs, notifications, migration_history

# 4. Health check
curl http://localhost:8000/health
# → {"status": "ok", "db": "connected"}

# 5. Migration idempotent
docker-compose exec api bash migrations/run_migrations.sh
# → mọi file in "⏭ Skipped (already applied)"
```
**Đầu ra mong đợi**: 12 tables tạo thành công, script idempotent, health check 200.

---

## Phase 2 — Domain Layer

### Yêu cầu
- Entities là pure Python dataclasses — **không import SQLAlchemy, FastAPI, hay bất kỳ thư viện external nào**
- Repository interfaces là ABCs thuần túy — chỉ định nghĩa contract, không có implementation
- `RBACService` chứa toàn bộ business logic phân quyền — testable không cần DB
- `DepartmentTreeService` xử lý đúng cây phân cấp đệ quy 4 tầng

### Tasks

**Entities** (sync với ERD v2)
- [ ] **2.1** `app/domain/entities/user.py` — `User(id, employee_code, email, full_name, phone, job_title, contract_type, role_name, department_id, manager_id, zalo_id, telegram_username, hire_date, is_active)`
- [ ] **2.2** `app/domain/entities/department.py` — `Department(id, name, level, parent_id, head_id, code)`
- [ ] **2.3** `app/domain/entities/task.py` — `Task(id, task_code, title, assignee_id, assigner_id, department_id, status, priority, start_date, due_date, estimated_hours)`
- [ ] **2.4** `app/domain/entities/leave.py` — `Leave(id, requester_id, leave_type, start_date, end_date, reason, status, reviewed_by, rejection_reason)`
- [ ] **2.5** `app/domain/entities/leave_balance.py` — `LeaveBalance(id, user_id, year, total_days, used_days, pending_days, remaining_days)`
- [ ] **2.6** `app/domain/entities/attendance.py` — `Attendance(id, user_id, date, check_in, check_out, total_minutes, ip_address, notes, status)`
- [ ] **2.7** `app/domain/entities/notification.py` — `Notification(id, recipient_id, type, channel, message, payload, is_read, sent_at)`
- [ ] **2.8** `app/domain/entities/audit_log.py` — `AuditLog(id, user_id, action, resource, resource_id, details, ip_address, user_agent, created_at)`
- [ ] **2.9** `app/domain/exceptions.py` — `PermissionDenied`, `ScopeViolation`, `ResourceNotFound`, `BusinessRuleViolation`

**Repository Interfaces**
- [ ] **2.8** `app/domain/repositories/user_repository.py` — `IUserRepository(ABC)`
- [ ] **2.9** `app/domain/repositories/task_repository.py` — `ITaskRepository(ABC)`
- [ ] **2.10** `app/domain/repositories/leave_repository.py` — `ILeaveRepository(ABC)`
- [ ] **2.11** `app/domain/repositories/attendance_repository.py` — `IAttendanceRepository(ABC)`
- [ ] **2.12** `app/domain/repositories/audit_log_repository.py` — `IAuditLogRepository(ABC)`

**Domain Services**
- [ ] **2.13** `app/domain/services/rbac_service.py`
  - `PERMISSION_MATRIX`: 4 roles × 9 permissions
  - `has_permission(user, permission_code) -> bool`
  - `get_attendance_scope(user) -> Literal["all","department","self"]`
  - `get_task_scope(user) -> Literal["all","department","self"]`
- [ ] **2.14** `app/domain/services/department_tree.py`
  - `get_descendants(dept_id, all_depts) -> set[int]`
  - `is_ancestor_of(ancestor_id, target_id, all_depts) -> bool`

### Kiểm thử đầu ra
```bash
# Chạy unit tests không cần DB (chỉ dùng Python stdlib)
pytest tests/unit/domain/ -v
```
**Test cases bắt buộc pass:**
```
✓ test_employee_has_no_approve_leave_permission
✓ test_admin_has_all_permissions
✓ test_manager_has_no_manage_org_permission
✓ test_bod_can_view_attendance_all
✓ test_employee_attendance_scope_is_self
✓ test_manager_attendance_scope_is_department
✓ test_dept_tree_is_ancestor_of_true
✓ test_dept_tree_is_ancestor_of_false_sibling
✓ test_dept_tree_get_descendants_returns_subtree
```
**Đầu ra mong đợi**: 9/9 tests pass, zero imports của SQLAlchemy/FastAPI trong `app/domain/`.

---

## Phase 3 — Application Layer

### Yêu cầu
- Use Cases chứa **toàn bộ business flow** — không có logic trong routers
- Ports (ITokenService, IPasswordService, INotificationService) là interfaces — Application không biết đến implementation cụ thể
- DTOs là Pydantic models — dùng để truyền dữ liệu giữa layers, không phải HTTP schema

### Tasks

**Ports**
- [ ] **3.1** `app/application/ports/token_port.py` — `ITokenService(ABC)`: `create_token`, `decode_token`
- [ ] **3.2** `app/application/ports/password_port.py` — `IPasswordService(ABC)`: `hash`, `verify`
- [ ] **3.3** `app/application/ports/notification_port.py` — `INotificationService(ABC)`: `notify_leave_request`, `notify_task_assigned`, `notify_leave_reviewed`

**DTOs**
- [ ] **3.4** `app/application/dtos/auth_dto.py` — `LoginInputDTO`, `TokenOutputDTO`
- [ ] **3.5** `app/application/dtos/user_dto.py` — `UserDTO`, `CreateUserDTO`
- [ ] **3.6** `app/application/dtos/task_dto.py` — `TaskDTO`, `CreateTaskDTO`, `AssignTaskDTO`
- [ ] **3.7** `app/application/dtos/leave_dto.py` — `LeaveDTO`, `CreateLeaveDTO`
- [ ] **3.8** `app/application/dtos/attendance_dto.py` — `AttendanceDTO`, `HeatmapDTO`

**Use Cases**
- [ ] **3.9** `use_cases/auth/login_use_case.py` — verify credentials → tạo JWT
- [ ] **3.10** `use_cases/auth/get_me_use_case.py`
- [ ] **3.11** `use_cases/user/list_users_use_case.py` — scope: admin/bod=all, manager=dept only
- [ ] **3.12** `use_cases/user/create_user_use_case.py` — admin only, hash password
- [ ] **3.13** `use_cases/task/list_tasks_use_case.py` — scope 3 tầng
- [ ] **3.14** `use_cases/task/create_task_use_case.py` — employee=self; manager=any in dept
- [ ] **3.15** `use_cases/task/assign_task_use_case.py` — scope check + notify assignee
- [ ] **3.16** `use_cases/leave/create_leave_use_case.py` — tạo đơn + notify manager
- [ ] **3.17** `use_cases/leave/list_leaves_use_case.py` — scope filter
- [ ] **3.18** `use_cases/leave/review_leave_use_case.py` — permission + scope + update + notify + audit
- [ ] **3.19** `use_cases/attendance/checkin_use_case.py` — self only, prevent duplicate
- [ ] **3.20** `use_cases/attendance/get_heatmap_use_case.py` — scope: self/dept/all

### Kiểm thử đầu ra
```bash
# Unit test với mock repositories (không cần DB)
pytest tests/unit/application/ -v
```
**Test cases bắt buộc pass:**
```
✓ test_login_wrong_password_raises_exception
✓ test_review_leave_employee_raises_permission_denied
✓ test_review_leave_manager_wrong_dept_raises_scope_violation
✓ test_review_leave_manager_correct_dept_succeeds
✓ test_create_task_employee_assign_others_raises_exception
✓ test_heatmap_employee_scope_returns_self_only
✓ test_heatmap_manager_scope_returns_dept
✓ test_heatmap_admin_scope_returns_all
```
**Đầu ra mong đợi**: 8/8 pass, mock repos không cần DB connection.

---

## Phase 4 — Infrastructure Layer

### Yêu cầu
- SQLAlchemy models chỉ tồn tại trong `infrastructure/`, không leak lên Application hay Domain
- Mỗi repository implementation có hàm `_to_entity()` convert ORM → Domain Entity
- `JWTService` implement đúng `ITokenService`, access token expire 15 phút
- `MockNotificationService` log ra console theo format `[ZALO MOCK]` và gửi WebSocket

### Tasks

**ORM Models**
- [ ] **4.1** `infrastructure/database/models/role_model.py`
- [ ] **4.2** `infrastructure/database/models/permission_model.py` + bảng `role_permissions` (M2M)
- [ ] **4.3** `infrastructure/database/models/department_model.py` — self-referential FK `parent_id`
- [ ] **4.4** `infrastructure/database/models/user_model.py`
- [ ] **4.5** `infrastructure/database/models/task_model.py`
- [ ] **4.6** `infrastructure/database/models/leave_model.py`
- [ ] **4.7** `infrastructure/database/models/attendance_model.py`
- [ ] **4.8** `infrastructure/database/models/audit_log_model.py` — `details` column type JSON
- [ ] **4.9** Alembic migration: `alembic revision --autogenerate -m "init_all_tables"` → `alembic upgrade head`

**Repository Implementations**
- [ ] **4.10** `sqlalchemy_user_repo.py` — implements `IUserRepository`
- [ ] **4.11** `sqlalchemy_task_repo.py` — implements `ITaskRepository`
- [ ] **4.12** `sqlalchemy_leave_repo.py` — implements `ILeaveRepository`
- [ ] **4.13** `sqlalchemy_attendance_repo.py` — implements `IAttendanceRepository`
- [ ] **4.14** `sqlalchemy_audit_log_repo.py` — implements `IAuditLogRepository`
- [ ] **4.15** Mỗi repo: `_to_entity(model) -> DomainEntity` method

**Security & Notifications**
- [ ] **4.16** `infrastructure/security/jwt_service.py` — implements `ITokenService`
- [ ] **4.17** `infrastructure/security/bcrypt_service.py` — implements `IPasswordService`
- [ ] **4.18** `infrastructure/notifications/websocket_manager.py` — `connect`, `disconnect`, `send_to_user`, `broadcast_to_dept`
- [ ] **4.19** `infrastructure/notifications/telegram_notification_service.py` — implements `INotificationService`
  - `_send_message(chat_id, text)` — gọi `https://api.telegram.org/bot{TOKEN}/sendMessage`
  - `notify_leave_request()` — gửi Telegram **và** push WebSocket đến manager
  - `notify_task_assigned()` — gửi Telegram đến assignee
  - `notify_leave_reviewed()` — gửi Telegram đến requester (approved/rejected)
  - Dùng `httpx.AsyncClient` để gọi Telegram API bất đồng bộ

### Kiểm thử đầu ra
```bash
# 1. Xác nhận tables tạo đúng (chạy sau Phase 1)
docker-compose exec db psql -U postgres -d masterop -c "\dt"
# → 10 tables hiển thị

# 2. Test infrastructure với PostgreSQL thật
pytest tests/integration/test_infrastructure.py -v
```
**Test cases bắt buộc pass:**
```
✓ test_user_repo_find_by_email_returns_entity (not ORM model)
✓ test_leave_repo_update_status_persists
✓ test_jwt_service_token_expires_in_15_min
✓ test_jwt_service_decode_expired_token_raises
✓ test_bcrypt_hash_and_verify
✓ test_websocket_manager_send_to_user
✓ test_telegram_service_sends_correct_payload  # mock httpx
```

---

## Phase 5 — Presentation Layer

### Yêu cầu
- Routers **không chứa business logic** — chỉ gọi use case, map exception → HTTPException
- Pydantic schemas chỉ dùng trong presentation layer (không dùng làm DTOs cho use cases)
- Swagger UI có đủ tags, descriptions, example values để mentor tự test
- `audit_middleware` ghi log tự động sau mọi request có status 2xx

### Tasks

**Dependencies**
- [ ] **5.1** `presentation/dependencies/db_deps.py` — `get_db()` session generator
- [ ] **5.2** `presentation/dependencies/auth_deps.py` — `get_current_user()`, `get_current_active_user()`

**Pydantic Schemas (HTTP only)**
- [ ] **5.3** `presentation/schemas/auth_schema.py` — `LoginRequest`, `TokenResponse`
- [ ] **5.4** `presentation/schemas/user_schema.py` — `UserResponse` (no hashed_password), `CreateUserRequest`
- [ ] **5.5** `presentation/schemas/task_schema.py`, `leave_schema.py`, `attendance_schema.py`

**API Routers**
- [ ] **5.6** `api/v1/auth.py` — `POST /auth/login`, `GET /auth/me`
- [ ] **5.7** `api/v1/users.py` — `GET /users/`, `GET /users/{id}`, `POST /users/`
- [ ] **5.8** `api/v1/tasks.py` — `GET /tasks/`, `POST /tasks/`, `PUT /tasks/{id}/assign`, `PUT /tasks/{id}/status`
- [ ] **5.9** `api/v1/leaves.py` — `POST /leaves/`, `GET /leaves/`, `PUT /leaves/{id}/approve`, `PUT /leaves/{id}/reject`
- [ ] **5.10** `api/v1/attendance.py` — `POST /attendance/checkin`, `POST /attendance/checkout`, `GET /attendance/heatmap`
- [ ] **5.11** `api/v1/departments.py` — `GET /departments/tree`, `POST /departments/`
- [ ] **5.12** `api/v1/notifications.py` — `WS /ws/notifications`, `GET /notifications/`
- [ ] **5.13** `api/v1/audit_logs.py` — `GET /audit-logs/` (Admin only)
- [ ] **5.14** Tất cả routers: catch `PermissionDenied` → 403, `ResourceNotFound` → 404, `ScopeViolation` → 403

**Middleware**
- [ ] **5.15** `presentation/middleware/audit_middleware.py` — log sau 2xx requests

### Kiểm thử đầu ra
```bash
# 1. Swagger UI có đủ endpoints
curl http://localhost:8000/openapi.json | python3 -c "
import json,sys; spec=json.load(sys.stdin)
paths=list(spec['paths'].keys())
print(f'Total endpoints: {len(paths)}')
print('\n'.join(paths))
"
# → Phải thấy ≥ 15 endpoints

# 2. Endpoint không có token → 401
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/users/
# → 401

# 3. Swagger UI render đúng
curl -s http://localhost:8000/docs | grep -c "swagger"
# → > 0
```
**Đầu ra mong đợi**: ≥15 endpoints, 401 khi không auth, Swagger renders.

---

## Phase 6 — Dependency Injection Container

### Yêu cầu
- `container.py` là **điểm duy nhất** wire infrastructure implementations vào application ports
- Routers không khởi tạo trực tiếp bất kỳ infrastructure class nào
- Dễ swap implementations (ví dụ: thay `MockNotificationService` bằng `ZaloNotificationService`)

### Tasks
- [ ] **6.1** `app/container.py`
  - `get_token_service() -> ITokenService` → `JWTService`
  - `get_password_service() -> IPasswordService` → `BcryptService`
  - `get_notification_service() -> INotificationService` → `MockNotificationService`
  - `get_user_repo(db) -> IUserRepository` → `SQLAlchemyUserRepository`
  - `get_*_use_case()` → inject tất cả dependencies
- [ ] **6.2** Tất cả routers dùng `Depends(get_*_use_case)` từ container
- [ ] **6.3** `GET /health` trả `{"status":"ok","db":"connected","version":"1.0.0"}`
- [ ] **6.4** `.env.example` bổ sung `TELEGRAM_BOT_TOKEN=your_bot_token` và `TELEGRAM_CHAT_ID=your_chat_id`

### Kiểm thử đầu ra
```bash
# Verify không có circular imports
python3 -c "from app.main import app; print('Import OK')"

# Verify DI wiring đúng
python3 -c "
from app.container import get_review_leave_use_case
from app.application.use_cases.leave.review_leave_use_case import ReviewLeaveUseCase
print('DI wiring OK')
"
```
**Đầu ra mong đợi**: Không có `ImportError` hay `CircularDependency`.

---

## Phase 7 — Database Seeding

### Yêu cầu
- Script idempotent: chạy nhiều lần không lỗi, không tạo duplicate
- 3 tài khoản demo với mật khẩu bcrypt đã hash
- Dữ liệu đủ để demo tất cả 9 RBAC scenarios

### Tasks
- [ ] **7.1** `app/infrastructure/database/seed.py`
  - 4 Roles: admin, bod, manager, employee
  - 9 Permissions + gán đúng Permission Matrix
  - Org 4 tầng: [Công ty] → [Ban A]/[Ban B] → [Phòng X]/[Phòng Y]/[Phòng Z] → [Nhóm]
  - 3 tài khoản demo (bảng bên dưới) + 7 users phụ phân bổ đều các phòng
  - 15 tasks (backlog/todo/in_progress/done), 5 leave requests (2 pending, 2 approved, 1 rejected)
  - 30 ngày attendance records, leave_balance cho mỗi user (năm hiện tại)
  - Thông báo mẫu trong bảng `notifications`
- [ ] **7.2** `Makefile` — targets: `make up`, `make seed`, `make test`, `make down`
- [ ] **7.3** Đảm bảo script idempotent (dùng `INSERT ... ON CONFLICT DO NOTHING`)

| Email | Password | Role | Đơn vị |
|-------|----------|------|--------|
| `admin@company.vn` | `Admin@123` | Admin | [Công ty] |
| `manager@company.vn` | `Manager@123` | Manager | [Phòng Z] |
| `employee@company.vn` | `Employee@123` | Employee | [Phòng Z] |

### Kiểm thử đầu ra
```bash
# 1. Chạy seed lần 1
docker-compose exec api python -m app.infrastructure.database.seed
# → "Seeding completed successfully"

# 2. Chạy seed lần 2 (idempotent)
docker-compose exec api python -m app.infrastructure.database.seed
# → Không lỗi, không duplicate

# 3. Verify dữ liệu
docker-compose exec db psql -U postgres -d masterop -c "
SELECT r.name, COUNT(u.id) as user_count
FROM roles r LEFT JOIN users u ON u.role_id = r.id
GROUP BY r.name;
"
# → admin:1, bod:1, manager:3, employee:5+ rows

# 4. Verify login với tài khoản demo
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.vn","password":"Admin@123"}'
# → {"access_token":"...","token_type":"bearer"}
```

---

## Phase 8 — Tests

### Yêu cầu
- Unit tests chạy không cần Docker/DB (dùng mock)
- Integration tests chạy với PostgreSQL test DB (isolated)
- 9 RBAC scenarios phải có test case tương ứng
- Coverage ≥ 80% cho `app/domain/` và `app/application/`

### Tasks

**Unit Tests**
- [ ] **8.1** `tests/unit/domain/test_rbac_service.py` (9 assertions)
- [ ] **8.2** `tests/unit/domain/test_department_tree.py` (4 assertions)
- [ ] **8.3** `tests/unit/application/test_review_leave_use_case.py` — mock repos
- [ ] **8.4** `tests/unit/application/test_heatmap_use_case.py` — mock repos

**Integration Tests**
- [ ] **8.5** `tests/integration/conftest.py` — test DB fixtures, token helpers
- [ ] **8.6** `tests/integration/test_auth.py` — login, wrong password, expired JWT
- [ ] **8.7** `tests/integration/test_rbac_scenarios.py` — 9 scenarios:

| # | Actor | Action | Expected |
|---|-------|--------|----------|
| S1 | Employee | GET /users/ (phòng khác) | **403** |
| S2 | Manager | PUT /leaves/{id}/approve (cùng phòng) | **200** |
| S3 | Manager | PUT /leaves/{id}/approve (phòng khác) | **403** |
| S4 | Employee | POST /tasks/ (assign người khác) | **403** |
| S5 | Manager | PUT /tasks/{id}/assign (cùng phòng) | **200** |
| S6 | Employee | POST /attendance/checkin | **200** |
| S7 | Employee | GET /attendance/heatmap | Chỉ thấy data mình |
| S8 | Manager | GET /attendance/heatmap | Thấy toàn phòng |
| S9 | Employee | GET /audit-logs/ | **403** |

- [ ] **8.8** `tests/integration/test_websocket.py` — connect WS, receive notification
- [ ] **8.9** `tests/integration/test_audit_log.py` — mọi action được ghi log

### Kiểm thử đầu ra
```bash
# 1. Unit tests (không cần Docker)
pytest tests/unit/ -v --tb=short
# → Pass tất cả, thời gian < 5 giây

# 2. Integration tests
pytest tests/integration/ -v --tb=short
# → Pass tất cả 9 RBAC scenarios

# 3. Coverage report
pytest tests/ --cov=app --cov-report=term-missing
# → Domain coverage ≥ 80%, Application coverage ≥ 80%

# 4. Full run
pytest tests/ -v --tb=short -q
# → X passed, 0 failed, 0 error
```
**Đầu ra mong đợi**: 100% test pass, coverage ≥ 80%.

---

## Documentation & Final Checks

- [ ] **D.1** `README.md` — quick start, tài khoản demo, permission matrix, 9 scenarios
- [ ] **D.2** Swagger tags + descriptions + example values cho tất cả endpoints
- [ ] **D.3** Clean build test từ repo mới clone:
  ```bash
  git clone ... && cd master-operation
  cp .env.example .env
  docker-compose up --build -d
  make seed
  pytest tests/ -v
  ```
- [ ] **D.4** Verify audit log ghi đúng sau mọi action

---

## ✅ Demo Checklist Cuối Cùng

| Kịch bản | Tài khoản | Kết quả mong đợi |
|----------|-----------|-----------------|
| Đăng nhập | 3 tài khoản demo | JWT token trả về |
| Xem tất cả user | admin | 200, thấy tất cả |
| Xem user list | manager | 200, chỉ thấy phòng mình |
| Duyệt đơn phép cùng phòng | manager | 200, WS notification gửi đến employee |
| Duyệt đơn phép phòng khác | manager | 403 Forbidden |
| Tạo task cho người khác | employee | 403 Forbidden |
| Check-in | employee | 200, tạo attendance record |
| Xem heatmap | employee | Chỉ thấy data cá nhân |
| Xem heatmap | manager | Thấy toàn phòng |
| Xem audit log | employee | 403 Forbidden |
| Xem audit log | admin | 200, thấy toàn bộ lịch sử |
| Nhận WS notification | manager | Hiển thị ngay khi employee gửi đơn |

*Cập nhật: 2026-05-27 — Clean Architecture với Requirements & Test Criteria*
