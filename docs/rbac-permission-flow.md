# RBAC Permission Flow — Master Operation

Tài liệu này giải thích cách phân quyền RBAC trong dự án hiện tại: dữ liệu nằm ở đâu, được load như thế nào, user mới được gán quyền ra sao, và một lượt kiểm tra permission đi qua file/hàm nào.

> Trạng thái code hiện tại: dự án đã có Domain + ORM + repository RBAC core. Các API router/use case/auth dependency tạo user và login chưa được triển khai đầy đủ; vì vậy tài liệu tách rõ **luồng đã có trong code** và **luồng dự kiến khi thêm API/use case**.

---

## 1. Ý tưởng chính

RBAC của dự án đi theo mô hình:

```text
User → Role → Permission
```

Cụ thể hơn:

```text
users.role_id
    ↓
roles.id
    ↓ many-to-many qua role_permissions
permissions.code
```

Khi hệ thống cần kiểm tra quyền của một user, repository sẽ load user cùng role và permissions từ DB, sau đó map thành `User` domain entity:

```python
User(
    role_name="manager",
    permissions={"approve_leave", "view_attendance_dept"},
)
```

Sau bước đó, `RBACService` chỉ kiểm tra trên `actor.permissions` trong RAM:

```python
permission_code in actor.permissions
```

Nói ngắn gọn:

```text
DB là nguồn sự thật của role/permission.
Repository biến DB data thành User.permissions.
RBACService quyết định có quyền hay không.
```

---

## 2. Cấu trúc file liên quan

### 2.1 Domain entities

| File | Vai trò |
|---|---|
| `app/domain/entities/user.py` | Domain entity chính cho người dùng. Chứa `role_name`, `permissions`, `department_id`, `manager_id`, `is_active`. |
| `app/domain/entities/role.py` | Domain entity mô tả role: `id`, `name`, `display_name`. |
| `app/domain/entities/permission.py` | Domain entity mô tả permission: `id`, `code`, `description`. |
| `app/domain/entities/role_permission.py` | Domain entity mô tả mapping role-permission: `role_id`, `permission_id`. |

Điểm quan trọng: `User` là entity được dùng trực tiếp khi kiểm tra quyền. `Role`, `Permission`, `RolePermission` giúp mô hình domain dễ đọc, nhưng hiện tại runtime check chủ yếu dùng `User.permissions`.

### 2.2 Domain services

| File | Class/Hàm | Vai trò |
|---|---|---|
| `app/domain/services/rbac_service.py` | `RBACService` | Service kiểm tra quyền thuần Python, không DB, không ORM, không FastAPI. |
| `app/domain/services/department_tree.py` | `DepartmentTreeService` | Service kiểm tra cây phòng ban, dùng cho scope manager/cấp dưới. |

Các hàm quan trọng trong `RBACService`:

| Hàm | Input | Output | Ý nghĩa |
|---|---|---|---|
| `has_permission(actor, permission_code)` | `User`, `str` | `bool` | Kiểm tra actor có permission hay không. |
| `require_permission(actor, permission_code)` | `User`, `str` | `None` hoặc raise `PermissionError` | Dùng khi use case muốn fail ngay nếu thiếu quyền. |
| `list_permissions(actor)` | `User` | `set[str]` | Trả về bản copy permissions hiện tại. |
| `get_attendance_scope(actor)` | `User` | `"all" / "department" / "self"` | Xác định phạm vi xem chấm công. |
| `get_task_scope(actor)` | `User` | `"all" / "department" / "self"` | Xác định phạm vi thao tác task. |
| `can_approve_leave_for(actor, is_ancestor)` | `User`, `bool` | `bool` | Rule tổng hợp cho duyệt đơn nghỉ. |

### 2.3 Repository interfaces

| File | Vai trò |
|---|---|
| `app/domain/repositories/user_repository.py` | Interface `UserRepository`; định nghĩa `find_by_id`, `find_by_email`, `find_all`, `list_by_department`, `create`, `update`, `delete`. |

Domain chỉ biết interface này, không biết SQLAlchemy.

### 2.4 Infrastructure ORM models

| File | DB table | Vai trò |
|---|---|---|
| `app/infrastructure/database/models/user_model.py` | `users` | ORM model cho user, có `role_id`, `department_id`, `manager_id`. |
| `app/infrastructure/database/models/role_model.py` | `roles` | ORM model cho role, có relationship `permissions`. |
| `app/infrastructure/database/models/permission_model.py` | `permissions` | ORM model cho permission code. |
| `app/infrastructure/database/models/role_permission_model.py` | `role_permissions` | Bảng trung gian many-to-many giữa role và permission. |

### 2.5 Repository implementation

| File | Class | Vai trò |
|---|---|---|
| `app/infrastructure/database/repositoties/sqlalchemy_user_repo.py` | `SQLAlchemyUserRepository` | Load user từ DB, eager-load role → permissions, map sang `User` domain entity. |

Các hàm quan trọng:

| Hàm | Vai trò |
|---|---|
| `_base_stmt()` | Tạo câu select `UserModel` với `selectinload(UserModel.role).selectinload(RoleModel.permissions)`. |
| `_to_entity(model)` | Map `UserModel` sang `User`, flatten `model.role.permissions` thành `set[str]`. |
| `find_by_id(user_id)` | Load một user theo id, trả về `User | None`. |
| `find_by_email(email)` | Load một user theo email, trả về `User | None`. |
| `create(user, hashed_password="")` | Tạo user mới, sau đó gọi `find_by_id()` để trả về entity đã load lại. |

---

## 3. Data model RBAC trong DB

Theo `docs/erd.md`, phần RBAC gồm 3 bảng chính:

```text
roles
permissions
role_permissions
```

### 3.1 `roles`

Ví dụ dữ liệu:

| id | name | display_name |
|---|---|---|
| 1 | `admin` | Admin |
| 2 | `bod` | Board of Directors |
| 3 | `manager` | Manager |
| 4 | `employee` | Employee |

### 3.2 `permissions`

Ví dụ dữ liệu:

| id | code | description |
|---|---|---|
| 1 | `approve_leave` | Duyệt đơn nghỉ |
| 2 | `view_attendance_all` | Xem chấm công toàn công ty |
| 3 | `view_attendance_dept` | Xem chấm công phòng ban |
| 4 | `view_attendance_self` | Xem chấm công bản thân |
| 5 | `manage_org` | Quản lý tổ chức/user |

### 3.3 `role_permissions`

Bảng này gán permission cho role:

| role_id | permission_id |
|---|---|
| manager | approve_leave |
| manager | view_attendance_dept |
| employee | view_attendance_self |

Sơ đồ:

```text
roles.id ──< role_permissions.role_id
permissions.id ──< role_permissions.permission_id
```

---

## 4. Luồng load user và cấp permission vào `User.permissions`

Đây là luồng quan trọng nhất, vì nó giải thích tại sao runtime check không cần query DB thêm.

### 4.1 Input

Một use case hoặc auth dependency cần lấy user:

```python
user = await user_repo.find_by_id(user_id)
```

hoặc:

```python
user = await user_repo.find_by_email(email)
```

### 4.2 Đi qua file/hàm nào?

#### Bước 1 — gọi repository interface

File:

```text
app/domain/repositories/user_repository.py
```

Interface:

```python
async def find_by_id(self, user_id: int) -> User | None
async def find_by_email(self, email: str) -> User | None
```

Ở tầng domain/application, code chỉ phụ thuộc interface này.

#### Bước 2 — implementation chạy query SQLAlchemy

File:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm:

```python
SQLAlchemyUserRepository.find_by_id(user_id)
SQLAlchemyUserRepository.find_by_email(email)
```

Hai hàm này gọi:

```python
stmt = self._base_stmt().where(...)
```

#### Bước 3 — `_base_stmt()` eager-load role và permissions

File:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm:

```python
def _base_stmt(self):
    return select(UserModel).options(
        selectinload(UserModel.role).selectinload(RoleModel.permissions)
    )
```

Ý nghĩa:

```text
Load UserModel
  → load RoleModel của user
      → load PermissionModel list của role
```

SQLAlchemy sẽ phát các query dạng:

```text
1. SELECT * FROM users WHERE id = ?
2. SELECT * FROM roles WHERE id IN (...)
3. SELECT permissions.*
   FROM permissions
   JOIN role_permissions ON role_permissions.permission_id = permissions.id
   WHERE role_permissions.role_id IN (...)
```

#### Bước 4 — `_to_entity()` map ORM sang domain

File:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm:

```python
def _to_entity(self, model: UserModel) -> User:
```

Đoạn quan trọng:

```python
permissions: set[str] = (
    {p.code for p in model.role.permissions}
    if model.role and model.role.permissions
    else set()
)
```

Sau đó trả về:

```python
User(
    id=model.id,
    employee_code=model.employee_code,
    email=model.email,
    full_name=model.full_name,
    role_name=model.role.name if model.role else "",
    permissions=permissions,
    department_id=model.department_id,
    manager_id=model.manager_id,
    is_active=model.is_active,
)
```

### 4.3 Output

Output của repository là domain entity:

```python
User(
    id=42,
    employee_code="EMP0042",
    email="manager@example.com",
    full_name="Manager A",
    role_name="manager",
    permissions={"approve_leave", "view_attendance_dept"},
    department_id=3,
    manager_id=None,
    is_active=True,
)
```

Từ thời điểm này, domain/application không cần biết DB đã join thế nào. Nó chỉ nhận `User` đã có `permissions`.

---

## 5. Luồng tạo user mới và user đó được phân quyền thế nào

### 5.1 Trạng thái hiện tại trong code

Hiện tại dự án mới có repository method:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm:

```python
async def create(self, user: User, hashed_password: str = "") -> User:
```

Nhưng method này hiện có ghi chú:

```python
# role_id phải được lookup trước khi gọi create, hoặc resolve từ role_name
```

Điều này nghĩa là: luồng tạo user hoàn chỉnh chưa xong. `UserModel` cần `role_id`, nhưng domain `User` chỉ có `role_name`. Vì vậy trước khi insert user, hệ thống cần thêm một bước resolve:

```text
role_name → roles.id
```

Có 2 cách hoàn thiện:

1. Use case lookup `RoleModel.id` hoặc gọi một `RoleRepository` trước khi gọi `SQLAlchemyUserRepository.create()`.
2. `SQLAlchemyUserRepository.create()` tự resolve `role_name` thành `role_id` trước khi tạo `UserModel`.

Hiện tại code comment đang để mở cả hai hướng.

### 5.2 Luồng tạo user dự kiến

Ví dụ admin tạo manager mới.

#### Input từ API

```json
{
  "employee_code": "EMP0042",
  "email": "manager@example.com",
  "full_name": "Manager A",
  "role_name": "manager",
  "department_id": 3,
  "password": "Manager@123"
}
```

#### Bước 1 — router nhận request

File dự kiến:

```text
app/presentation/api/v1/users.py
```

Hàm dự kiến:

```python
create_user(...)
```

Trạng thái hiện tại: file router này chưa có. `app/main.py` hiện chỉ có `/health`.

#### Bước 2 — auth dependency lấy actor hiện tại

File dự kiến:

```text
app/presentation/dependencies/auth_deps.py
```

Hàm dự kiến:

```python
get_current_user()
```

Output dự kiến:

```python
actor = User(role_name="admin", permissions={...})
```

#### Bước 3 — use case kiểm tra actor có quyền tạo user

File dự kiến:

```text
app/application/use_cases/user/create_user_use_case.py
```

Hàm dự kiến:

```python
execute(actor: User, input_dto: CreateUserInput)
```

Use case nên gọi:

```python
rbac.require_permission(actor, "manage_org")
```

Đi qua:

```text
app/domain/services/rbac_service.py
RBACService.require_permission(actor, "manage_org")
  → RBACService.has_permission(actor, "manage_org")
```

Nếu actor thiếu quyền:

```text
raise PermissionError
```

Presentation layer nên map lỗi này thành HTTP 403.

#### Bước 4 — hash password

File dự kiến:

```text
app/infrastructure/security/bcrypt_service.py
```

Trạng thái hiện tại: chưa có implementation.

Output:

```python
hashed_password = "..."
```

#### Bước 5 — resolve role

Input:

```python
role_name = "manager"
```

Query cần chạy:

```sql
SELECT id FROM roles WHERE name = 'manager';
```

Output:

```python
role_id = 3
```

#### Bước 6 — insert user

File hiện có:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm hiện có:

```python
SQLAlchemyUserRepository.create(user, hashed_password)
```

Nó tạo:

```python
UserModel(
    employee_code=user.employee_code,
    email=user.email,
    full_name=user.full_name,
    hashed_password=hashed_password,
    department_id=user.department_id,
    manager_id=user.manager_id,
    is_active=user.is_active,
)
```

Điểm cần hoàn thiện: phải set `role_id` vào `UserModel` trước khi insert.

#### Bước 7 — load lại user đã tạo

Sau insert:

```python
await self._session.flush()
await self._session.refresh(model)
return await self.find_by_id(model.id)
```

Hàm `find_by_id()` sẽ đi qua `_base_stmt()` và `_to_entity()` như mục 4, nên output cuối cùng là:

```python
User(
    id=42,
    role_name="manager",
    permissions={"approve_leave", "view_attendance_dept", ...},
)
```

### 5.3 User mới được phân quyền ở đâu?

User mới **không được gán permission trực tiếp**.

User mới được phân quyền qua role:

```text
users.role_id = roles.id
roles.id → role_permissions → permissions
```

Ví dụ:

```text
Tạo user với role_name = "manager"
  → resolve ra role_id của manager
  → insert users.role_id = manager.id
  → lần sau load user sẽ lấy permissions của role manager
```

Vì vậy muốn thay đổi quyền của tất cả manager, không sửa từng user. Chỉ sửa mapping:

```text
role_permissions(manager, permission)
```

---

## 6. Luồng kiểm tra permission cho một request bất kỳ

Ví dụ request: manager duyệt đơn nghỉ.

```http
PUT /api/v1/leaves/123/approve
Authorization: Bearer <token>
```

### 6.1 Luồng tổng quát

```text
Client request
  ↓
FastAPI router
  ↓
Auth dependency decode token
  ↓
SQLAlchemyUserRepository.find_by_id(user_id)
  ↓
_base_stmt(): load user → role → permissions
  ↓
_to_entity(): User.permissions = {permission codes}
  ↓
Use case nhận actor: User
  ↓
RBACService.require_permission(actor, "approve_leave")
  ↓
RBACService.has_permission(actor, "approve_leave")
  ↓
True: tiếp tục business logic
False: raise PermissionError → HTTP 403
```

### 6.2 File/hàm chi tiết

#### Bước 1 — router nhận request

File dự kiến:

```text
app/presentation/api/v1/leaves.py
```

Hàm dự kiến:

```python
approve_leave(leave_id, current_user, use_case)
```

Trạng thái hiện tại: router chưa được implement.

#### Bước 2 — auth dependency lấy current user

File dự kiến:

```text
app/presentation/dependencies/auth_deps.py
```

Hàm dự kiến:

```python
get_current_user(token, db)
```

Nhiệm vụ:

```text
JWT token → user_id → user_repo.find_by_id(user_id)
```

Output:

```python
current_user: User
```

#### Bước 3 — repository load permission passport

File hiện có:

```text
app/infrastructure/database/repositoties/sqlalchemy_user_repo.py
```

Hàm:

```python
find_by_id(user_id)
```

Gọi:

```python
self._base_stmt()
```

Rồi:

```python
self._to_entity(model)
```

Output:

```python
User(..., role_name="manager", permissions={"approve_leave", ...})
```

#### Bước 4 — use case gọi RBACService

File dự kiến:

```text
app/application/use_cases/leave_request/review_leave_request_use_case.py
```

Hàm dự kiến:

```python
execute(actor: User, leave_id: int, approved: bool)
```

Kiểm tra quyền:

```python
rbac.require_permission(actor, "approve_leave")
```

Đi qua:

```text
app/domain/services/rbac_service.py
RBACService.require_permission()
  → RBACService.has_permission()
```

#### Bước 5 — `RBACService.has_permission()` quyết định

File:

```text
app/domain/services/rbac_service.py
```

Hàm:

```python
def has_permission(self, actor: User, permission_code: str) -> bool:
```

Logic:

```python
if not actor.is_active:
    return False
if actor.role_name in {"admin"}:
    return True
return permission_code in actor.permissions
```

Input ví dụ:

```python
actor.role_name = "manager"
actor.permissions = {"approve_leave", "view_attendance_dept"}
permission_code = "approve_leave"
```

Output:

```python
True
```

Nếu permission không có:

```python
False
```

Nếu dùng `require_permission()`, output khi thiếu quyền là exception:

```python
PermissionError("Role 'employee' lacks permission 'approve_leave'.")
```

#### Bước 6 — scope rule nếu cần

Một số quyền không chỉ là có/không, mà còn có phạm vi.

Ví dụ manager có `approve_leave`, nhưng chỉ được duyệt nhân viên trong nhánh phòng ban mình quản lý.

Đi qua file:

```text
app/domain/services/department_tree.py
```

Hàm:

```python
DepartmentTreeService.is_ancestor_of(
    ancestor_id=actor.department_id,
    target_id=requester.department_id,
    all_depts=departments,
)
```

Output:

```python
is_ancestor: bool
```

Sau đó gọi:

```python
RBACService.can_approve_leave_for(actor, is_ancestor)
```

Logic:

```python
if not self.has_permission(actor, "approve_leave"):
    return False
if actor.role_name in ("admin", "bod"):
    return True
return is_ancestor
```

---

## 7. Ví dụ cụ thể: employee gọi API duyệt đơn nghỉ

### Input

```python
actor = User(
    id=10,
    role_name="employee",
    permissions={"view_attendance_self"},
    is_active=True,
    ...
)
```

Use case gọi:

```python
rbac.require_permission(actor, "approve_leave")
```

### Đi qua hàm

```text
RBACService.require_permission(actor, "approve_leave")
  ↓
RBACService.has_permission(actor, "approve_leave")
  ↓
actor.is_active == True
  ↓
actor.role_name != "admin"
  ↓
"approve_leave" in {"view_attendance_self"} == False
  ↓
raise PermissionError
```

### Output

Ở domain:

```python
PermissionError
```

Ở presentation layer nên map thành:

```http
HTTP 403 Forbidden
```

---

## 8. Ví dụ cụ thể: admin gọi permission bất kỳ

### Input

```python
actor = User(
    id=1,
    role_name="admin",
    permissions=set(),
    is_active=True,
    ...
)
```

Use case gọi:

```python
rbac.has_permission(actor, "any_future_permission")
```

### Đi qua hàm

```text
RBACService.has_permission(actor, "any_future_permission")
  ↓
actor.is_active == True
  ↓
actor.role_name in {"admin"} == True
  ↓
return True
```

### Output

```python
True
```

Lưu ý: admin bypass permission code, nhưng admin bị khóa tài khoản vẫn bị từ chối vì `is_active` được kiểm tra trước.

---

## 9. Vì sao gọi là kiểm tra quyền trên RAM?

Permission vẫn được lưu ở DB. Nhưng DB chỉ được dùng khi load user.

Sau khi repository trả về `User`, dữ liệu permission đã ở dạng Python set:

```python
actor.permissions = {"approve_leave", "view_attendance_dept"}
```

Khi kiểm tra:

```python
"approve_leave" in actor.permissions
```

Đây là kiểm tra trong RAM, không query DB thêm.

So sánh:

| Cách | Khi check permission | DB query thêm? |
|---|---|---|
| Query DB mỗi lần | JOIN `users → roles → role_permissions → permissions` mỗi lần check | Có |
| Cách hiện tại | Load permissions một lần vào `User.permissions`, sau đó dùng set lookup | Không |

---

## 10. Thêm use case mới thì dùng RBAC thế nào?

Ví dụ thêm `AssignTaskUseCase`.

File dự kiến:

```text
app/application/use_cases/task/assign_task_use_case.py
```

Flow nên viết:

```python
class AssignTaskUseCase:
    def __init__(self, task_repo, user_repo, dept_repo, rbac, tree):
        self.task_repo = task_repo
        self.user_repo = user_repo
        self.dept_repo = dept_repo
        self.rbac = rbac
        self.tree = tree

    async def execute(self, actor: User, task_id: int, assignee_id: int):
        self.rbac.require_permission(actor, "assign_task")

        assignee = await self.user_repo.find_by_id(assignee_id)

        if actor.role_name == "manager":
            all_depts = await self.dept_repo.list_all()
            is_in_scope = self.tree.is_ancestor_of(
                actor.department_id,
                assignee.department_id,
                all_depts,
            )
            if not is_in_scope:
                raise PermissionError("Manager can only assign within managed scope")

        return await self.task_repo.assign(task_id, assignee_id)
```

Nguyên tắc:

```text
Permission đơn giản → RBACService.require_permission()
Scope phòng ban/cấp dưới → DepartmentTreeService
Business flow cụ thể → UseCase
DB read/write → Repository
```

---

## 11. Những phần chưa hoàn thiện trong code hiện tại

Các phần sau chưa có hoặc chưa hoàn chỉnh, nên khi đọc luồng cần phân biệt với phần đã implement:

| Phần | Trạng thái |
|---|---|
| API routes `app/presentation/api/v1/*.py` | Chưa có route nghiệp vụ; `app/main.py` hiện chỉ có `/health`. |
| Auth dependency `get_current_user()` | Chưa có. |
| JWT service | Chưa có. |
| Create user use case | Chưa có. |
| Resolve `role_name → role_id` khi create user | Chưa hoàn thiện trong `SQLAlchemyUserRepository.create()`. |
| `RoleRepository` / `PermissionRepository` | Chưa có, nên chưa có nơi chuyên trách lookup/quản trị role-permission ở tầng Domain/Application. |
| Seed role/permission demo | Chưa thấy trong source hiện tại. |

Phần đã có và chạy được:

| Phần | File |
|---|---|
| Domain RBAC logic | `app/domain/services/rbac_service.py` |
| Domain user chứa permission passport | `app/domain/entities/user.py` |
| ORM Role/Permission mapping | `app/infrastructure/database/models/*.py` |
| User repository eager-load permissions | `app/infrastructure/database/repositoties/sqlalchemy_user_repo.py` |
| Unit tests RBAC | `tests/unit/domain/test_rbac_service.py` |

Các caveat kỹ thuật cần nhớ:

| Caveat | Ý nghĩa |
|---|---|
| `app/infrastructure/database/repositoties/` bị typo | Tên đúng nên là `repositories`, nhưng hiện code đang dùng path typo này. Nếu đổi, cần đổi import toàn bộ. |
| `RBACService.require_permission()` raise built-in `PermissionError` | Trong `app/domain/exceptions.py` có `PermissionDenied`, nhưng RBACService hiện chưa dùng exception domain này. Presentation layer sau này cần map lỗi nhất quán. |
| `RBACService.get_task_scope()` còn hardcode role name | Hàm này dùng `admin`/`bod`/`manager`, không hoàn toàn dựa trên permission code. Nếu muốn DB-driven triệt để, nên cân nhắc permission riêng cho task scope. |
| `SQLAlchemyUserRepository.create()` chưa set `role_id` | Comment trong code đã ghi rõ phải lookup trước hoặc resolve từ `role_name`. Đây là blocker cho create-user flow hoàn chỉnh. |

---

## 12. Checklist khi người mới đọc code

Nếu bạn muốn hiểu RBAC trong dự án, nên đọc theo thứ tự này:

1. `docs/erd.md` — xem bảng `roles`, `permissions`, `role_permissions`, `users`.
2. `app/domain/entities/user.py` — xem `User.permissions` và `role_name`.
3. `app/infrastructure/database/models/user_model.py` — xem `users.role_id` và relationship `role`.
4. `app/infrastructure/database/models/role_model.py` — xem relationship `permissions`.
5. `app/infrastructure/database/repositoties/sqlalchemy_user_repo.py` — xem `_base_stmt()` và `_to_entity()`.
6. `app/domain/services/rbac_service.py` — xem `has_permission()` và các scope helpers.
7. `tests/unit/domain/test_rbac_service.py` — xem ví dụ executable cho admin, manager, employee.

---

## 13. Tóm tắt một dòng

RBAC của dự án dùng DB làm nguồn sự thật cho `Role ↔ Permission`, repository load quyền vào `User.permissions`, và `RBACService` kiểm tra permission trên RAM để use case quyết định cho phép tiếp tục hay trả lỗi 403.
