# Note nhanh: SQLAlchemy + Alembic

## 1) Hai công cụ này là gì

### SQLAlchemy
- Là thư viện làm việc với database trong Python.
- Cho phép định nghĩa bảng bằng class Python (ORM models).
- Dùng trong runtime của app để query, insert, update, delete dữ liệu.
- Trong dự án này dùng SQLAlchemy 2.0 async với asyncpg.

### Alembic
- Là công cụ migration cho SQLAlchemy.
- Dùng để quản lý lịch sử thay đổi schema database theo version.
- Sinh file migration khi schema thay đổi.
- Chạy upgrade hoặc downgrade để áp hoặc lùi schema.

### Dùng cùng nhau như thế nào
- SQLAlchemy định nghĩa schema và thao tác dữ liệu.
- Alembic đọc metadata từ SQLAlchemy để tạo migration.
- SQLAlchemy lo phần runtime.
- Alembic lo phần thay đổi cấu trúc database theo thời gian.

## 2) Các file quan trọng trong repo này

- app/infrastructure/database/base.py
  - Chứa Base và metadata naming convention.
  - Tất cả ORM model kế thừa từ Base.

- app/infrastructure/database/session.py
  - Tạo async engine và AsyncSessionLocal.
  - Runtime dùng session từ đây để truy cập DB.

- alembic/env.py
  - Cấu hình Alembic chạy async migration.
  - target_metadata lấy từ Base.metadata.
  - Có import app.infrastructure.database.models để Alembic nhìn thấy toàn bộ model.

- alembic.ini
  - Cấu hình Alembic cơ bản.
  - sqlalchemy.url để trống, URL thực tế lấy từ settings trong env.py.

- docs/erd.md
  - Là đầu vào thiết kế dữ liệu trước khi viết ORM model.

## 3) Quy trình bắt đầu xây dựng database

Bước 1: Chốt ERD
- Chốt bảng, cột, quan hệ, khóa chính, khóa ngoại, unique, index.

Bước 2: Viết ORM models theo ERD
- Mỗi bảng tương ứng một model.
- Model kế thừa từ Base trong base.py.

Bước 3: Đảm bảo Alembic load đủ model
- Xác nhận module models được import trong alembic/env.py.
- Nếu Alembic không thấy model, autogenerate sẽ ra migration rỗng.

Bước 4: Tạo migration
- Chạy lệnh:
  alembic revision --autogenerate -m "init_all_tables"

Bước 5: Áp migration vào DB
- Chạy lệnh:
  alembic upgrade head

Bước 6: Kiểm tra database
- Kiểm tra bảng đã được tạo.
- Chạy health check của app để xác nhận kết nối DB.

## 4) Ví dụ trực quan: thêm một bảng mới

Ví dụ muốn thêm bảng projects:

1. Cập nhật ERD: thêm entity projects.
2. Tạo model Project trong app/infrastructure/database/models.
3. Bảo đảm models package import model Project.
4. Chạy autogenerate:
   alembic revision --autogenerate -m "add_projects_table"
5. Review file migration vừa sinh.
6. Chạy:
   alembic upgrade head
7. Dùng AsyncSessionLocal trong session.py để query bảng projects trong API.

## 5) Checklist trước khi chạy migration

- Đã cập nhật ERD cho thay đổi mới.
- ORM model đã khai báo đúng kiểu dữ liệu, FK, unique, index.
- Model mới đã được import để Base.metadata nhìn thấy.
- DATABASE_URL đúng môi trường chạy.
- Đã review migration file trước khi upgrade.

## 6) Ghi nhớ nhanh

- SQLAlchemy = định nghĩa model + thao tác dữ liệu khi app chạy.
- Alembic = quản lý version schema qua migration.
- Không cần viết toàn bộ SQL thủ công, nhưng vẫn cần hiểu SQL để thiết kế đúng và review migration an toàn.
