# Hoàn thiện CRUD cho module Document với RBAC theo phòng ban và role

## TL;DR

> **Tóm tắt nhanh**: Hoàn thiện backend CRUD cho module `document` bằng cách bổ sung list/detail/update/delete/search, đồng thời áp dụng quyền `read` theo mô hình kết hợp **department + role**. Router giữ mỏng, authorization nằm ở use case/domain service, và backend CRUD/RBAC dùng TDD chọn lọc.
>
> **Deliverables**:
> - API CRUD đầy đủ cho `document`: list, detail, update, delete, search
> - Rule read thống nhất cho list/detail/search/download metadata nếu có
> - Permission seed mới: `read_document`, `update_document`, `delete_document`
> - Repository/use case/DTO/schema đầy đủ cho các action còn thiếu
> - Test pytest cho CRUD + RBAC matrix
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves + final verification
> **Critical Path**: Task 1 → Task 3 → Task 6 → Task 9 → F1-F4

---

## Context

### Original Request
Người dùng yêu cầu: “thực hiện lên plan cập nhật hoàn thiện CRUD cho module document, và chú ý về read thì phân quyền theo phòng ban và role”. Sau đó người dùng chốt chọn hướng **C** và yêu cầu plan bằng **tiếng Việt**.

### Interview Summary
**Key Discussions**:
- Chọn rule read theo hướng C: department + role cùng quyết định phạm vi xem.
- `read` áp dụng cho list, detail, search. Download/file access nếu route đó tồn tại cũng phải dùng cùng policy.
- Frontend không phải trọng tâm, plan tập trung backend CRUD + RBAC.
- Backend test dùng TDD chọn lọc vì repo đã có pytest và test document/RBAC hiện hữu.

**Research Findings**:
- `app/presentation/api/v1/documents.py` hiện chỉ có `POST /api/v1/documents/` cho create/upload.
- `app/application/use_cases/document/create_document.py` đã hoàn thiện upload validation, RBAC `upload_document`, MinIO write, DB persistence, rollback cleanup.
- `app/domain/repositories/documents_repository.py` và `app/infrastructure/database/repositories/sqlalchemy_documents_repo.py` mới có `create` và `find_by_id`.
- `app/application/dtos/document.py` và `app/presentation/schemas/document_schema.py` mới phục vụ create/output cơ bản.
- Pattern RBAC chuẩn nằm ở `app/domain/services/rbac_service.py` và `app/domain/services/department_tree.py`.
- Pattern document access policy gần nhất nằm ở `app/agentic/contracts/access_policy.py` và `app/agentic/pipeline/access_control/core.py`.
- Test infra backend dùng pytest tốt, có sẵn test cho create document và RBAC.

### Metis Review
**Identified Gaps** (addressed):
- Cần khóa rule read bằng câu một nghĩa và test matrix → plan định nghĩa truth table cho employee/manager/admin.
- Search là leakage path → list/detail/search dùng cùng document read policy.
- CRUD dễ phình scope → plan loại trừ versioning, restore, audit log, bulk, export.
- Authorization không được trôi vào router → plan bắt buộc use case/domain service.

---

## Work Objectives

### Core Objective
Hoàn thiện backend CRUD cho module `document` theo đúng kiến trúc hiện tại của repo, đồng thời bảo đảm mọi đường đọc document được lọc hoặc chặn theo role + department trước khi trả dữ liệu.

### Concrete Deliverables
- `GET /api/v1/documents/` trả toàn bộ document user được phép thấy theo role + phòng ban.
- `GET /api/v1/documents/{document_id}` detail với access check.
- `GET /api/v1/documents?q=...` search keyword ngay trên list endpoint, chỉ trong tập document user được phép thấy.
- `PATCH/PUT /api/v1/documents/{document_id}` chỉ update metadata.
- `DELETE /api/v1/documents/{document_id}` hard delete document và cleanup MinIO object.
- Repository methods cho list/search/update/delete.
- DTO/schema cho request/response mới.
- Permission seed cho `read_document`, `update_document`, `delete_document`.
- Pytest unit/integration coverage cho CRUD + RBAC.

### Definition of Done
- [ ] `pytest tests/unit/application/test_*document* tests/unit/domain/test_rbac_service.py` PASS.
- [ ] Integration tests cho document CRUD trả đúng 200/204/401/403/404.
- [ ] `GET /documents` trả toàn bộ document user được phép thấy theo role + department.
- [ ] `GET /documents?q=...` chỉ search trong tập document user được phép thấy.
- [ ] User thường không thấy document ngoài department trong list/search/detail.
- [ ] Manager thấy document trong department của mình và department con.
- [ ] Admin/BOD thấy toàn bộ document.
- [ ] Update chỉ sửa metadata, không sửa policy read.
- [ ] Router không chứa business authorization phức tạp.

### Must Have
- Read policy dùng chung cho list/detail/search/download nếu route download tồn tại.
- Authorization nằm trong use case/domain service, không hard-code ở router.
- Search chạy trên chính `GET /documents` qua query param `q`, không tạo route riêng ở MVP.
- `GET /documents` trả toàn bộ document user được phép thấy, không pagination ở MVP.
- Search không được leak metadata của document ngoài scope.
- Update chỉ cho sửa metadata (ví dụ `title`, `description`, và `status` nếu thực sự cần), không sửa read policy ở MVP.
- Delete là hard delete; nếu object MinIO không tồn tại thì coi như xóa xong, nếu MinIO lỗi thật sự thì raise exception đã định nghĩa.
- Update/delete phải có permission riêng, không dùng lẫn `read_document`.
- TDD cho backend use case/RBAC trước khi implement logic chính.

### Must NOT Have (Guardrails)
- Không thêm frontend UI mới nếu người dùng chưa yêu cầu.
- Không thêm document versioning.
- Không thêm restore/soft-delete phức tạp nếu DB hiện tại chưa hỗ trợ rõ.
- Không thêm audit log/bulk action/export/notification.
- Không rewrite agentic pipeline.
- Không thêm pagination cho `GET /documents` ở MVP.
- Không thêm route search riêng ở MVP.
- Không cho update read policy/visibility scope qua update ở MVP.
- Không đưa logic phân quyền vào router ngoài việc lấy `actor` từ `get_current_user`.
- Không trả document trước rồi mới filter ở client.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - Tất cả verification phải agent-executed. Không có acceptance criteria nào yêu cầu người dùng tự kiểm tra.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: TDD chọn lọc cho backend CRUD/RBAC, tests-after tối thiểu nếu UI bị chạm
- **Framework**: pytest backend, Playwright nếu cần route/UI verification
- **If TDD**: Mỗi task backend quan trọng theo RED → GREEN → REFACTOR
- **MVP defaults locked**:
  - Search dùng query param `q` trên `GET /documents`
  - Không pagination ở MVP
  - Update chỉ metadata
  - Delete hard delete, object missing thì ignore, MinIO failure thật thì raise exception

### QA Policy
Mỗi task phải có QA scenario agent-executed. Evidence lưu tại `.omo/evidence/task-{N}-{scenario-slug}.{ext}`.

- **API/Backend**: dùng Bash/curl hoặc pytest để gọi endpoint và assert status + JSON fields.
- **Library/Module**: dùng pytest trực tiếp cho use case/domain service.
- **Storage**: dùng fake/Mock MinIO trong unit test, integration chỉ khi repo đã có fixture phù hợp.

### Document Read Policy Truth Table

| Actor | Department condition | Expected read scope |
|---|---|---|
| unauthenticated | N/A | 401 |
| employee | same department | allow |
| employee | other department | deny / filtered out |
| manager | own department | allow |
| manager | descendant department | allow |
| manager | unrelated department | deny / filtered out |
| admin | any department | allow |
| bod | any department | allow |
| inactive user | any | deny |

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation + tests first):
├── Task 1: Permission seed + RBAC document scope helper [quick]
├── Task 2: DTO/schema contract cho list/detail/update/search [quick]
├── Task 3: Repository interface + SQLAlchemy query contracts [quick]
├── Task 4: Test matrix fixtures cho document RBAC [quick]
└── Task 5: Domain access policy adapter cho Document entity [unspecified-high]

Wave 2 (Use cases, MAX PARALLEL):
├── Task 6: ListDocuments use case + tests (depends: 1,2,3,4,5) [unspecified-high]
├── Task 7: GetDocumentById use case + tests (depends: 1,2,3,4,5) [unspecified-high]
├── Task 8: SearchDocuments use case + tests (depends: 1,2,3,4,5) [unspecified-high]
├── Task 9: UpdateDocument use case + tests (depends: 1,2,3) [unspecified-high]
└── Task 10: DeleteDocument use case + tests (depends: 1,3) [unspecified-high]

Wave 3 (Routes + integration):
├── Task 11: Wire DI providers for new use cases (depends: 6-10) [quick]
├── Task 12: Add API routes for CRUD/search (depends: 11) [quick]
├── Task 13: Integration tests for CRUD + RBAC API behavior (depends: 12) [unspecified-high]
└── Task 14: Regression cleanup + docs-in-code consistency check (depends: 13) [quick]

Wave FINAL (After ALL tasks):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real API QA execution (unspecified-high)
└── Task F4: Scope fidelity check (deep)
```

### Dependency Matrix

- **1**: blocks 6,7,8,9,10,13
- **2**: blocks 6,7,8,9,12,13
- **3**: blocks 6,7,8,9,10
- **4**: blocks 6,7,8,13
- **5**: blocks 6,7,8
- **6**: blocked by 1,2,3,4,5; blocks 11,12,13
- **7**: blocked by 1,2,3,4,5; blocks 11,12,13
- **8**: blocked by 1,2,3,4,5; blocks 11,12,13
- **9**: blocked by 1,2,3; blocks 11,12,13
- **10**: blocked by 1,3; blocks 11,12,13
- **11**: blocked by 6,7,8,9,10; blocks 12
- **12**: blocked by 11; blocks 13
- **13**: blocked by 12; blocks 14
- **14**: blocked by 13; blocks F1-F4

### Agent Dispatch Summary

- **Wave 1**: 5 tasks - T1 quick, T2 quick, T3 quick, T4 quick, T5 unspecified-high
- **Wave 2**: 5 tasks - T6-T10 unspecified-high
- **Wave 3**: 4 tasks - T11 quick, T12 quick, T13 unspecified-high, T14 quick
- **FINAL**: 4 review agents - F1 oracle, F2 unspecified-high, F3 unspecified-high, F4 deep

---

## TODOs

- [x] 1. Bổ sung permission và scope helper cho document

  **What to do**:
  - Thêm permission constants/seed cho `read_document`, `update_document`, `delete_document`.
  - Bổ sung `get_document_scope(actor)` trong `RBACService` theo truth table đã chốt: admin/bod → all, manager → department, employee → same department only.
  - Nếu cần subtree cho manager, dùng `DepartmentTreeService` thay vì hard-code.
  - Viết test trước cho scope helper và permission check mới.

  **Must NOT do**:
  - Không hard-code logic phân quyền ở router.
  - Không đổi semantics của task/leave/attendance scope hiện có.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: thay đổi nhỏ gọn, tập trung RBAC helper + seed + test đơn vị.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: plan đã có research đủ, task implement chỉ cần follow plan.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3, 4, 5)
  - **Blocks**: 6, 7, 8, 9, 10
  - **Blocked By**: None

  **References**:
  - `/home/pdat/Documents/master-operation/app/domain/services/rbac_service.py` - pattern chuẩn cho permission checks và scope helpers.
  - `/home/pdat/Documents/master-operation/app/domain/services/department_tree.py` - cách tính department descendants cho manager scope.
  - `/home/pdat/Documents/master-operation/app/infrastructure/database/seed.py` - nơi seed permissions hiện có như `upload_document`.
  - `/home/pdat/Documents/master-operation/tests/unit/domain/test_rbac_service.py` - pattern test thuần domain cho RBACService.

  **Acceptance Criteria**:
  - [ ] Permission mới tồn tại trong seed/constant nơi repo đang quản lý.
  - [ ] `RBACService` có helper scope cho document read.
  - [ ] `pytest tests/unit/domain/test_rbac_service.py` PASS với scenario document scope mới.

  **QA Scenarios**:
  ```
  Scenario: document scope for manager includes descendants
    Tool: Bash (pytest)
    Preconditions: test data có manager department=10, child department=11
    Steps:
      1. Chạy pytest cho test case manager document scope
      2. Assert helper trả về `department` và descendant expansion đúng
      3. Assert employee tương tự không có descendant scope
    Expected Result: test PASS, manager scope khác employee scope
    Failure Indicators: helper trả sai scope hoặc không xét descendant
    Evidence: .omo/evidence/task-1-manager-scope.txt

  Scenario: permission denial for inactive user
    Tool: Bash (pytest)
    Preconditions: fixture user inactive
    Steps:
      1. Chạy test `require_permission` với inactive user
      2. Assert raise `PermissionDenied`
    Expected Result: inactive user bị deny
    Evidence: .omo/evidence/task-1-inactive-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(document): add document RBAC permissions`
  - Files: `app/domain/services/rbac_service.py`, seed, tests
  - Pre-commit: `pytest tests/unit/domain/test_rbac_service.py`

- [x] 2. Tạo contract DTO/schema cho list, detail, update, search

  **What to do**:
  - Bổ sung request/response DTO cho list/detail/update/search.
  - Chuẩn hóa fields được phép update để tránh scope creep sang file versioning.
  - Bổ sung FastAPI schemas tương ứng ở presentation layer.
  - Viết test serialization/validation nếu repo hiện có pattern phù hợp.

  **Must NOT do**:
  - Không thêm fields cho version history, restore, audit trail.
  - Không trộn file-replacement workflow nếu chưa chốt trong plan.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: task chủ yếu là contract/schema alignment.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: không liên quan backend contract.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3, 4, 5)
  - **Blocks**: 6, 7, 8, 9, 12
  - **Blocked By**: None

  **References**:
  - `/home/pdat/Documents/master-operation/app/application/dtos/document.py` - pattern DTO hiện có cho create/output.
  - `/home/pdat/Documents/master-operation/app/presentation/schemas/document_schema.py` - pattern FastAPI schema cho document module.
  - `/home/pdat/Documents/master-operation/app/domain/entities/document.py` - source of truth cho enum/status/visibility/classification.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit -k document and schema` PASS với DTO/schema mới.
  - [ ] List response DTO có tối thiểu `id`, `title`, `classification`, `visibility_scope`, `department_id`, `created_at`.
  - [ ] Detail response DTO chứa đúng fields đã chốt và không có field versioning/restore.
  - [ ] Update request DTO chỉ cho phép metadata/policy fields trong scope.

  **QA Scenarios**:
  ```
  Scenario: update request rejects out-of-scope field
    Tool: Bash (pytest)
    Preconditions: schema validation test có payload chứa field versioning giả
    Steps:
      1. Validate payload qua schema/model
      2. Assert field lạ bị reject hoặc ignore theo contract đã chọn
    Expected Result: payload không mở scope ngoài plan
    Evidence: .omo/evidence/task-2-update-schema.txt

  Scenario: detail response serializes visibility fields
    Tool: Bash (pytest)
    Preconditions: sample Document entity với classification/visibility
    Steps:
      1. Serialize response DTO
      2. Assert output chứa các field expected và không lộ field nội bộ thừa
    Expected Result: response contract ổn định
    Evidence: .omo/evidence/task-2-detail-response.txt
  ```

  **Commit**: YES
  - Message: `feat(document): add CRUD dto contracts`
  - Files: DTO/schema files
  - Pre-commit: `pytest tests/unit -k document`

- [x] 3. Mở rộng repository contract và query methods cho CRUD/search

  **What to do**:
  - Thêm repository interface methods cho list, list_by_departments, list_by_owner, search, update, delete.
  - Implement trong SQLAlchemy repo với query shape khớp scope all/department/self.
  - Thiết kế search để policy filter có thể áp lên query, tránh leak từ search results.

  **Must NOT do**:
  - Không filter ở client side.
  - Không implement query chung chung thiếu phân biệt department/self scope.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: task tập trung 1 module repository + query contracts.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `ultrabrain`: không cần cho query extension chuẩn.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 4, 5)
  - **Blocks**: 6, 7, 8, 9, 10
  - **Blocked By**: None

  **References**:
  - `/home/pdat/Documents/master-operation/app/domain/repositories/documents_repository.py` - interface hiện tại cần được mở rộng.
  - `/home/pdat/Documents/master-operation/app/infrastructure/database/repositories/sqlalchemy_documents_repo.py` - nơi implement SQLAlchemy queries.
  - `/home/pdat/Documents/master-operation/app/application/use_cases/task/list_tasks.py` - pattern chọn query theo scope.
  - `/home/pdat/Documents/master-operation/app/application/use_cases/leave_request/list_leave_request.py` - pattern department + descendants list filtering.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit -k "document and repository"` PASS.
  - [ ] Repository interface có `list_all`, `list_by_departments`, `list_by_owner`, `search`, `update`, `delete`.
  - [ ] Search method nhận scope/filter input rõ ràng.
  - [ ] Delete method trả đủ thông tin object path để cleanup MinIO.

  **QA Scenarios**:
  ```
  Scenario: repository list_by_departments returns only scoped rows
    Tool: Bash (pytest)
    Preconditions: seeded DB test với docs nhiều department
    Steps:
      1. Gọi repository method với dept_ids [10,11]
      2. Assert docs department ngoài scope không xuất hiện
    Expected Result: query layer đã filter đúng
    Evidence: .omo/evidence/task-3-list-by-departments.txt

  Scenario: search query does not leak foreign department docs
    Tool: Bash (pytest)
    Preconditions: keyword trùng ở 2 department
    Steps:
      1. Chạy repository search dưới scope hạn chế
      2. Assert chỉ docs hợp lệ được trả về
    Expected Result: không leak metadata từ search
    Evidence: .omo/evidence/task-3-search-scope.txt
  ```

  **Commit**: YES
  - Message: `feat(document): extend repository queries`
  - Files: repository interface + implementation
  - Pre-commit: `pytest tests/unit -k document`

- [x] 4. Tạo test fixtures và matrix cho document RBAC

  **What to do**:
  - Chuẩn hóa fixtures cho employee/manager/admin, nhiều department, descendant department, unauthorized document.
  - Viết ma trận test tối thiểu cho list/detail/search/update/delete.
  - Bảo đảm search/list/detail dùng chung policy expectations.

  **Must NOT do**:
  - Không tạo matrix khổng lồ vượt scope.
  - Không bỏ qua negative scenarios.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: task test scaffolding, nhỏ nhưng quan trọng để unlock TDD wave 2.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `writing`: không phải docs prose.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 5)
  - **Blocks**: 6, 7, 8, 13
  - **Blocked By**: None

  **References**:
  - `/home/pdat/Documents/master-operation/tests/unit/application/test_create_document_use_case.py` - style AsyncMock/MagicMock/pytest.raises.
  - `/home/pdat/Documents/master-operation/tests/integration/test_rbac_scenarios.py` - scenario-matrix style cho permission allow/deny.
  - `/home/pdat/Documents/master-operation/tests/integration/conftest.py` - auth token fixtures cho integration tests.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit -k document_rbac_fixtures` PASS.
  - [ ] Fixtures tạo được employee, manager, admin và ít nhất 2 department có quan hệ parent/child.
  - [ ] Ma trận test có ít nhất 1 happy path và 1 deny path cho mỗi action list/detail/search/update/delete.
  - [ ] Search/list/detail parity được encode thành assertions cụ thể.

  **QA Scenarios**:
  ```
  Scenario: test matrix covers all actor classes
    Tool: Bash (pytest)
    Preconditions: fixture module đã tạo xong
    Steps:
      1. Chạy pytest với marker/keyword document rbac
      2. Assert employee/manager/admin cases đều được execute
    Expected Result: matrix không thiếu actor class chính
    Evidence: .omo/evidence/task-4-rbac-matrix.txt

  Scenario: negative matrix includes cross-department denial
    Tool: Bash (pytest)
    Preconditions: doc thuộc department khác manager scope
    Steps:
      1. Chạy denial tests
      2. Assert 403 hoặc filtered-out behavior khớp contract
    Expected Result: deny path được khóa bằng test
    Evidence: .omo/evidence/task-4-cross-dept-deny.txt
  ```

  **Commit**: YES
  - Message: `test(document): add RBAC fixtures and matrix`
  - Files: tests fixtures and cases
  - Pre-commit: `pytest tests/unit tests/integration -k "document and rbac"`

- [x] 5. Tạo access policy adapter cho Document theo pattern agentic

  **What to do**:
  - Thêm adapter/helper để map `Document` entity hoặc ORM model sang access policy record có thể evaluate.
  - Tái sử dụng tối đa `AccessPolicyMetadata` / `evaluate_access` hoặc mirror logic tương thích, tránh duplicate semantics.
  - Nếu manager subtree cần hỗ trợ mà policy hiện tại chưa support, thêm explicit handling ở document module path theo guardrail của plan.

  **Must NOT do**:
  - Không rewrite toàn bộ agentic pipeline.
  - Không tạo policy semantics mâu thuẫn với truth table đã chốt.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: task đòi hỏi cẩn thận để tái dùng đúng policy model mà không làm lệch semantics.
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - `security-research`: không cần mức audit bảo mật đầy đủ cho task adapter.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2, 3, 4)
  - **Blocks**: 6, 7, 8
  - **Blocked By**: None

  **References**:
  - `/home/pdat/Documents/master-operation/app/agentic/contracts/access_policy.py` - model policy chuẩn cho classification/visibility/allowed_roles/department/owner.
  - `/home/pdat/Documents/master-operation/app/agentic/pipeline/access_control/core.py` - evaluate_access hiện tại cho role/department/owner.
  - `/home/pdat/Documents/master-operation/app/domain/entities/document.py` - fields hiện có trên Document entity.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit -k document_policy` PASS.
  - [ ] Adapter map được `Document` sang policy input không lỗi với sample entity.
  - [ ] Employee/manager/admin evaluation khớp truth table đã chốt.
  - [ ] Không có duplicate policy logic nào ở router, repo, hoặc use case — kiểm tra bằng grep trong file router và repo không thấy evaluate_access gọi trực tiếp.

  **QA Scenarios**:
  ```
  Scenario: evaluate_access allows same-department employee
    Tool: Bash (pytest)
    Preconditions: document policy department_id=10, actor employee dept=10
    Steps:
      1. Map document qua adapter
      2. Evaluate access với employee context
      3. Assert allowed=True
    Expected Result: same department employee được xem
    Evidence: .omo/evidence/task-5-employee-allow.txt

  Scenario: evaluate_access denies unrelated manager
    Tool: Bash (pytest)
    Preconditions: manager dept=20, document dept=10, không phải descendant
    Steps:
      1. Evaluate access
      2. Assert denied theo contract
    Expected Result: manager ngoài scope bị deny
    Evidence: .omo/evidence/task-5-manager-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(document): add access policy adapter`
  - Files: access policy helper + tests
  - Pre-commit: `pytest tests/unit -k document`

- [x] 6. ListDocuments use case + tests

  **What to do**:
  - Implement `ListDocumentsUseCase.execute(actor)` theo scope helper từ Task 1.
  - Gọi repo method phù hợp theo scope (all/department+descendants/self).
  - Map result qua response DTO từ Task 2.
  - Viết unit tests với AsyncMock repo.

  **Must NOT do**:
  - Không filter ở router.
  - Không trả list rồi strip ở client.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần implement đúng 3-branch scope logic + tests đủ cho list endpoint.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 7, 8, 9, 10)
  - **Blocks**: 11, 12, 13
  - **Blocked By**: 1, 2, 3, 4, 5

  **References**:
  - `/home/pdat/Documents/master-operation/app/application/use_cases/task/list_tasks.py` - 3-branch scope pattern chuẩn.
  - `/home/pdat/Documents/master-operation/app/application/use_cases/leave_request/list_leave_request.py` - department+descendants scope filtering.
  - `/home/pdat/Documents/master-operation/tests/unit/application/test_create_document_use_case.py` - style AsyncMock test.
  - Task 1 output: `get_document_scope(actor)` helper.
  - Task 2 output: list DTO schema.
  - Task 3 output: `list_all()`, `list_by_departments()`, `list_by_owner()`.
  - Task 5 output: access policy adapter.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit/application/test_list_documents_use_case.py` PASS.
  - [ ] Admin nhận all documents.
  - [ ] Manager nhận department + descendants only.
  - [ ] Employee nhận own department only.
  - [ ] Inactive user nhận PermissionDenied.

  **QA Scenarios**:
  ```
  Scenario: admin list returns all documents
    Tool: Bash (pytest)
    Preconditions: MockRepo trả [doc1, doc2, doc3] từ 3 departments
    Steps:
      1. Execute use case với admin actor
      2. Assert result length = 3
    Expected Result: admin thấy toàn bộ
    Evidence: .omo/evidence/task-6-admin-list.txt

  Scenario: employee list returns only own department
    Tool: Bash (pytest)
    Preconditions: docs gồm dept=10 và dept=20; employee dept=10
    Steps:
      1. Execute use case với employee actor dept=10
      2. Assert result chỉ chứa docs dept=10
    Expected Result: cross-dept docs không xuất hiện
    Evidence: .omo/evidence/task-6-employee-filter.txt
  ```

  **Commit**: NO (groups với Task 7, 8)

- [x] 7. GetDocumentById use case + tests

  **What to do**:
  - Implement `GetDocumentByIdUseCase.execute(actor, document_id)`.
  - Sau khi tìm record, evaluate policy access; raise `PermissionDenied` hoặc NotFound nếu ngoài scope.
  - Map qua response DTO.
  - Viết unit tests.

  **Must NOT do**:
  - Không chỉ check auth JWT mà quên kiểm policy của document cụ thể đó.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần evaluate policy của từng document, không phải chỉ scope chung.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 8, 9, 10)
  - **Blocks**: 11, 12, 13
  - **Blocked By**: 1, 2, 3, 4, 5

  **References**:
  - `/home/pdat/Documents/master-operation/app/application/use_cases/task/get_task.py` - pattern single-resource access check cho scoped reads.
  - Task 5 output: access policy adapter + evaluate_access.
  - Task 2 output: detail DTO.
  - Task 3 output: `find_by_id()`.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit/application/test_get_document_use_case.py` PASS.
  - [ ] Employee xem document đúng department → 200.
  - [ ] Employee xem document ngoài department → PermissionDenied.
  - [ ] Admin xem bất kỳ document → 200.
  - [ ] Document không tồn tại → NotFound.

  **QA Scenarios**:
  ```
  Scenario: detail returns 200 for authorized employee
    Tool: Bash (pytest)
    Preconditions: doc dept=10, employee dept=10
    Steps:
      1. Execute GetDocumentById use case
      2. Assert result.id khớp document_id requested
    Expected Result: authorized read thành công
    Evidence: .omo/evidence/task-7-employee-allow.txt

  Scenario: detail raises PermissionDenied for foreign employee
    Tool: Bash (pytest)
    Preconditions: doc dept=20, employee dept=10
    Steps:
      1. Execute use case
      2. Assert raises PermissionDenied
    Expected Result: cross-dept access bị chặn
    Evidence: .omo/evidence/task-7-deny.txt
  ```

  **Commit**: NO (groups với Task 6, 8)

- [x] 8. SearchDocuments use case + tests

  **What to do**:
  - Implement `SearchDocumentsUseCase.execute(actor, query)`.
  - Áp dụng scope filter trước khi search, không search trước rồi mới filter.
  - Dùng cùng policy evaluation logic như list/detail.
  - Trả list documents. Không cần pagination trong scope này — basic list được chấp nhận.

  **Must NOT do**:
  - Không đưa raw search results rồi filter ở controller.
  - Không search không scope.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần bảo đảm search không leak, phải dùng chung policy.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 9, 10)
  - **Blocks**: 11, 12, 13
  - **Blocked By**: 1, 2, 3, 4, 5

  **References**:
  - Task 3 output: `search()` method với scope filter hook.
  - Task 5 output: access policy adapter.
  - Task 2 output: search request DTO.
  - `/home/pdat/Documents/master-operation/app/agentic/pipeline/retrieval/core.py` - defense-in-depth double-filter pattern.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit/application/test_search_documents_use_case.py` PASS.
  - [ ] Search dùng cùng scope input như list — kiểm tra bằng test assert cùng dept_ids được truyền vào search và list repo call.
  - [ ] Keyword khớp document ngoài scope → không xuất hiện trong results.

  **QA Scenarios**:
  ```
  Scenario: search returns only authorized docs matching keyword
    Tool: Bash (pytest)
    Preconditions: docs dept=10 và dept=20, keyword match cả hai; employee dept=10
    Steps:
      1. Execute search với keyword
      2. Assert chỉ dept=10 docs trong results
    Expected Result: cross-dept doc không lọt qua search
    Evidence: .omo/evidence/task-8-search-scope.txt

  Scenario: admin search sees all matches
    Tool: Bash (pytest)
    Preconditions: same setup
    Steps:
      1. Execute search với admin actor
      2. Assert cả hai docs xuất hiện
    Expected Result: admin thấy full results
    Evidence: .omo/evidence/task-8-admin-search.txt
  ```

  **Commit**: YES (groups T6, T7, T8)
  - Message: `feat(document): add list/detail/search use cases with scoped access`
  - Files: `app/application/use_cases/document/` 3 new files + tests
  - Pre-commit: `pytest tests/unit/application -k document`

- [x] 9. UpdateDocument use case + tests

  **What to do**:
  - Implement `UpdateDocumentUseCase.execute(actor, document_id, payload)`.
  - Check permission `update_document` từ Task 1.
  - Cho phép update metadata/policy fields trong contract, không cho thay file binary hoặc versioning.
  - Persist changes qua repository update method từ Task 3.

  **Must NOT do**:
  - Không implement file replacement/versioning.
  - Không allow user thay title/status nếu ngoài quyền.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần permission check + partial-update semantics đúng.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 10)
  - **Blocks**: 11, 12, 13
  - **Blocked By**: 1, 2, 3

  **References**:
  - Task 1 output: permission `update_document`, scope helper.
  - Task 2 output: update request DTO.
  - Task 3 output: repository `update()` method.
  - `/home/pdat/Documents/master-operation/app/application/use_cases/document/create_document.py` - RBAC check pattern.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit/application/test_update_document_use_case.py` PASS.
  - [ ] Actor không có `update_document` → PermissionDenied.
  - [ ] actor có permission → `repo.update` được gọi và use case trả DTO với ít nhất các fields `id`, `title`, `updated_at`.
  - [ ] Fields ngoài contract không được truyền vào `repo.update` — kiểm tra bằng assert payload không có field versioning hoặc ngoài update DTO.

  **QA Scenarios**:
  ```
  Scenario: admin updates document successfully
    Tool: Bash (pytest)
    Preconditions: doc tồn tại, admin có update_document
    Steps:
      1. Execute update use case
      2. Assert repo.update called với đúng payload
      3. Assert result đúng DTO
    Expected Result: update thành công
    Evidence: .omo/evidence/task-9-update-success.txt

  Scenario: employee denied update
    Tool: Bash (pytest)
    Preconditions: employee không có update_document
    Steps:
      1. Execute update
      2. Assert raises PermissionDenied
    Expected Result: denied với đúng exception
    Evidence: .omo/evidence/task-9-update-deny.txt
  ```

  **Commit**: NO (groups với Task 10)

- [x] 10. DeleteDocument use case + tests

  **What to do**:
  - Implement `DeleteDocumentUseCase.execute(actor, document_id)`.
  - Check permission `delete_document`.
  - Xóa DB record và cleanup MinIO object theo policy: nếu MinIO cleanup thất bại thì raise exception xác định để caller thấy lỗi và test assert được; không silently ignore.
  - Đảm bảo delete không mở thêm soft-delete/versioning ngoài scope.

  **Must NOT do**:
  - Không thêm soft-delete workflow nếu chưa chốt.
  - Không bỏ qua cleanup MinIO, để tránh orphaned objects.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: side-effect cleanup cần cẩn thận với ordering và error handling.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 6, 7, 8, 9)
  - **Blocks**: 11, 12, 13
  - **Blocked By**: 1, 3

  **References**:
  - Task 1 output: permission `delete_document`.
  - Task 3 output: repository `delete()`.
  - `/home/pdat/Documents/master-operation/app/application/use_cases/document/create_document.py` - MinIO cleanup/rollback pattern.

  **Acceptance Criteria**:
  - [ ] `pytest tests/unit/application/test_delete_document_use_case.py` PASS.
  - [ ] Delete permission check enforced bằng `delete_document`.
  - [ ] MinIO removal được gọi với đúng object path.
  - [ ] Nếu MinIO removal thất bại, test assert exception xác định được raise và lỗi không bị silently ignored.

  **QA Scenarios**:
  ```
  Scenario: delete removes DB and triggers MinIO cleanup
    Tool: Bash (pytest)
    Preconditions: mock repo + mock MinIO
    Steps:
      1. Execute delete use case
      2. Assert repo.delete called
      3. Assert minio.remove_object called với đúng path
    Expected Result: cả hai cleanup được gọi
    Evidence: .omo/evidence/task-10-delete-cleanup.txt

  Scenario: delete denied without permission
    Tool: Bash (pytest)
    Steps:
      1. Execute với actor không có delete_document
      2. Assert PermissionDenied raised
      3. Assert repo.delete NOT called
    Expected Result: không xóa gì nếu không có quyền
    Evidence: .omo/evidence/task-10-delete-deny.txt
  ```

  **Commit**: YES (groups T9, T10)
  - Message: `feat(document): add update/delete use cases`
  - Files: update + delete use case + tests
  - Pre-commit: `pytest tests/unit/application -k document`

- [x] 11. Thêm DI providers cho các use cases mới

  **What to do**:
  - Bổ sung dependency injection cho `ListDocumentsUseCase`, `GetDocumentByIdUseCase`, `SearchDocumentsUseCase`, `UpdateDocumentUseCase`, `DeleteDocumentUseCase` vào `app/di/document.py`.

  **Must NOT do**:
  - Không thêm logic business vào DI provider.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: task wiring DI đơn giản.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential sau Wave 2
  - **Blocks**: 12
  - **Blocked By**: 6, 7, 8, 9, 10

  **References**:
  - `/home/pdat/Documents/master-operation/app/di/document.py` - DI wiring create use case hiện tại.

  **Acceptance Criteria**:
  - [ ] `python -c "from app.di.document import *"` không lỗi import.
  - [ ] Mỗi use case mới có provider function trong DI và resolve được dependency graph.

  **QA Scenarios**:
  ```
  Scenario: DI resolves without import errors
    Tool: Bash (python)
    Steps:
      1. Chạy python -c "from app.di.document import provide_list_documents; print(provide_list_documents)"
      2. Assert không có ImportError
    Expected Result: DI module load thành công
    Evidence: .omo/evidence/task-11-di-import.txt
  ```

  **Commit**: NO (groups với Task 12)

- [x] 12. Thêm API routes cho CRUD/search

  **What to do**:
  - Bổ sung routes cho `GET /api/v1/documents/`, `GET /api/v1/documents/search`, `GET /api/v1/documents/{document_id}`, `PATCH /api/v1/documents/{document_id}`, `DELETE /api/v1/documents/{document_id}`.
  - Router chỉ lấy `actor` từ `get_current_user`, inject use case từ DI, delegate authorization sang use case.
  - Đảm bảo status codes nhất quán.

  **Must NOT do**:
  - Không thêm authorization logic vào router.
  - Không hard-code role check ở router.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: router thin, chỉ wiring và status code mapping.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential sau Task 11
  - **Blocks**: 13
  - **Blocked By**: 11

  **References**:
  - `/home/pdat/Documents/master-operation/app/presentation/api/v1/documents.py` - router hiện có.
  - `/home/pdat/Documents/master-operation/app/presentation/api/v1/roles.py` - thin router pattern.
  - `/home/pdat/Documents/master-operation/app/presentation/dependencies/auth_deps.py` - `get_current_user` dependency.

  **Acceptance Criteria**:
  - [ ] `pytest tests/integration -k document_route_import` PASS.
  - [ ] Router không chứa if/else logic phân quyền ngoài việc lấy `actor`.
  - [ ] Route trả đúng status codes: 200 success, 401 unauthenticated, 403 denied, 404 not found, 422 validation.

  **QA Scenarios**:
  ```
  Scenario: GET /api/v1/documents/ exists and requires authentication
    Tool: Bash (curl)
    Steps:
      1. curl -X GET http://localhost:8000/api/v1/documents/ (no token)
      2. Assert status 401
    Expected Result: 401 Unauthorized
    Evidence: .omo/evidence/task-12-route-noauth.txt

  Scenario: GET /api/v1/documents/{id} wired correctly
    Tool: Bash (curl)
    Steps:
      1. curl -X GET http://localhost:8000/api/v1/documents/999 (với valid token)
      2. Assert status 404 (document không tồn tại)
    Expected Result: 404 cho non-existent document
    Evidence: .omo/evidence/task-12-route-404.txt
  ```

  **Commit**: YES (groups T11, T12)
  - Message: `feat(document): expose CRUD API routes`
  - Files: `app/presentation/api/v1/documents.py`, `app/di/document.py`
  - Pre-commit: `pytest tests/unit -k document`

- [x] 13. Integration tests cho CRUD và RBAC API behavior

  **What to do**:
  - Viết integration tests cho các API routes mới với actor employee/manager/admin.
  - Verify HTTP status + response body cho list/detail/search/update/delete.
  - Đảm bảo parity test cho search/list/detail.

  **Must NOT do**:
  - Không chỉ test happy path.
  - Không test bỏ qua denial cases.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: integration tests cần setup actor + real HTTP request flow.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential sau Task 12
  - **Blocks**: 14
  - **Blocked By**: 12, 4

  **References**:
  - `/home/pdat/Documents/master-operation/tests/integration/test_auth.py` - httpx.AsyncClient pattern.
  - `/home/pdat/Documents/master-operation/tests/integration/test_rbac_scenarios.py` - scenario matrix style.
  - `/home/pdat/Documents/master-operation/tests/integration/conftest.py` - token fixtures.

  **Acceptance Criteria**:
  - [ ] `pytest tests/integration -k document` PASS.
  - [ ] 401 cho unauthenticated requests.
  - [ ] 403 cho cross-scope reads.
  - [ ] 200 + body fields chính xác cho authorized reads.
  - [ ] 200 cho authorized update với response body chứa ít nhất `id` và `updated_at`.
  - [ ] 204 hoặc 200 với empty body cho authorized delete — chọn 204 làm chuẩn.

  **QA Scenarios**:
  ```
  Scenario: employee sees 200 for own department doc
    Tool: Bash (pytest httpx)
    Preconditions: employee token, doc dept=same
    Steps:
      1. GET /api/v1/documents/{id} với employee token
      2. Assert status 200, response.id khớp
    Expected Result: 200 với document metadata
    Evidence: .omo/evidence/task-13-integration-allow.txt

  Scenario: employee sees 403 for foreign document
    Tool: Bash (pytest httpx)
    Preconditions: employee token, doc dept=different
    Steps:
      1. GET /api/v1/documents/{id} với employee token
      2. Assert status 403
    Expected Result: 403 Forbidden
    Evidence: .omo/evidence/task-13-integration-deny.txt

  Scenario: search list parity — both return same scoped set
    Tool: Bash (pytest httpx)
    Steps:
      1. GET /api/v1/documents/ với employee token → collect ids
      2. GET /api/v1/documents/search?q=test với employee token → collect ids
      3. Assert không có id từ search nằm ngoài set từ list (policy parity)
    Expected Result: no search leakage beyond list scope
    Evidence: .omo/evidence/task-13-search-list-parity.txt
  ```

  **Commit**: YES
  - Message: `test(document): add CRUD RBAC integration tests`
  - Files: `tests/integration/test_document_crud.py`
  - Pre-commit: `pytest tests/integration -k document`

- [~] 14. Regression cleanup và consistency check

  **What to do**:
  - Chạy toàn bộ test suite để phát hiện regression.
  - Review diff các file thay đổi để bảo đảm không có logic phân quyền trong router, không có feature ngoài scope.
  - Đảm bảo seed data và tests khớp nhau.

  **Must NOT do**:
  - Không add features mới trong task này.
  - Không force-skip failing tests.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: task là regression check và consistency sweep.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential sau Task 13
  - **Blocks**: F1, F2, F3, F4
  - **Blocked By**: 13

  **References**:
  - `pytest.ini` - cấu hình test toàn bộ backend.
  - Plan guardrails trong Must NOT Have section.

  **Acceptance Criteria**:
  - [ ] `pytest` (toàn bộ suite) PASS không có regression từ tasks mới.
  - [ ] Grep router files không thấy business authorization logic ngoài `get_current_user` injection.
  - [ ] Kiểm tra scope bằng `pytest` không có failures và không có thay đổi file ngoài danh sách scoped trong plan.

  **QA Scenarios**:
  ```
  Scenario: full test suite passes without regression
    Tool: Bash (pytest)
    Steps:
      1. Chạy pytest từ root
      2. Assert 0 unexpected failures
    Expected Result: all tests pass
    Evidence: .omo/evidence/task-14-regression.txt

  Scenario: router files are thin (no if/else authorization)
    Tool: Bash (grep)
    Steps:
      1. Grep router file cho pattern if.*role hoặc if.*permission
      2. Assert không có match ngoài get_current_user injection
    Expected Result: CLEAN
    Evidence: .omo/evidence/task-14-router-thin.txt
  ```

  **Commit**: YES (cleanup commit nếu cần)
  - Message: `chore(document): regression cleanup`
  - Files: bất kỳ file cần fix
  - Pre-commit: `pytest`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents chạy SONG SONG. Tất cả phải APPROVE. Trình bày kết quả tổng hợp cho user và chờ user explicit okay trước khi hoàn tất.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Đọc plan end-to-end. Với từng Must Have, kiểm tra implementation tồn tại bằng đọc file, curl endpoint hoặc chạy command. Với từng Must NOT Have, search codebase để bảo đảm không có pattern bị cấm. Kiểm tra evidence files trong `.omo/evidence/`. So sánh deliverables với plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Chạy `pytest`, type/lint command hiện có nếu repo định nghĩa. Review changed files để phát hiện: broad exception swallowing, commented-out code, unused imports, logic phân quyền trong router, duplicate policy logic, hard-coded role ngoài RBAC service.
  Output: `Build [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real API QA Execution** — `unspecified-high`
  Start clean test state. Chạy mọi QA scenario từ từng task. Test tích hợp list/detail/search/update/delete với actor employee/manager/admin. Lưu response bodies và command logs vào `.omo/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  Đọc actual diff và đối chiếu từng task. Đảm bảo không có frontend UI mới, versioning, restore, audit log, export, bulk action, notification, agentic pipeline rewrite. Flag mọi file không nằm trong scope.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Commit 1**: `feat(document): add RBAC permissions and contracts` - RBAC scope, seed, DTO/schema, repository contracts, tests
- **Commit 2**: `feat(document): add read use cases with scoped access` - list/detail/search use cases and tests
- **Commit 3**: `feat(document): add update and delete use cases` - update/delete use cases and tests
- **Commit 4**: `feat(document): expose CRUD API routes` - DI, routes, integration tests
- **Commit 5**: `test(document): cover CRUD RBAC scenarios` - regression and QA fixes if needed

---

## Success Criteria

### Verification Commands
```bash
pytest tests/unit/application/test_create_document_use_case.py tests/unit/domain/test_rbac_service.py
# Expected: PASS

pytest tests/unit/application -k document
# Expected: PASS

pytest tests/integration -k "document or rbac"
# Expected: PASS for implemented document/RBAC paths
```

### Final Checklist
- [ ] CRUD backend routes exist and are wired.
- [ ] List/detail/search use identical read policy.
- [ ] Employee cannot read other department documents.
- [ ] Manager can read own department + descendants only.
- [ ] Admin/BOD can read all documents.
- [ ] Update/delete require explicit permissions.
- [ ] Delete handles DB + MinIO cleanup safely.
- [ ] No business authorization in routers.
- [ ] No out-of-scope features added.
