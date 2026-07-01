# Draft: Document CRUD RBAC

## Requirements (confirmed)
- Hoàn thiện CRUD cho module `document`
- Quyền `read` phân quyền theo CÁCH C: kết hợp department + role
  - User thường (employee): chỉ thấy document của phòng ban mình
  - Role cao (manager, admin/bod): thấy rộng hơn tùy role
  - Rule áp dụng cho list, detail, search

## Technical Decisions
- **Test strategy**: TDD chọn lọc — backend CRUD + RBAC use cases viết test TRƯỚC; frontend/UI tests-after hoặc Playwright tối thiểu
- **Authorization pattern**: router mỏng, auth ở dependency, authorization ở use case (canonical của repo)
- **RBAC read pattern**: dùng `evaluate_access` / `AccessPolicyMetadata` từ agentic pipeline + `RBACService` scope helper (all/department/self)
- **Department scope**: filter bằng `dept_and_descendants` khi role là manager

## Research Findings - Document Module hiện tại
- Create/upload: HOÀN THIỆN end-to-end (route, use case, repo, DI, tests)
- List: THIẾU HOÀN TOÀN (không có route, use case, repo method, DTO)
- Detail (get by id): CHỈ CÓ repo `find_by_id`, không có route/use case
- Update: THIẾU HOÀN TOÀN
- Delete: THIẾU HOÀN TOÀN (cần cleanup MinIO + DB)
- Search/filter: THIẾU HOÀN TOÀN
- Permission cho read/update/delete: CHƯA CÓ (chỉ có `upload_document` cho create)

## Research Findings - RBAC Pattern
- Pattern chuẩn: `rbac_service.require_permission(actor, "permission_code")` để block endpoint
- Pattern filter: tính scope (all/department/self), rồi filter repo query theo đó
- Department subtree: `dept_tree_service.get_dept_and_descendants(actor.department_id, all_depts)`
- Agentic access policy: `evaluate_access(document_record, user_context)` + `build_retrieval_filter`
- Scope hiện có: task (admin/bod→all, manager→department, else→self), leave, attendance

## Research Findings - Test Infrastructure
- Backend: pytest mạnh, asyncio_mode=auto, đã có test cho document create + RBAC
- Không có CI tự động tìm thấy, nhưng local pytest chạy được
- Frontend: Angular unit test + Playwright E2E wired, nhưng chưa proven nhiều

## Open Questions ĐÃ CHỐT
- Quyền read áp dụng cho: list + detail + search ✓
- Chiến lược: C (department + role cùng quyết định) ✓
- Test: TDD backend ✓

## Scope Boundaries
- INCLUDE:
  - Thêm permission constants: `read_document`, `update_document`, `delete_document`
  - Repository methods: list, list_by_departments, list_by_owner, update, delete
  - Use cases: ListDocuments, GetDocumentById, UpdateDocument, DeleteDocument, SearchDocuments
  - Routes: GET list, GET detail, PUT update, DELETE delete, GET search
  - DTOs: ListDocumentRequest, DocumentDetailResponse, UpdateDocumentRequest, SearchDocumentRequest
  - RBAC scope helper `get_document_scope` trong RBACService
  - Seed data update cho permissions mới
  - Backend tests (TDD): use case unit tests + integration tests cho permissions
- EXCLUDE:
  - Frontend UI component mới (chỉ backend CRUD + RBAC là trọng tâm)
  - Thay đổi agentic pipeline (đó là module khác)
  - Export PDF/CSV (không đề cập)
  - Versioning tài liệu
  - Notification khi document thay đổi
