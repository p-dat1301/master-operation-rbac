# Hướng Dẫn Test API với Postman — Master Operation RBAC

## Tổng quan

Tài liệu này hướng dẫn bạn sử dụng **Postman** để test toàn bộ API của hệ thống Master Operation RBAC. Bao gồm:

- Import Collection và Environment
- Chạy test từng endpoint
- Kiểm tra các trường hợp bình thường (happy path) và lỗi (error cases)
- Sử dụng Postman Runner để chạy tự động
- Giải thích các kịch bản RBAC (Role-Based Access Control)

---

## Chuẩn bị

### 1. Khởi động API Server

Trước khi test, đảm bảo server đang chạy:

```bash
# Trong thư mục dự án
uvicorn app.main:app --reload --port 8000
```

Hoặc nếu dùng Docker:

```bash
docker-compose up
```

Kiểm tra health endpoint:
```bash
curl http://localhost:8000/health
```

### 2. Cài đặt Postman

- Tải và cài đặt từ [https://www.postman.com/downloads/](https://www.postman.com/downloads/)
- Đăng nhập tài khoản (không bắt buộc nhưng khuyến khích để sync)

---

## Import Collection

### Bước 1: Import Collection JSON

1. Mở Postman
2. Click **Import** (góc trái trên)
3. Chọn file: `scripts/postman-collection.json`
4. Click **Import**

Bạn sẽ thấy Collection tên **"Master Operation RBAC - Full API Test"** xuất hiện trong sidebar.

### Bước 2: Tạo Environment

1. Click **Environments** (bên phải sidebar) → **Create Environment**
2. Đặt tên: `Master Operation Local`
3. Thêm các biến sau:

| Variable | Initial Value | Current Value | Mô tả |
|----------|--------------|---------------|-------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` | URL của API server |
| `admin_email` | `admin@company.vn` | `admin@company.vn` | Email admin |
| `admin_password` | `Admin@123` | `Admin@123` | Password admin |
| `manager_email` | `manager@company.vn` | `manager@company.vn` | Email manager |
| `manager_password` | `Manager@123` | `Manager@123` | Password manager |
| `employee_email` | `employee@company.vn` | `employee@company.vn` | Email employee |
| `employee_password` | `Employee@123` | `Employee@123` | Password employee |
| `user_id` | `3` | `3` | ID user test (employee) |
| `department_id` | `1` | `1` | ID phòng ban |
| `role_id` | `2` | `2` | ID role test |
| `permission_id` | `1` | `1` | ID permission test |
| `notification_id` | `1` | `1` | ID notification test |
| `year` | `2026` | `2026` | Năm test leave balance |
| `start_date` | `2026-06-01` | `2026-06-01` | Ngày bắt đầu heatmap |
| `end_date` | `2026-06-30` | `2026-06-30` | Ngày kết thúc heatmap |
| `admin_token` | *(để trống)* | *(để trống)* | Tự động fill sau login |
| `manager_token` | *(để trống)* | *(để trống)* | Tự động fill sau login |
| `employee_token` | *(để trống)* | *(để trống)* | Tự động fill sau login |
| `today` | *(để trống)* | *(để trống)* | Tự động set |
| `tomorrow` | *(để trống)* | *(để trống)* | Tự động set |
| `day_after` | *(để trống)* | *(để trống)* | Tự động set |
| `now` | *(để trống)* | *(để trống)* | Tự động set |

4. Click **Save**

5. Chọn Environment: Ở góc trên bên phải Postman, chọn `Master Operation Local` từ dropdown

---

## Cấu trúc Collection

Collection được tổ chức thành 10 folder, mỗi folder tương ứng một module:

| Folder | Module | Số request | Mô tả |
|--------|--------|-----------|-------|
| 01 — Auth | Authentication | 11 | Login, Get Me, token tests |
| 02 — Users | User Management | 10 | CRUD users, activate, password |
| 03 — Leaves | Leave Requests | 7 | Create, review, cancel leaves |
| 04 — Tasks | Task Management | 10 | CRUD tasks, assign, complete |
| 05 — Attendance | Attendance | 3 | Checkin, checkout, heatmap |
| 06 — Roles & Permissions | RBAC | 8 | Role CRUD, permissions |
| 07 — Notifications | Notifications | 3 | List, mark read |
| 08 — Leave Balances | Leave Balances | 3 | Get/update balances |
| 09 — Audit Logs | Audit Logs | 2 | List logs (admin only) |
| 10 — Health | Health Check | 1 | Server health |

**Tổng cộng: 58 requests**

---

## Chạy Test Cơ Bản

### Chạy từng request

1. Mở folder **01 — Auth**
2. Click vào request đầu tiên: **Login — Admin**
3. Click nút **Send** (màu xanh)
4. Kiểm tra tab **Test Results** bên dưới — bạn sẽ thấy:
   - ✅ Status 200
   - ✅ Has access_token
   - ✅ Token type is bearer

5. Token đã tự động lưu vào biến `admin_token` trong Environment

### Chạy toàn bộ folder với Collection Runner

1. Click vào folder (vd: **01 — Auth**)
2. Click nút **Run** (màu xanh bên phải, có icon play)
3. Collection Runner sẽ mở ra
4. Chọn Environment: `Master Operation Local`
5. Click **Run 01 — Auth**
6. Xem kết quả: tổng hợp pass/fail cho từng request

### Chạy toàn bộ Collection

1. Click vào Collection root: **Master Operation RBAC - Full API Test**
2. Click **Run**
3. Chọn Environment
4. Click **Run Master Operation RBAC...**

**Lưu ý quan trọng:** Chạy folder **01 — Auth** trước để populate các token. Các folder sau đó dùng token để xác thực.

---

## Các Trường Hợp Test

### A. Happy Path Tests

Đây là các trường hợp thành công bình thường:

#### 1. Auth Flow
- **Login — Admin** → 200, trả về access_token
- **Get Me — Admin** → 200, email = `admin@company.vn`, role = `admin`
- **Get Me — Manager** → 200, role = `manager`
- **Get Me — Employee** → 200, role = `employee`

#### 2. User Management (Admin)
- **List Users** → 200, trả về mảng users
- **Create User** → 200/201, user mới được tạo
- **Get User** → 200, user details
- **Update User** → 200, full_name cập nhật
- **Change Password** → 200
- **Reset Password** → 200
- **Deactivate/Activate** → 200, is_active thay đổi
- **Delete User** → 200

#### 3. Leave Requests
- **Create Leave — Employee** → 200, status = `pending`
- **List Leaves** → 200, mảng leave requests
- **Review Leave — Manager Same Dept** → 200, status = `approved`
- **Update Leave** → 200
- **Cancel Leave** → 200

#### 4. Tasks
- **Create Task — Admin** → 200/201
- **List Tasks** → 200, có filter params
- **Get Task** → 200
- **Assign Task** → 200
- **Start Task** → 200
- **Complete Task** → 200
- **Cancel Task** → 200
- **Update Task** → 200
- **Delete Task** → 200

#### 5. Attendance
- **Checkin — Employee** → 200, status = `checked_in`
- **Checkout — Employee** → 200
- **Heatmap — Manager** → 200, mảng attendance records

#### 6. Roles & Permissions
- **List Roles** → 200
- **Create Role** → 200/201
- **Update Role** → 200
- **List Role Permissions** → 200
- **Add Permission to Role** → 200
- **Remove Permission from Role** → 200
- **Delete Role** → 200
- **List Permissions** → 200

#### 7. Notifications
- **List Notifications** → 200
- **Mark Notification Read** → 200
- **Mark All Read** → 200, có `marked_count`

#### 8. Leave Balances
- **Get My Leave Balance** → 200, có `user_id`, `total_days`, `used_days`
- **Get User Leave Balance** → 200
- **Update User Leave Balance** → 200

#### 9. Health
- **Health Check** → 200, không cần auth

---

### B. Error & RBAC Tests

Đây là các trường hợp kiểm tra bảo mật và validation:

#### 1. Authentication Errors

| Request | Expected | Test kiểm tra |
|---------|----------|---------------|
| Login — Wrong Password | 403 | `Permission denied` |
| Login — Nonexistent User | 404 | `User not found` |
| Login — Missing Password | 422 | Validation error |
| Get Me — No Token | 401 | Unauthorized |
| Get Me — Invalid Token | 401 | Invalid token format |

#### 2. RBAC — Employee bị chặn

| Request | Expected | Lý do |
|---------|----------|-------|
| List Users — Employee | 403 | Employee không có quyền list users |
| Create Task — Employee | 403 | Employee không có quyền tạo task |
| List Audit Logs — Employee | 403 (hoặc 200 nếu placeholder) | Admin only |

#### 3. RBAC — Manager cross-department

| Request | Expected | Lý do |
|---------|----------|-------|
| Review Leave — Manager Other Dept | 403 | Manager chỉ review cùng phòng |

#### 4. Resource Errors

| Request | Expected | Test |
|---------|----------|------|
| Get Task — Not Found | 404 | Task ID không tồn tại |
| Get User — Not Found | 404 | User ID không tồn tại |

---

## Chi tiết kỹ thuật

### Pre-request Script

Collection có script chạy trước mỗi request để tự động tính ngày tháng:

```javascript
// Tự động set ngày hôm nay, ngày mai, ngày kia
const now = new Date();
const today = now.toISOString().split('T')[0];
const tomorrow = new Date(now); tomorrow.setDate(tomorrow.getDate()+1);
const dayAfter = new Date(now); dayAfter.setDate(dayAfter.getDate()+2);
pm.environment.set('today', today);
pm.environment.set('tomorrow', tomorrow.toISOString().split('T')[0]);
pm.environment.set('day_after', dayAfter.toISOString().split('T')[0]);
pm.environment.set('now', now.toISOString());
```

### Test Script Pattern

Mỗi request có test script kiểm tra response. Ví dụ:

```javascript
// Status check
pm.test('Status 200', () => pm.response.to.have.status(200));

// Response structure check
pm.test('Has access_token', () => {
  const json = pm.response.json();
  pm.expect(json).to.have.property('access_token');
  pm.expect(json.access_token).to.be.a('string');
});

// Value check
pm.test('Token type is bearer', () => {
  pm.expect(pm.response.json().token_type).to.eql('bearer');
});

// Save to environment
pm.environment.set('admin_token', pm.response.json().access_token);
```

### Dynamic Variables

Postman hỗ trợ các biến động:

- `{{$randomInt}}` — Random integer (dùng trong create user/task/role để tránh duplicate)
- `{{base_url}}` — Environment variable
- `{{admin_token}}` — Token lưu sau login

---

## Kịch bản RBAC đầy đủ (S1-S9)

Dựa trên test matrix trong `tests/integration/test_rbac_scenarios.py`:

### S1 — Employee GET /users/ phòng khác → 403
**Request:** `List Users — Employee`  
**Expected:** 403 Permission denied  
**Thực tế:** Employee không có quyền xem danh sách users

### S2 — Manager PUT /leaves/{id}/review cùng phòng → 200
**Request:** `Review Leave — Manager Same Dept`  
**Flow:** Employee tạo leave → Manager (cùng dept) approve → 200, status = approved

### S3 — Manager PUT /leaves/{id}/review phòng khác → 403
**Request:** `Review Leave — Manager Other Dept`  
**Flow:** Admin (dept=None) tạo leave → Manager (dept=1) approve → 403

### S4 — Employee POST /tasks/ assign người khác → 403
**Request:** `Create Task — Employee`  
**Expected:** 403

### S5 — Manager PUT /tasks/{id}/assign cùng phòng → 200
**Request:** `Assign Task — Manager`  
**Expected:** 200 (nếu implement đúng)

### S6 — Employee POST /attendance/checkin → 200
**Request:** `Checkin — Employee`  
**Expected:** 200, status = checked_in

### S7 — Employee GET /attendance/heatmap → chỉ data mình
**Request:** Heatmap với employee_token  
**Expected:** Chỉ trả về record của employee

### S8 — Manager GET /attendance/heatmap → toàn phòng
**Request:** `Heatmap — Manager`  
**Expected:** Trả về toàn bộ phòng ban

### S9 — Employee GET /audit-logs/ → 403
**Request:** `List Audit Logs — Employee`  
**Expected:** 403 (hoặc 200 nếu endpoint còn là placeholder)

---

## Tips & Tricks

### 1. Chạy nhanh với Newman (CLI)

Nếu bạn thích command line:

```bash
# Cài newman
npm install -g newman

# Chạy collection
newman run scripts/postman-collection.json \
  -e scripts/postman-environment.json \
  --reporters cli,json \
  --reporter-json-export scripts/postman-report.json
```

### 2. Tạo Environment file để import

Bạn có thể tạo file `scripts/postman-environment.json`:

```json
{
  "name": "Master Operation Local",
  "values": [
    { "key": "base_url", "value": "http://localhost:8000", "enabled": true },
    { "key": "admin_email", "value": "admin@company.vn", "enabled": true },
    { "key": "admin_password", "value": "Admin@123", "enabled": true },
    { "key": "manager_email", "value": "manager@company.vn", "enabled": true },
    { "key": "manager_password", "value": "Manager@123", "enabled": true },
    { "key": "employee_email", "value": "employee@company.vn", "enabled": true },
    { "key": "employee_password", "value": "Employee@123", "enabled": true },
    { "key": "user_id", "value": "3", "enabled": true },
    { "key": "department_id", "value": "1", "enabled": true },
    { "key": "role_id", "value": "2", "enabled": true },
    { "key": "permission_id", "value": "1", "enabled": true },
    { "key": "notification_id", "value": "1", "enabled": true },
    { "key": "year", "value": "2026", "enabled": true },
    { "key": "start_date", "value": "2026-06-01", "enabled": true },
    { "key": "end_date", "value": "2026-06-30", "enabled": true }
  ]
}
```

Import file này vào Postman thay vì tạo thủ công.

### 3. Debug failing tests

Khi test fail:
1. Mở request bị fail
2. Click tab **Console** (góc dưới trái) hoặc `View → Show Postman Console`
3. Kiểm tra request/response chi tiết
4. So sánh expected vs actual status code

### 4. Thêm request mới

Nếu cần test endpoint khác:
1. Duplicate request tương tự trong cùng folder
2. Sửa URL, method, body
3. Viết test script phù hợp
4. Chạy để xác nhận

### 5. Data-driven testing

Để test với nhiều bộ dữ liệu:
1. Tạo file CSV/JSON với các column: `email`, `password`, `expected_status`
2. Trong Collection Runner, chọn **Data** → chọn file CSV
3. Sử dụng `{{email}}` trong request body
4. Chạy runner — nó sẽ lặp qua từng row

---

## Troubleshooting

| Vấn đề | Nguyên nhân | Cách fix |
|--------|-------------|----------|
| 401 Unauthorized | Chưa login hoặc token hết hạn | Chạy folder Auth trước |
| 403 Permission denied | User không có quyền | Kiểm tra role của user |
| 404 Not Found | Resource không tồn tại | Kiểm tra ID, đảm bảo seed data đúng |
| 422 Validation Error | Request body thiếu/sai field | Kiểm tra schema, required fields |
| Connection refused | Server chưa chạy | Khởi động uvicorn hoặc docker |
| Tests không chạy | Chưa chọn Environment | Chọn `Master Operation Local` từ dropdown |

---

## Tài liệu liên quan

- `scripts/postman-collection.json` — Collection chính
- `scripts/api-tests.json` — JSON test runner (không cần Postman)
- `scripts/run_api_tests.py` — Python script chạy API tests
- `tests/integration/` — Integration tests (pytest)
- `app/presentation/api/v1/` — API route handlers
- `app/presentation/schemas/` — Request/response schemas

---

## Lệnh chạy nhanh (Python Alternative)

Nếu không muốn dùng Postman, có thể chạy test bằng Python:

```bash
# Chạy test với script có sẵn
python scripts/run_api_tests.py

# Chạy integration tests
pytest tests/integration/ -v

# Chạy riêng test auth
pytest tests/integration/test_auth.py -v

# Chạy RBAC scenarios
pytest tests/integration/test_rbac_scenarios.py -v
```

---

*Last updated: 2026-06-10*
