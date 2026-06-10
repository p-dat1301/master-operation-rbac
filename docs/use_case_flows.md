# Luồng Xử Lý Của Các Use Case

Tài liệu này mô tả đường đi từ API đến DB cho từng use case trong codebase. Mỗi mục nêu rõ:
- Endpoint hoặc nơi gọi use case
- Đầu vào
- Đầu ra
- Các bước xử lý chính
- Repository/DB được chạm tới
- Lỗi nghiệp vụ thường gặp

## 1. Auth

### 1.1 LoginUseCase
- Nơi dùng: API đăng nhập ở tầng presentation.
- Đầu vào: `LoginInput` gồm `email`, `password`.
- Đầu ra: `LoginOutput` gồm `access_token`, `token_type`, `expires_in`.
- Luồng xử lý:
  1. Tìm user theo email bằng `user_repo.find_by_email`.
  2. Kiểm tra user có tồn tại không.
  3. Kiểm tra `is_active`.
  4. Kiểm tra user có `hashed_password` hay không.
  5. So khớp password bằng `password_service.verify`.
  6. Tạo JWT bằng `token_service.create_access_token`.
  7. Trả token cho client.
- DB chạm tới:
  - `UserRepository.find_by_email`.
- Lỗi có thể gặp:
  - `ResourceNotFound` nếu không có user hoặc không có credentials.
  - `PermissionDenied` nếu user bị khóa hoặc password sai.

### 1.2 GetMeUseCase
- Nơi dùng: API lấy thông tin user hiện tại.
- Đầu vào: `user_id` lấy từ token đã decode.
- Đầu ra: `UserOutput`.
- Luồng xử lý:
  1. Tìm user theo id bằng `user_repo.find_by_id`.
  2. Nếu không có user thì báo lỗi.
  3. Map entity sang DTO `UserOutput`.
- DB chạm tới:
  - `UserRepository.find_by_id`.
- Lỗi có thể gặp:
  - `ResourceNotFound`.

## 2. User

### 2.1 CreateUserUseCase
- Nơi dùng: API tạo user.
- Đầu vào: `actor: User`, `UserCreateInput` gồm:
  - `employee_code`
  - `email`
  - `full_name`
  - `password`
  - `role_name`
  - `phone`
  - `job_title`
  - `contact_type`
  - `department_id`
  - `manager_id`
  - `hire_date`
  - `is_active`
- Đầu ra: `UserOutput`.
- Luồng xử lý:
  1. Kiểm tra quyền `manage_org` bằng `rbac_service.require_permission`.
  2. Tìm role theo tên bằng `role_repo.find_by_name`.
  3. Kiểm tra email đã tồn tại bằng `user_repo.find_by_email`.
  4. Hash password bằng `password_service.hash`.
  5. Tạo domain `User` với dữ liệu đã validate.
  6. Gọi `user_repo.create(user_entity, hashed_password=...)`.
  7. Chuyển kết quả sang `UserOutput`.
- DB chạm tới:
  - `RoleRepository.find_by_name`.
  - `UserRepository.find_by_email`.
  - `UserRepository.create`.
- Lỗi có thể gặp:
  - `PermissionDenied` nếu actor không có quyền.
  - `ResourceNotFound` nếu role không tồn tại.
  - `BusinessRuleViolation` nếu email bị trùng.

### 2.2 ListUsersUseCase
- Nơi dùng: API lấy danh sách user.
- Đầu vào: `actor: User`.
- Đầu ra: `list[UserOutput]`.
- Luồng xử lý:
  1. Kiểm tra quyền `manage_org`.
  2. Gọi `user_repo.find_all`.
  3. Map từng entity sang `UserOutput`.
- DB chạm tới:
  - `UserRepository.find_all`.
- Lỗi có thể gặp:
  - `PermissionDenied`.

## 3. Task

### 3.1 CreateTaskUseCase
- Nơi dùng: API tạo task.
- Đầu vào: `actor: User`, `TaskCreateInput` gồm:
  - `task_code`
  - `title`
  - `description`
  - `assignee_id`
  - `department_id`
  - `priority`
  - `start_date`
  - `due_date`
  - `estimated_hours`
- Đầu ra: `TaskOutput`.
- Luồng xử lý:
  1. Kiểm tra quyền `create_task`.
  2. Tạo domain `Task` với `status="todo"` và `assigner_id=actor.id`.
  3. Gọi `task_repo.create`.
  4. Map entity sang `TaskOutput`.
- DB chạm tới:
  - `TaskRepository.create`.
- Lỗi có thể gặp:
  - `PermissionDenied`.

### 3.2 AssignTaskUseCase
- Nơi dùng: API gán task.
- Đầu vào: `actor: User`, `AssignTaskInput` gồm `task_id`, `assignee_id`.
- Đầu ra: `TaskOutput`.
- Luồng xử lý:
  1. Kiểm tra quyền `assign_task`.
  2. Tìm task theo id bằng `task_repo.find_by_id`.
  3. Nếu không có task thì báo lỗi.
  4. Gọi `task_repo.assign_task(...)` để cập nhật người được giao.
  5. Trả `TaskOutput`.
- DB chạm tới:
  - `TaskRepository.find_by_id`.
  - `TaskRepository.assign_task`.
- Lỗi có thể gặp:
  - `PermissionDenied`.
  - `ResourceNotFound`.

### 3.3 CompleteTaskUseCase
- Nơi dùng: API hoàn thành task.
- Đầu vào: `actor: User`, `CompleteTaskInput` gồm `task_id`.
- Đầu ra: `TaskOutput`.
- Luồng xử lý:
  1. Tìm task theo id.
  2. Kiểm tra quyền theo 3 điều kiện:
     - actor là người giao task
     - actor có permission `complete_task`
     - actor có role `admin` hoặc `bod`
  3. Nếu task đã `done` hoặc `cancelled` thì báo lỗi.
  4. Tạo entity mới với `status="done"`.
  5. Gọi `task_repo.update`.
  6. Trả `TaskOutput`.
- DB chạm tới:
  - `TaskRepository.find_by_id`.
  - `TaskRepository.update`.
- Lỗi có thể gặp:
  - `ResourceNotFound`.
  - `PermissionDenied`.
  - `BusinessRuleViolation`.

### 3.4 ListTasksUseCase
- Nơi dùng: API liệt kê task.
- Đầu vào: `actor: User`.
- Đầu ra: `list[TaskOutput]`.
- Luồng xử lý:
  1. Lấy scope bằng `rbac_service.get_task_scope(actor)`.
  2. Nếu scope là `all` thì gọi `task_repo.list_all`.
  3. Nếu scope là `department` thì gọi `task_repo.list_by_department(actor.department_id)`.
  4. Còn lại thì gọi `task_repo.list_by_assignee(actor.id)`.
  5. Map danh sách entity sang `TaskOutput`.
- DB chạm tới:
  - `TaskRepository.list_all`.
  - `TaskRepository.list_by_department`.
  - `TaskRepository.list_by_assignee`.
- Lỗi có thể gặp:
  - Chủ yếu phụ thuộc scope, use case này không ném lỗi quyền trực tiếp trong code hiện tại.

## 4. Attendance

### 4.1 CheckinUseCase
- Nơi dùng: API chấm công check-in.
- Đầu vào: `CheckinInput` gồm:
  - `user_id`
  - `check_in`
  - `ip_address`
  - `note`
- Đầu ra: `AttendanceOutput`.
- Luồng xử lý:
  1. Lấy ngày từ `check_in`.
  2. Kiểm tra đã check-in trong ngày chưa bằng `attendance_repo.find_by_user_date`.
  3. Nếu đã có bản ghi thì báo lỗi.
  4. Lấy user bằng `user_repo.find_by_id` để biết `department_id`.
  5. Tạo entity `Attendance` với `status="checked_in"`.
  6. Gọi `attendance_repo.create`.
  7. Trả `AttendanceOutput`.
- DB chạm tới:
  - `AttendanceRepository.find_by_user_date`.
  - `UserRepository.find_by_id`.
  - `AttendanceRepository.create`.
- Lỗi có thể gặp:
  - `BusinessRuleViolation` nếu đã check-in trong ngày.

### 4.2 GetHeatmapUseCase
- Nơi dùng: API lấy heatmap chấm công.
- Đầu vào: `actor: User`, `HeatmapFilterInput` gồm:
  - `start_date`
  - `end_date`
  - `user_id`
  - `department_id`
- Đầu ra: `list[AttendanceOutput]`.
- Luồng xử lý:
  1. Lấy scope bằng `rbac_service.get_attendance_scope(actor)`.
  2. Nếu scope là `all` thì lấy toàn bộ bản ghi theo khoảng ngày.
  3. Nếu scope là `department` thì lấy toàn bộ department con bằng `dept_tree_service.get_dept_and_descendants`, rồi query theo danh sách department id.
  4. Nếu scope hẹp hơn thì chỉ được xem chính mình; nếu filter `user_id` khác actor.id thì báo lỗi.
  5. Query attendance theo user.
  6. Map sang `AttendanceOutput`.
- DB chạm tới:
  - `AttendanceRepository.list_by_date_range`.
  - `DepartmentRepository.find_all`.
  - `AttendanceRepository.list_by_departments`.
  - `AttendanceRepository.list_by_user`.
- Lỗi có thể gặp:
  - `PermissionDenied` nếu cố xem attendance của user khác ở scope cá nhân.

## 5. Leave Request

### 5.1 CreateLeaveRequestUseCase
- Nơi dùng: API tạo đơn xin nghỉ.
- Đầu vào: `actor: User`, `LeaveRequestCreateInput` gồm:
  - `leave_type`
  - `start_date`
  - `end_date`
  - `reason`
- Đầu ra: `LeaveRequestOutput`.
- Luồng xử lý:
  1. Tạo domain `LeaveRequest` với `requester_id=actor.id`.
  2. Gán `status="pending"`.
  3. Gán `department_id=actor.department_id`.
  4. Gọi `leave_repo.create`.
  5. Trả `LeaveRequestOutput`.
- DB chạm tới:
  - `LeaveRequestRepository.create`.
- Lỗi có thể gặp:
  - Trong code hiện tại không có check quyền riêng.

### 5.2 ListLeaveRequestsUseCase
- Nơi dùng: API liệt kê đơn xin nghỉ.
- Đầu vào: `actor: User`.
- Đầu ra: `list[LeaveRequestOutput]`.
- Luồng xử lý:
  1. Lấy scope bằng `rbac_service.get_leave_request_scope(actor)`.
  2. Nếu scope là `all` thì gọi `leave_repo.list_all`.
  3. Nếu scope là `department` thì lấy department con bằng `dept_tree_service` rồi query `leave_repo.list_by_departments`.
  4. Còn lại thì chỉ lấy đơn của chính actor bằng `leave_repo.list_by_requester`.
  5. Map sang `LeaveRequestOutput`.
- DB chạm tới:
  - `LeaveRequestRepository.list_all`.
  - `DepartmentRepository.find_all`.
  - `LeaveRequestRepository.list_by_departments`.
  - `LeaveRequestRepository.list_by_requester`.

### 5.3 ReviewLeaveRequestUseCase
- Nơi dùng: API duyệt hoặc từ chối đơn nghỉ.
- Đầu vào: `actor: User`, `ReviewLeaveRequestInput` gồm:
  - `leave_request_id`
  - `action` (`approve` hoặc `reject`)
  - `rejected_reason`
- Đầu ra: `LeaveRequestOutput`.
- Luồng xử lý:
  1. Tìm đơn nghỉ bằng `leave_repo.find_by_id`.
  2. Nếu không tồn tại thì báo lỗi.
  3. Lấy toàn bộ department để xác định quan hệ ancestor/descendant.
  4. Kiểm tra actor có quyền duyệt đơn trong scope đó bằng `rbac_service.can_approve_leave_for`.
  5. Tính `new_status` là `approved` hoặc `rejected`.
  6. Gọi `leave_repo.update_status` để cập nhật trạng thái.
  7. Gọi `notification_service.notify_user` để báo cho người xin nghỉ.
  8. Trả `LeaveRequestOutput`.
- DB chạm tới:
  - `LeaveRequestRepository.find_by_id`.
  - `DepartmentRepository.find_all`.
  - `LeaveRequestRepository.update_status`.
  - `NotificationService` có thể tạo notification tùy implementation.
- Lỗi có thể gặp:
  - `ResourceNotFound`.
  - `PermissionDenied`.

## 6. Notification

### 6.1 ListNotificationsUseCase
- Nơi dùng: API lấy danh sách thông báo.
- Đầu vào: `actor: User`.
- Đầu ra: `list[NotificationOutput]`.
- Luồng xử lý:
  1. Gọi `notification_repo.list_by_recipient(actor.id)`.
  2. Map từng record sang `NotificationOutput`.
- DB chạm tới:
  - `NotificationRepository.list_by_recipient`.

## 7. Audit Log

### 7.1 ListAuditLogsUseCase
- Nơi dùng: API xem audit log.
- Đầu vào: `actor: User`.
- Đầu ra: `list[AuditLogOutput]`.
- Luồng xử lý:
  1. Kiểm tra actor có permission `view_audit_logs` không.
  2. Nếu không có thì báo lỗi.
  3. Gọi `audit_log_repo.list_recent(limit=100)`.
  4. Map sang `AuditLogOutput`.
- DB chạm tới:
  - `AuditLogRepository.list_recent`.
- Lỗi có thể gặp:
  - `PermissionDenied`.

## 8. Cách đọc nhanh một use case

Khi muốn hiểu một use case bất kỳ, hãy đọc theo thứ tự này:
1. File use case trong `app/application/use_cases/...`
2. DTO input/output trong `app/application/dtos/...`
3. Route ở `app/presentation/api/v1/...`
4. Provider/DI ở `app/di/...` hoặc `app/container.py`
5. Repository concrete ở `app/infrastructure/database/repositories/...`
6. ORM model ở `app/infrastructure/database/models/...`
7. Session ở `app/infrastructure/database/session.py`

## 9. Ghi chú kiến trúc

- Presentation nhận request và validate schema.
- Application chứa business rule.
- Domain giữ entity, exception, service nghiệp vụ.
- Infrastructure làm việc với SQLAlchemy, JWT, bcrypt, notification.
- Use case không nên biết FastAPI hay SQLAlchemy trực tiếp, mà chỉ phụ thuộc vào interface/repository abstraction.
