# Master Operation — RBAC Demo: Implementation Plan (Clean Architecture + SQLAlchemy 2.0)

Tài liệu này mô tả kế hoạch triển khai RBAC demo theo Clean Architecture. Nội dung được khôi phục lại sau khi file gốc bị xóa nhầm do `docs/` đang nằm trong `.gitignore`.

---

## 1. Tổng quan

Demo phân quyền đa tầng theo RBAC:

```text
Presentation → Application → Domain ← Infrastructure
```

Ý tưởng chính:

```text
User → Role → Permission
```

Runtime flow:

```text
Auth/API layer
  → UserRepository.find_by_id/find_by_email
  → SQLAlchemy eager-load UserModel → RoleModel → PermissionModel
  → map sang User.permissions: set[str]
  → RBACService.has_permission()/require_permission()
```

---

## 2. Kiến trúc thư mục mục tiêu

```text
app/
  domain/
    entities/
      user.py
      role.py
      permission.py
      role_permission.py
      department.py
      task.py
      leave_request.py
      leave_balance.py
      attendance.py
      notification.py
      audit_log.py
    repositories/
      user_repository.py
      task_repository.py
      leave_request_repository.py
      leave_balance_repository.py
      attendance_repository.py
      notification_repository.py
      audit_log_repository.py
    services/
      rbac_service.py
      department_tree.py
    exceptions.py

  application/
    use_cases/
      auth/
        login_use_case.py
        get_me_use_case.py
      user/
        list_users_use_case.py
        create_user_use_case.py
      task/
        list_tasks_use_case.py
        create_task_use_case.py
        assign_task_use_case.py
      leave_request/
        create_leave_request_use_case.py
        list_leave_requests_use_case.py
        review_leave_request_use_case.py
      attendance/
        checkin_use_case.py
        get_heatmap_use_case.py
    dtos/
    ports/

  infrastructure/
    database/
      base.py
      session.py
      models/
        role_model.py
        permission_model.py
        role_permission_model.py
        department_model.py
        user_model.py
        task_model.py
        leave_request_model.py
        leave_balance_model.py
        attendance_model.py
        notification_model.py
        audit_log_model.py
      repositories/        # current code has typo: repositoties/
        sqlalchemy_user_repo.py
        sqlalchemy_task_repo.py
        sqlalchemy_leave_request_repo.py
        sqlalchemy_leave_balance_repo.py
        sqlalchemy_attendance_repo.py
        sqlalchemy_notification_repo.py
        sqlalchemy_audit_log_repo.py
      seed.py
    security/
      jwt_service.py
      bcrypt_service.py
    notifications/
      websocket_manager.py
      telegram_notification_service.py

  presentation/
    api/v1/
      auth.py
      users.py
      tasks.py
      leaves.py
      attendance.py
      departments.py
      notifications.py
      audit_logs.py
    schemas/
    dependencies/
      auth_deps.py
      db_deps.py
    middleware/
      audit_middleware.py

  container.py
  main.py
```

---

## 3. Domain Layer

### 3.1 `User` Rich Domain Entity

File hiện có:

```text
app/domain/entities/user.py
```

`User` chứa permission passport đã được repository nạp từ DB:

```python
@dataclass
class User:
    id: int
    employee_code: str
    email: str
    full_name: str
    role_name: str
    permissions: set[str] = field(default_factory=set)
    department_id: int | None = None
    manager_id: int | None = None
    is_active: bool = True
```

Nguyên tắc:

```text
User không import SQLAlchemy.
User không giữ ORM object.
User.permissions là flat set[str] dùng cho O(1) permission lookup.
```

### 3.2 RBAC entities

Giữ lại các entity sau để domain model dễ đọc:

```text
app/domain/entities/role.py
app/domain/entities/permission.py
app/domain/entities/role_permission.py
```

Chúng tương ứng với DB concepts:

```text
roles
permissions
role_permissions
```

Hiện tại runtime permission check chủ yếu dùng `User.permissions`, nhưng các entity này hữu ích cho use case quản trị role/permission sau này.

### 3.3 `RBACService`

File:

```text
app/domain/services/rbac_service.py
```

Trách nhiệm:

- Không DB
- Không ORM
- Không FastAPI
- Chỉ quyết định quyền từ `actor: User`

Core logic:

```python
def has_permission(self, actor: User, permission_code: str) -> bool:
    if not actor.is_active:
        return False
    if actor.role_name in {"admin"}:
        return True
    return permission_code in actor.permissions
```

Các hàm quan trọng:

```text
has_permission(actor, permission_code) -> bool
require_permission(actor, permission_code) -> None
list_permissions(actor) -> set[str]
get_attendance_scope(actor) -> "all" | "department" | "self"
get_task_scope(actor) -> "all" | "department" | "self"
can_approve_leave_for(actor, is_ancestor) -> bool
```

### 3.4 `DepartmentTreeService`

File:

```text
app/domain/services/department_tree.py
```

Dùng cho manager scope:

```python
is_ancestor_of(actor.department_id, requester.department_id, all_depts)
```

---

## 4. Infrastructure Layer

### 4.1 ORM relationship

Các bảng RBAC:

```text
users.role_id → roles.id
roles.id → role_permissions.role_id
permissions.id → role_permissions.permission_id
```

File chính:

```text
app/infrastructure/database/models/user_model.py
app/infrastructure/database/models/role_model.py
app/infrastructure/database/models/permission_model.py
app/infrastructure/database/models/role_permission_model.py
```

`UserModel.role` dùng `lazy="selectin"`.

`RoleModel.permissions` dùng `secondary="role_permissions"` và `lazy="selectin"`.

### 4.2 `SQLAlchemyUserRepository`

File hiện có:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

> Lưu ý: folder đang bị typo là `repositoties`, nên đổi về `repositories` trước khi mở rộng lớn.

Core flow:

```python
def _base_stmt(self):
    return select(UserModel).options(
        selectinload(UserModel.role).selectinload(RoleModel.permissions)
    )
```

Mapping:

```python
permissions = {p.code for p in model.role.permissions}

return User(
    role_name=model.role.name,
    permissions=permissions,
    ...
)
```

### 4.3 Caveat khi create user

`SQLAlchemyUserRepository.create()` hiện chưa set `role_id`.

Trong code có comment:

```python
# role_id phải được lookup trước khi gọi create, hoặc resolve từ role_name
```

Kế hoạch cần chọn một trong hai hướng:

1. Use case resolve `role_name → role_id` rồi truyền xuống repository.
2. Repository tự lookup role từ `user.role_name` trước khi insert.

Khuyến nghị sạch hơn theo Clean Architecture:

```text
CreateUserUseCase
  → RoleRepository.find_by_name(role_name)
  → SQLAlchemyUserRepository.create(..., role_id hoặc role entity)
```

---

## 5. Application Layer dự kiến

### 5.1 `CreateUserUseCase`

File dự kiến:

```text
app/application/use_cases/user/create_user_use_case.py
```

Flow:

```text
Input DTO
  → actor = current user
  → rbac.require_permission(actor, "manage_org")
  → password_service.hash(password)
  → role_repo.find_by_name(role_name)
  → user_repo.create(user, hashed_password, role_id)
  → return UserDTO
```

Pseudo-code:

```python
async def execute(self, actor: User, data: CreateUserInput) -> UserDTO:
    self.rbac.require_permission(actor, "manage_org")

    hashed_password = self.password_service.hash(data.password)
    role = await self.role_repo.find_by_name(data.role_name)

    user = User(
        id=0,
        employee_code=data.employee_code,
        email=data.email,
        full_name=data.full_name,
        role_name=role.name,
        permissions=set(),
        department_id=data.department_id,
        is_active=True,
    )

    created = await self.user_repo.create(user, hashed_password)
    return UserDTO.from_entity(created)
```

### 5.2 `ReviewLeaveRequestUseCase`

File dự kiến:

```text
app/application/use_cases/leave_request/review_leave_request_use_case.py
```

Flow:

```python
async def execute(self, actor: User, leave_id: int, approved: bool):
    self.rbac.require_permission(actor, "approve_leave")

    leave = await self.leave_repo.find_by_id(leave_id)
    requester = await self.user_repo.find_by_id(leave.requester_id)

    if actor.role_name == "manager":
        all_depts = await self.dept_repo.list_all()
        is_ancestor = self.tree.is_ancestor_of(
            actor.department_id,
            requester.department_id,
            all_depts,
        )
        if not self.rbac.can_approve_leave_for(actor, is_ancestor):
            raise ScopeViolation()

    updated = await self.leave_repo.update_status(leave_id, approved, actor.id)
    await self.audit_repo.log(actor.id, "review_leave", "leave", leave_id, {"approved": approved})
    return LeaveRequestDTO.from_entity(updated)
```

---

## 6. Presentation Layer dự kiến

### 6.1 Auth dependency

File dự kiến:

```text
app/presentation/dependencies/auth_deps.py
```

Flow:

```text
Bearer token
  → jwt_service.decode(token)
  → user_id = payload["sub"]
  → user_repo.find_by_id(user_id)
  → User with permissions passport
```

### 6.2 User router

File dự kiến:

```text
app/presentation/api/v1/users.py
```

Create user endpoint:

```python
@router.post("/users/")
async def create_user(
    data: UserCreateSchema,
    actor: User = Depends(get_current_user),
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
):
    return await use_case.execute(actor, data)
```

### 6.3 Error mapping

Presentation layer cần map:

```text
PermissionError hoặc PermissionDenied → HTTP 403
ResourceNotFound → HTTP 404
BusinessRuleViolation → HTTP 400
```

Hiện `RBACService.require_permission()` raise built-in `PermissionError`, trong khi `app/domain/exceptions.py` có `PermissionDenied`. Cần thống nhất trước khi public API.

---

## 7. API endpoint matrix dự kiến

| Method | Path | Permission | Scope |
|---|---|---|---|
| POST | `/api/v1/auth/login` | — | JWT |
| GET | `/api/v1/auth/me` | authenticated | current user |
| GET | `/api/v1/users/` | `view_personnel` | admin/bod all, manager department |
| POST | `/api/v1/users/` | `manage_org` | admin |
| GET | `/api/v1/tasks/` | authenticated | self/dept/all |
| POST | `/api/v1/tasks/` | `create_task` | business rules |
| PUT | `/api/v1/tasks/{id}/assign` | `assign_task` | manager scope |
| POST | `/api/v1/leaves/` | authenticated | self |
| GET | `/api/v1/leaves/` | authenticated | scoped |
| PUT | `/api/v1/leaves/{id}/approve` | `approve_leave` | manager ancestor/admin/bod |
| PUT | `/api/v1/leaves/{id}/reject` | `approve_leave` | manager ancestor/admin/bod |
| POST | `/api/v1/attendance/checkin` | authenticated | self |
| GET | `/api/v1/attendance/heatmap` | authenticated | self/dept/all |
| GET | `/api/v1/audit-logs/` | `view_audit_log` | admin |

---

## 8. Database seeding plan

File dự kiến:

```text
app/infrastructure/database/seed.py
```

Seed theo thứ tự:

```text
roles
permissions
role_permissions
departments
users
tasks/leaves/attendance demo data
```

Roles mặc định:

```text
admin
bod
manager
employee
```

Permission examples:

```text
manage_org
view_personnel
approve_leave
assign_task
create_task
view_attendance_all
view_attendance_dept
view_attendance_self
view_audit_log
```

---

## 9. Verification plan

```bash
docker-compose up --build -d
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.infrastructure.database.seed
pytest tests/unit/ -v
pytest tests/integration/ -v
```

Manual checks:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.vn","password":"Admin@123"}'
```

Expected RBAC scenarios:

| Scenario | Expected |
|---|---|
| employee xem audit logs | 403 |
| admin xem audit logs | 200 |
| manager duyệt đơn cùng nhánh | 200 |
| manager duyệt đơn ngoài nhánh | 403 |
| employee assign task cho người khác | 403 |

---

## 10. Ghi chú kiến trúc

Giữ kiến trúc hiện tại vì dễ mở rộng use case:

```text
User entity          → data/passport
RBACService          → permission decision
DepartmentTreeService → organization scope
UseCase              → business flow
Repository           → DB access
```

Không đưa toàn bộ logic RBAC vào `User`, vì về lâu dài `User` dễ phình thành god object khi thêm nhiều rule như assign task, approve leave, view attendance, audit log, dashboard scope.

*Khôi phục: 2026-06-01 — file implementation plan được phục dựng sau khi bị xóa nhầm do `docs/` đang bị ignore.*
