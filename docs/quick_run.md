# Quick Run — Master Operation API

Hướng dẫn chạy nhanh backend bằng Docker, seed dữ liệu demo, mở Swagger và test các API chính.

## 1. Yêu cầu trước khi chạy

Cần có:

- Docker + Docker Compose
- Python virtualenv `.venv` đã cài dependencies nếu muốn chạy `make seed` / `make test` từ máy host
- File `.env` ở root project

Nếu chưa có `.env`, tạo từ mẫu:

```bash
cp .env.example .env
```

Với Docker Compose hiện tại, `.env` nên dùng DB host là service name `db`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/masterop
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## 2. Chạy Docker services

Chạy API + PostgreSQL + Redis:

```bash
make up
```

Lệnh này tương đương:

```bash
docker compose up --build -d
```

Các service chính:

| Service | URL / Port |
|---|---|
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

Kiểm tra container:

```bash
docker compose ps
```

Kiểm tra health API:

```bash
curl http://localhost:8000/health
```

Kết quả mong đợi:

```json
{"status":"ok","db":"connected"}
```

## 3. Chạy migration

Nếu database mới chưa có schema, chạy migration trong container API:

```bash
docker compose exec api alembic upgrade head
```

Hoặc nếu chạy từ máy host, cần dùng `DATABASE_URL` trỏ về `localhost`:

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/masterop"
.venv/bin/alembic upgrade head
```

## 4. Seed dữ liệu demo

Seed roles, permissions, departments và demo users:

```bash
make seed
```

`make seed` dùng DB local port `5432`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop
```

Nếu không muốn dùng `.venv` trên máy host, có thể seed trực tiếp trong container API:

```bash
docker compose exec api python -m app.infrastructure.database.seed
```

Tài khoản demo:

| Email | Password | Role |
|---|---|---|
| `admin@company.vn` | `Admin@123` | admin |
| `manager@company.vn` | `Manager@123` | manager |
| `employee@company.vn` | `Employee@123` | employee |

## 5. Mở Swagger và login

Mở:

```text
http://localhost:8000/docs
```

Tìm endpoint:

```text
POST /api/v1/auth/login
```

Body ví dụ:

```json
{
  "email": "employee@company.vn",
  "password": "Employee@123"
}
```

Response sẽ có `access_token`:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Trong Swagger, bấm **Authorize** rồi nhập:

```text
Bearer <access_token>
```

Sau đó các API cần đăng nhập sẽ dùng token này.

## 6. Test API cơ bản trên Swagger

### Kiểm tra user hiện tại

Endpoint:

```text
GET /api/v1/auth/me
```

Kết quả trả về user lấy từ JWT token.

### Check-in

Endpoint:

```text
POST /api/v1/attendance/checkin
```

Body tối thiểu:

```json
{
  "check_in": "2026-06-08T08:30:00"
}
```

Body đầy đủ hơn:

```json
{
  "check_in": "2026-06-08T08:30:00",
  "ip_address": "127.0.0.1",
  "note": "Test check-in from Swagger"
}
```

Không cần truyền `user_id`. Backend lấy user từ JWT qua `get_current_user()` rồi dùng `actor.id` để ghi attendance.

### Checkout

Endpoint:

```text
POST /api/v1/attendance/checkout
```

Không cần body. Backend tìm bản ghi check-in hôm nay của user hiện tại và cập nhật `check_out`, `total_minutes`, `status="checked_out"`.

### List tasks

Endpoint:

```text
GET /api/v1/tasks/
```

Có thể filter bằng query:

```text
status=todo
assignee_id=3
department_id=1
```

### Leave request

Tạo đơn nghỉ:

```text
POST /api/v1/leaves/
```

Ví dụ body:

```json
{
  "leave_type": "annual",
  "start_date": "2026-06-10",
  "end_date": "2026-06-12",
  "reason": "Family trip"
}
```

Xem balance cá nhân:

```text
GET /api/v1/leave-balances/me
```

### Roles / Permissions

Dùng admin token để test:

```text
GET /api/v1/roles/
GET /api/v1/permissions/
GET /api/v1/roles/{id}/permissions
POST /api/v1/roles/{role_id}/permissions/{permission_id}
DELETE /api/v1/roles/{role_id}/permissions/{permission_id}
```

## 7. Test bằng curl nhanh

Login:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"employee@company.vn","password":"Employee@123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

Get me:

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

Check-in:

```bash
curl -X POST http://localhost:8000/api/v1/attendance/checkin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"check_in\":\"$(date -Iseconds)\",\"note\":\"Quick run check-in\"}"
```

Checkout:

```bash
curl -X POST http://localhost:8000/api/v1/attendance/checkout \
  -H "Authorization: Bearer $TOKEN"
```

## 8. Chạy tests

Unit tests:

```bash
make test-unit
```

Integration tests:

```bash
make test-integration
```

Lưu ý hiện tại: TODO mới nhất ghi nhận unit tests còn fail ở phần leave use case sau refactor `leave_balance_repo`, và integration scenarios còn stale/skip. Xem thêm `docs/TODO.md` để biết trạng thái mới nhất.

## 9. Dừng services và giữ dữ liệu

Nếu chỉ muốn dừng container nhưng giữ DB volume:

```bash
docker compose stop
```

Hoặc xóa container nhưng giữ volume:

```bash
docker compose down
```

Không dùng nếu muốn giữ dữ liệu:

```bash
make down
```

Vì `make down` hiện chạy:

```bash
docker compose down -v
```

`-v` sẽ xóa Docker volume PostgreSQL, tức mất dữ liệu DB demo.

## 10. Các lỗi thường gặp

### `401 Unauthorized`

Chưa login, chưa bấm **Authorize**, hoặc token sai/hết hạn.

### `403 Permission denied`

User không có quyền. Dùng admin token để test API quản trị.

### `400 Already checked in today`

User đã check-in ngày hôm đó. Hãy checkout hoặc reset DB/test bằng ngày khác.

### `404 Attendance check-in not found for today`

Gọi checkout trước khi check-in hôm nay.

### DB không kết nối

Kiểm tra container DB:

```bash
docker compose ps
docker compose logs db
```

Kiểm tra `.env` khi chạy Docker phải dùng host `db`, còn chạy từ máy host phải dùng `localhost`.
