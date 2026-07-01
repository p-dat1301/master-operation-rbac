# Kế hoạch cải thiện frontend admin

## TL;DR

> **Tóm tắt nhanh**: Kế hoạch này cải thiện toàn diện frontend `apps/admin` theo bốn trục: củng cố nền tảng kiến trúc, hoàn thiện độ phủ capability/backend API trên admin UI, giảm nợ kỹ thuật maintainability, và siết chất lượng bằng test + verification tự động.
>
> **Deliverables chính**:
> - Chuẩn hóa routing/config/service/auth-error handling của admin app
> - Bổ sung các capability còn thiếu hoặc mới phủ một phần: attendance, departments, leave balances, users, tasks, leaves, permissions
> - Chuẩn hóa pattern component/state/form/style/test cho các màn hình lớn
> - Đưa app về trạng thái dễ scale hơn mà không rewrite toàn bộ stack
>
> **Estimated Effort**: XL
> **Parallel Execution**: YES - 4 wave chính + 1 final verification wave
> **Critical Path**: 1 → 2 → 6 → 10 → 15 → F1-F4

---

## Context

### Yêu cầu gốc
Lập work plan bằng tiếng Việt cho toàn bộ quá trình cải thiện frontend của dự án, tập trung vào `apps/admin`, bao gồm các đề xuất về kiến trúc, hiệu năng, maintainability, và độ phủ API/backend capability lên frontend.

### Tóm tắt trao đổi
**Các điểm đã xác định**:
- Frontend hiện tại chỉ có `apps/admin`.
- App đang dùng Angular 21 standalone, NG Zorro, Tailwind, Playwright, signals, service layer và guards.
- Các vấn đề nổi bật: eager routes làm bundle lớn, hard-code API base URL, error handling chưa tập trung, service abstraction chưa sạch, nhiều page component phình to, styling/async/form patterns chưa đồng nhất.
- Backend capability chưa được phản ánh đầy đủ ở admin frontend: attendance, departments, leave balances; ngoài ra users/tasks/leaves/permissions mới chỉ phủ một phần UI.
- Có dấu hiệu contract mismatch ở domain leaves giữa backend route review và frontend service hiện tại.

### Kết quả nghiên cứu
- `apps/admin/src/app/app.routes.ts` đang import page components trực tiếp, chưa lazy load feature routes.
- `apps/admin/src/app/app.config.ts` đang hard-code `API_BASE_URL`.
- `BaseApiService` và các service kế thừa đang dùng pattern không thống nhất, có chỗ cast để truy cập `apiBaseUrl`.
- Build production pass nhưng warning vượt budget initial bundle.
- Backend API surface rộng hơn đáng kể so với những flow UI hiện có trên admin app.

### Kết quả review từ Metis
**Các gap đã được xử lý trong plan**:
- Chốt guardrail frontend-only: phạm vi chính là `apps/admin`; backend chỉ xuất hiện như dependency/blocker khi contract không khớp.
- Khóa scope creep: không broad rewrite, không đổi stack, không redesign toàn bộ UI.
- Tách maintainability thành hạng mục cụ thể: routing/config, service abstraction, async state, form strategy, styling system, test breadth.
- Bổ sung edge cases: backend contract chưa sẵn sàng, lazy loading phá guards/providers, runtime config phá dev/test.

---

## Work Objectives

### Mục tiêu cốt lõi
Nâng cấp frontend admin từ trạng thái “discipled but transitional” sang trạng thái ổn định hơn để mở rộng: nền tảng rõ ràng, route/config/service patterns sạch hơn, capability admin phủ sát backend hơn, và chất lượng được khóa bằng test/QA tự động.

### Deliverables cụ thể
- Routing feature của admin app được lazy-load theo capability ưu tiên.
- API base URL không còn hard-code trực tiếp trong `app.config.ts`.
- Pattern service/API access được thống nhất và loại bỏ cast workaround.
- Error/auth handling tập trung cho 401/403/network/API failures.
- Các capability admin còn thiếu/thiếu một phần được đưa vào backlog thực thi rõ ràng và có đường đi UI cụ thể.
- Component/page lớn được chuẩn hóa theo pattern tách logic/presentation/style hợp lý.
- Test coverage và QA scenario được mở rộng theo các flow quan trọng.

### Definition of Done
- [ ] `npm run build` trong `apps/admin` pass và bundle initial không còn vượt budget cấu hình hiện tại hoặc budget được điều chỉnh có chủ đích kèm rationale.
- [ ] `npm run test:unit` pass.
- [ ] `npm run e2e` pass cho các flow cũ và các flow mới thuộc phạm vi plan.
- [ ] Không còn hard-coded API base URL trong runtime app config chính.
- [ ] Không còn pattern cast truy cập `apiBaseUrl` kiểu workaround trong service layer admin.
- [ ] Tất cả capability được chọn trong plan đều có mapping rõ: backend contract ↔ service ↔ UI flow ↔ test.

### Must Have
- Cải thiện nền tảng frontend trước khi mở rộng capability mới.
- Giữ nguyên Angular 21 standalone architecture, không replatform.
- Ghi rõ mọi backend blocker/contract mismatch thay vì “ẩn” trong task frontend.
- Mọi acceptance criteria và QA đều agent-executable.
- Kế hoạch tối đa hóa song song sau khi các nền tảng chung được chốt.

### Must NOT Have (Guardrails)
- Không rewrite toàn bộ frontend hoặc đổi state library lớn chỉ vì cleanup.
- Không redesign toàn bộ visual identity/admin theme.
- Không mở rộng sang app ngoài `apps/admin`.
- Không âm thầm sửa business logic backend như một phần ngầm của task frontend.
- Không tạo bucket “cleanup chung chung”; mọi task phải gắn với pain point đã quan sát được.

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - Tất cả verification phải được thực thi bởi agent bằng command/tool. Không dùng tiêu chí kiểu “người dùng xác nhận đẹp/chạy đúng”.

### Quyết định test
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after
- **Framework**: Angular test tooling + Vitest + Playwright
- **Agent-Executed QA**: ALWAYS

### Chính sách QA
Mỗi task phải có ít nhất:
- 1 scenario happy path
- 1 scenario failure/edge path
- bằng command/tool cụ thể
- có evidence path tại `.omo/evidence/`

Áp dụng:
- **Frontend/UI**: Playwright
- **App/build/config**: Bash (`npm run build`, `npm run test:unit`, grep/read config)
- **API integration**: Bash/curl khi cần mock hoặc backend local sẵn sàng
- **Static verification**: grep/read cho route/service/config/pattern checks

---

## Execution Strategy

### Parallel Execution Waves

> Chiến lược: làm nền tảng chung trước để mở đường cho các wave capability chạy song song. Những task chạm shared infrastructure đi trước; task domain chạy song song theo capability.

```
Wave 1 (Nền tảng bắt buộc - bắt đầu ngay):
├── 1. Chuẩn hóa routing lazy-load cho feature pages [quick]
├── 2. Tách cấu hình API base URL khỏi runtime hard-code [quick]
├── 3. Chuẩn hóa service abstraction/BaseApiService [quick]
├── 4. Thiết kế error/auth handling tập trung cho 401/403/network [unspecified-high]
└── 5. Xác minh và khóa contract backend/frontend cho leaves + các blocker khác [deep]

Wave 2 (Capability core - sau Wave 1, tối đa song song):
├── 6. Hoàn thiện user management UI theo CRUD thực tế [unspecified-high]
├── 7. Hoàn thiện task management UI theo lifecycle đầy đủ [unspecified-high]
├── 8. Hoàn thiện leave management + leave balances admin UI [deep]
├── 9. Bổ sung permissions CRUD + departments directory [unspecified-high]
└── 10. Bổ sung attendance capability cho admin app [deep]

Wave 3 (Maintainability cleanup - sau Wave 2, song song theo module):
├── 11. Tách component lớn và chuẩn hóa page composition [quick]
├── 12. Chuẩn hóa async/loading/error state pattern [unspecified-high]
├── 13. Chuẩn hóa form strategy và validation rules [quick]
├── 14. Chuẩn hóa styling primitives và giảm copy-paste CSS [visual-engineering]
└── 15. Chuẩn hóa i18n copy, accessibility hooks và UX states [visual-engineering]

Wave 4 (Kiểm chứng chất lượng & hiệu năng - sau Wave 3):
├── 16. Mở rộng unit/integration coverage cho service/guard/component trọng yếu [quick]
├── 17. Mở rộng Playwright coverage cho capability mới và regression cũ [unspecified-high]
├── 18. Đo bundle/performance và chốt regression guard [quick]
└── 19. Rà soát screen-to-API coverage matrix và dọn dead paths [deep]

Wave FINAL (sau tất cả implementation tasks):
├── F1. Audit tuân thủ plan (oracle)
├── F2. Review chất lượng code/build/test (unspecified-high)
├── F3. QA thực chiến toàn flow admin (unspecified-high)
└── F4. Scope fidelity + contamination check (deep)
```

### Dependency Matrix
- **1**: - - 6, 7, 8, 9, 10, 18, 2
- **2**: - - 6, 7, 8, 9, 10, 18, 2
- **3**: - - 6, 7, 8, 9, 10, 12, 16, 2
- **4**: - - 6, 7, 8, 9, 10, 12, 15, 17, 2
- **5**: - - 8, 19, 2
- **6**: 1, 2, 3, 4 - 11, 12, 13, 17, 19, 3
- **7**: 1, 2, 3, 4 - 11, 12, 13, 17, 19, 3
- **8**: 1, 2, 3, 4, 5 - 11, 12, 13, 17, 19, 3
- **9**: 1, 2, 3, 4 - 11, 12, 13, 17, 19, 3
- **10**: 1, 2, 3, 4 - 11, 12, 13, 17, 19, 3
- **11**: 6, 7, 8, 9, 10 - 16, 17, 18, 19, 4
- **12**: 3, 4, 6, 7, 8, 9, 10 - 16, 17, 18, 19, 4
- **13**: 6, 7, 8, 9, 10 - 16, 17, 19, 4
- **14**: 6, 7, 8, 9, 10 - 17, 18, 19, 4
- **15**: 4, 6, 7, 8, 9, 10 - 17, 19, 4
- **16**: 3, 11, 12, 13 - F2, F3, 4
- **17**: 4, 6, 7, 8, 9, 10, 11, 12, 14, 15 - F2, F3, 4
- **18**: 1, 2, 11, 12, 14 - F2, 4
- **19**: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 - F1, F4, 4

### Agent Dispatch Summary
- **Wave 1**: 5 task — 1/2/3 → `quick`, 4 → `unspecified-high`, 5 → `deep`
- **Wave 2**: 5 task — 6/7/9 → `unspecified-high`, 8/10 → `deep`
- **Wave 3**: 5 task — 11/13 → `quick`, 12 → `unspecified-high`, 14/15 → `visual-engineering`
- **Wave 4**: 4 task — 16/18 → `quick`, 17 → `unspecified-high`, 19 → `deep`
- **FINAL**: 4 task — F1 → `oracle`, F2/F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. `app.routes.ts`: Chuyển feature routes sang lazy-load để giảm initial bundle - expect route tree tách tải theo màn hình

  **What to do**:
  - Đổi các route feature từ `component:` sang `loadComponent:` cho các page admin chính.
  - Giữ nguyên shell route, guards và system routes.
  - Xác minh bundle/route loading không phá login, permission guard, hoặc redirect.

  **Must NOT do**:
  - Không đổi business logic route.
  - Không chạm backend.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: thay đổi routing cấu hình, phạm vi gọn nhưng ảnh hưởng bundle.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: cần xác định route dependency và shell flow hiện tại.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 6, 7, 8, 9, 10, 18, 19
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/app.routes.ts:20-112` - route tree hiện tại cần được lazy-load hóa.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:305-365` - shell/breadcrumb metadata phải tiếp tục hoạt động.

  **WHY Each Reference Matters**:
  - Routes là nơi đang eager-load toàn bộ feature component.
  - Shell metadata cho biết việc lazy-load không được làm hỏng breadcrumb/title.

  **Acceptance Criteria**:
  - [ ] Các feature page ưu tiên được lazy-load bằng `loadComponent`.
  - [ ] `npm run build` vẫn pass.
  - [ ] Login, unauthorized, forbidden và dashboard vẫn hoạt động.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Route feature lazy-load vẫn mở đúng
    Tool: Playwright
    Preconditions: `npm run dev` đang chạy
    Steps:
      1. Mở `http://127.0.0.1:4200/login`
      2. Đăng nhập bằng `admin@company.vn` / `Admin@123`
      3. Điều hướng tới `/users`
    Expected Result: page users load thành công, không redirect sai, shell vẫn hiển thị breadcrumb/title đúng
    Failure Indicators: blank screen, route error, shell không render
    Evidence: .omo/evidence/task-1-users-lazy-load.png

  Scenario: Guard route vẫn chặn đúng sau lazy-load
    Tool: Playwright
    Preconditions: token không hợp lệ hoặc chưa đăng nhập
    Steps:
      1. Mở trực tiếp `/config/menu-sync`
      2. Quan sát redirect
    Expected Result: chuyển tới `/unauthorized`
    Evidence: .omo/evidence/task-1-guard-redirect.png
  ```

- [x] 2. `app.config.ts`: Tách API base URL sang environment/runtime config - expect không hard-code endpoint runtime

  **What to do**:
  - Thay `API_BASE_URL` hard-code bằng environment hoặc runtime config.
  - Giữ local dev, test và production có thể cấu hình riêng.
  - Cập nhật provider/injection để service đọc một nguồn cấu hình duy nhất.

  **Must NOT do**:
  - Không phá local dev.
  - Không sửa backend để bù cho frontend config.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: refactor cấu hình, phạm vi nhỏ, lợi ích lớn.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 6, 7, 8, 9, 10, 18
  - **Blocked By**: None

  **References**:
  - `apps/admin/src/app/app.config.ts:28-45` - provider hiện hard-code URL.
  - `apps/admin/README.md` - local dev backend 8010 là baseline cần giữ được.

  **Acceptance Criteria**:
  - [ ] Không còn hard-code `http://127.0.0.1:8010` trong runtime app config.
  - [ ] Build/test/dev start vẫn pass.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Runtime config được đọc đúng ở local dev
    Tool: Bash
    Preconditions: app chạy ở local
    Steps:
      1. Khởi động frontend
      2. Kiểm tra app gọi API qua base URL cấu hình
    Expected Result: request đi tới backend được cấu hình, không dính hard-code trong source chính
    Evidence: .omo/evidence/task-2-runtime-config.txt

  Scenario: Sai config bị phát hiện sớm
    Tool: Bash
    Preconditions: đặt base URL sai trong config test/dev
    Steps:
      1. Chạy build hoặc test
      2. Quan sát lỗi kết nối
    Expected Result: lỗi cấu hình được lộ ra rõ ràng, không im lặng
    Evidence: .omo/evidence/task-2-bad-config.txt
  ```

- [x] 3. `services/*`: Chuẩn hóa BaseApiService và các service kế thừa - expect không còn cast workaround API URL

  **What to do**:
  - Thống nhất cách build URL trong `BaseApiService`.
  - Loại bỏ pattern `as unknown as { apiBaseUrl: string }`.
  - Làm cho các service kế thừa dùng cùng một đường đi `get/post/put/delete`.

  **Must NOT do**:
  - Không đổi endpoint contract backend.
  - Không sinh thêm wrapper không cần thiết.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: refactor service layer hẹp nhưng ảnh hưởng nhiều files.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: cần map caller/callee của service base.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 6, 7, 8, 9, 10, 12, 16, 19
  - **Blocked By**: 2

  **References**:
  - `apps/admin/src/app/services/base-api.service.ts:10-27` - base abstraction hiện tại.
  - `apps/admin/src/app/services/user-api.service.ts:17-55` - workaround buildUrl/cast.
  - `apps/admin/src/app/services/task-api.service.ts:17-52` - cùng pattern workaround.

  **Acceptance Criteria**:
  - [ ] Không còn cast workaround truy cập `apiBaseUrl`.
  - [ ] Các service chính dùng cùng một abstraction để tạo URL.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Service gọi endpoint qua base abstraction mới
    Tool: Bash
    Preconditions: source đã refactor
    Steps:
      1. Tìm cast workaround trong services
      2. Xác nhận không còn pattern đó
    Expected Result: không match chuỗi cast workaround
    Evidence: .omo/evidence/task-3-service-abstraction.txt

  Scenario: API call vẫn hoạt động sau refactor
    Tool: Playwright
    Preconditions: app đã đăng nhập
    Steps:
      1. Mở users/tasks list
      2. Quan sát dữ liệu tải về
    Expected Result: dữ liệu load bình thường
    Evidence: .omo/evidence/task-3-api-flow.png
  ```

- [x] 4. `core/`: Thiết kế error/auth handling tập trung cho 401/403/network - expect redirect và feedback nhất quán

  **What to do**:
  - Bổ sung/cải tổ interceptor hoặc error handler chung.
  - Xử lý 401/403 theo chuẩn thống nhất.
  - Chuẩn hóa message hiển thị khi API/network fail.

  **Must NOT do**:
  - Không làm thay đổi logic bảo mật backend.
  - Không nuốt lỗi im lặng.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: logic cross-cutting, ảnh hưởng auth/UX toàn app.
  - **Skills**: [`gitnexus-debugging`]
    - `gitnexus-debugging`: phù hợp để rà lỗi runtime/flow auth.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 6, 7, 8, 9, 10, 16, 17
  - **Blocked By**: 2, 3

  **References**:
  - `apps/admin/src/app/core/interceptors/auth.interceptor.ts:6-20` - interceptor hiện chỉ gắn header.
  - `apps/admin/src/app/core/guards/auth.guard.ts:6-12` - auth redirect flow.
  - `apps/admin/src/app/core/guards/permission.guard.ts:6-18` - permission redirect flow.

  **Acceptance Criteria**:
  - [ ] Khi API trả 401 trong route bảo vệ, app redirect về `/unauthorized` hoặc `/login` theo quyết định implementation được ghi rõ trong code/tests.
  - [ ] Khi API trả 403 trong route có permission guard, app render `/forbidden` hoặc message permission-denied đã được test bằng Playwright.
  - [ ] Khi request list/mutation thất bại do network, page hiển thị một thông báo lỗi quan sát được trong DOM hoặc toast loggable, không silent fail.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Token hết hạn bị redirect đúng
    Tool: Playwright
    Preconditions: token lỗi hoặc hết hạn
    Steps:
      1. Reload app
      2. Điều hướng vào route bảo vệ
    Expected Result: redirect về login/unauthorized theo chuẩn đã chọn
    Evidence: .omo/evidence/task-4-401-redirect.png

  Scenario: Network failure hiển thị error message
    Tool: Playwright
    Preconditions: backend không phản hồi
    Steps:
      1. Mở một page load dữ liệu
      2. Chờ request fail
    Expected Result: hiển thị message lỗi rõ ràng
    Evidence: .omo/evidence/task-4-network-error.png
  ```

- [x] 5. `leaves` contract: Xác minh và khóa lại review/approve/reject + blocker phụ thuộc backend - expect contract đúng trước khi mở rộng UI

  **What to do**:
  - Đối chiếu route backend với service/frontend hiện tại.
  - Xác nhận chính xác contract review của leaves và các endpoint liên quan.
  - Ghi lại blocker nếu backend/front contract cần đồng bộ trước khi làm UI chi tiết.

  **Must NOT do**:
  - Không tự ý bịa contract mới.
  - Không implement UI mới khi contract còn mơ hồ.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: cần đối chiếu contract và flow thực tế kỹ lưỡng.
  - **Skills**: [`gitnexus-exploring`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: 8, 19
  - **Blocked By**: 2, 3, 4

  **References**:
  - `app/presentation/api/v1/leaves.py` - backend routes leaves.
  - `apps/admin/src/app/services/leave-api.service.ts:17-49` - frontend leave service hiện tại.
  - `apps/admin/src/app/features/leaves/leaves-page.component.ts:134-194` - UI actions hiện có.

  **Acceptance Criteria**:
  - [ ] Có mapping contract leaves rõ ràng giữa backend và frontend.
  - [ ] Nêu rõ blocker nếu route/action nào chưa khớp.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Contract mapping được xác minh
    Tool: Bash
    Preconditions: source/backend sẵn sàng
    Steps:
      1. So khớp endpoint service với backend route
      2. Ghi nhận mismatch nếu có
    Expected Result: contract matrix rõ ràng
    Evidence: .omo/evidence/task-5-leaves-contract.md

  Scenario: Mismatch bị báo cáo thay vì ngầm bỏ qua
    Tool: Bash
    Preconditions: phát hiện endpoint không khớp
    Steps:
      1. Đánh dấu mismatch
      2. Ghi blocker vào plan/task note
    Expected Result: blocker được ghi rõ
    Evidence: .omo/evidence/task-5-leaves-mismatch.md
  ```

- [x] 6. `features/users`: Hoàn thiện user management UI theo CRUD thực tế - expect create/edit/delete/detail flow đầy đủ

  **What to do**:
  - Thêm luồng create/edit/delete/detail user theo backend endpoints.
  - Giữ lại activate/deactivate và reset password.
  - Bổ sung filter hợp lý nếu phục vụ thao tác quản trị.

  **Must NOT do**:
  - Không đổi rule auth/permission.
  - Không phá list/filter hiện có.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: page quản trị có nhiều hành động và trạng thái.
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 16, 17, 19
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - `app/presentation/api/v1/users.py` - full CRUD backend.
  - `apps/admin/src/app/services/user-api.service.ts:17-55` - service hiện có.
  - `apps/admin/src/app/features/users/users-page.component.ts:27-199` - UI hiện tại.

  **Acceptance Criteria**:
  - [ ] Có UI cho create/edit/detail/delete user.
  - [ ] Activate/deactivate/reset password vẫn hoạt động.
  - [ ] `npm run e2e` có scenario users mới.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Tạo và chỉnh sửa user thành công
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở users page
      2. Tạo user mới với dữ liệu hợp lệ
      3. Mở user vừa tạo và sửa một trường
    Expected Result: user xuất hiện trong danh sách và cập nhật đúng
    Evidence: .omo/evidence/task-6-users-crud.png

  Scenario: Delete user bị chặn với thao tác xác nhận/hợp lệ
    Tool: Playwright
    Preconditions: có user mục tiêu
    Steps:
      1. Nhấn delete
      2. Hủy confirm hoặc thử xóa user không hợp lệ
    Expected Result: thao tác an toàn, không xóa nhầm, lỗi hiển thị rõ nếu bị chặn
    Evidence: .omo/evidence/task-6-users-delete-guard.png
  ```

- [x] 7. `features/tasks`: Hoàn thiện task management UI theo lifecycle đầy đủ - expect assign/create/detail/edit/delete flow

  **What to do**:
  - Thêm UI cho create/edit/detail/assign/delete task.
  - Giữ các action start/complete/cancel.
  - Bổ sung filter nếu cần theo assignee/department/status.

  **Must NOT do**:
  - Không phá flow hiện có.
  - Không đổi contract backend task trừ khi blocker đã ghi rõ.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: nghiệp vụ task có nhiều action và trạng thái.
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 16, 17, 19
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - `app/presentation/api/v1/tasks.py` - backend task lifecycle.
  - `apps/admin/src/app/services/task-api.service.ts:17-52` - service hiện có.
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts:35-173` - UI hiện có.

  **Acceptance Criteria**:
  - [ ] Có UI cho create/edit/assign/delete/detail task.
  - [ ] Start/complete/cancel vẫn hoạt động.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Tạo và assign task thành công
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở tasks page
      2. Tạo task mới
      3. Assign task cho user hợp lệ
    Expected Result: task xuất hiện và trạng thái/assignee đúng
    Evidence: .omo/evidence/task-7-task-lifecycle.png

  Scenario: Cancel task từ trạng thái hợp lệ
    Tool: Playwright
    Preconditions: task ở pending/in_progress
    Steps:
      1. Bấm cancel
      2. Xác nhận modal
    Expected Result: task chuyển trạng thái đúng, không lỗi UI
    Evidence: .omo/evidence/task-7-task-cancel.png
  ```

- [x] 8. `features/leaves` + `leave-balances`: Hoàn thiện leave management và leave balance admin UI - expect detail, cancel, balance view/edit

  **What to do**:
  - Đưa leave workflow thành UI đầy đủ hơn: list/detail/review/cancel/edit nếu contract cho phép.
  - Thêm bề mặt cho leave balances: xem số dư theo user/năm và chỉnh số dư nếu backend cho phép.
  - Đồng bộ lại tên action với contract thực tế.

  **Must NOT do**:
  - Không tự bịa action review nếu backend contract chưa chốt.
  - Không che mismatch bằng code “giả vờ” hoạt động.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: domain nghiệp vụ và contract có khả năng mismatch.
  - **Skills**: [`gitnexus-exploring`, `playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 16, 17, 19
  - **Blocked By**: 1, 2, 3, 4, 5

  **References**:
  - `app/presentation/api/v1/leaves.py` - endpoint lifecycle.
  - `app/presentation/api/v1/leave_balances.py` - balance endpoints.
  - `apps/admin/src/app/services/leave-api.service.ts:17-49` - service hiện tại.
  - `apps/admin/src/app/features/leaves/leaves-page.component.ts:35-194` - UI hiện có.

  **Acceptance Criteria**:
  - [ ] Có UI cho leave balance xem/chỉnh hoặc blocker note rõ ràng nếu backend chưa cho phép.
  - [ ] UI leave route/actions khớp contract đã xác minh.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Xem leave balance theo user/năm
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở leave balance UI
      2. Chọn user và năm
    Expected Result: balance hiển thị đúng dữ liệu
    Evidence: .omo/evidence/task-8-leave-balance.png

  Scenario: Reject/cancel flow hiển thị lỗi khi contract chưa khớp
    Tool: Playwright
    Preconditions: endpoint không khớp hoặc backend trả lỗi
    Steps:
      1. Thử thao tác review/cancel
      2. Quan sát lỗi
    Expected Result: lỗi hiển thị rõ, không silent fail
    Evidence: .omo/evidence/task-8-leave-error.png
  ```

- [x] 9. `features/rbac` + `features/system`: Bổ sung permissions CRUD và departments directory - expect access-control and org reference screens

  **What to do**:
  - Mở rộng permissions UI sang create/edit/delete nếu backend hỗ trợ.
  - Thêm departments directory/read-only list làm nguồn tham chiếu tổ chức.
  - Giữ roles/permissions navigation rõ ràng.

  **Must NOT do**:
  - Không làm rộng RBAC sang redesign toàn bộ authorization model.
  - Không thêm quy tắc phân quyền mới ngoài contract hiện có.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: tác động trực tiếp tới access control và org structure.
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 12, 16, 17, 19
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - `app/presentation/api/v1/permissions.py` - permissions CRUD.
  - `app/presentation/api/v1/departments.py` - departments list.
  - `apps/admin/src/app/features/rbac/permissions-page.component.ts` - current permission UI.
  - `apps/admin/src/app/features/rbac/roles-page.component.ts` - role management UI.

  **Acceptance Criteria**:
  - [ ] Permission CRUD UI tồn tại hoặc ghi blocker rõ ràng.
  - [ ] Departments directory có page/service hoặc ghi blocker rõ ràng.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Permission list/create/edit/delete flow
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở permissions page
      2. Tạo hoặc sửa một permission hợp lệ
    Expected Result: permission xuất hiện/cập nhật đúng
    Evidence: .omo/evidence/task-9-permission-crud.png

  Scenario: Departments directory loads safely
    Tool: Playwright
    Preconditions: backend accessible
    Steps:
      1. Mở departments directory page
      2. Kiểm tra list render
    Expected Result: danh sách departments hiển thị hoặc empty state rõ ràng
    Evidence: .omo/evidence/task-9-departments.png
  ```

- [x] 10. `features/attendance`: Bổ sung attendance capability cho admin app - expect service/page khớp đúng các endpoint attendance hiện có

  **What to do**:
  - Tạo service/page cho attendance dựa trên endpoint backend hiện có.
  - Hiển thị dữ liệu từ `GET /api/v1/attendance/heatmap` theo hình thức phù hợp với response thực tế sau khi inspect contract.
  - Chỉ thêm thao tác check-in/check-out hoặc filter nếu backend contract hiện có hỗ trợ rõ ràng; nếu không, ghi blocker.

  **Must NOT do**:
  - Không giả định backend contract khác khi chưa xác minh.
  - Không làm UI chỉ “trưng bày” nếu không gắn được vào data thật.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: domain mới hoàn toàn trong frontend admin.
  - **Skills**: [`gitnexus-exploring`, `playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: 11, 12, 16, 17, 19
  - **Blocked By**: 1, 2, 3, 4

  **References**:
  - `app/presentation/api/v1/attendance.py` - backend attendance domain.
  - `apps/admin/src/app/app.routes.ts` - route map hiện chưa có attendance.

  **Acceptance Criteria**:
  - [ ] Có service/page attendance hoặc blocker note rõ ràng nếu backend contract chưa đủ.
  - [ ] Có thể load/hiển thị dữ liệu attendance thực hoặc state rỗng rõ ràng.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Attendance overview hiển thị dữ liệu
    Tool: Playwright
    Preconditions: backend có dữ liệu attendance
    Steps:
      1. Mở attendance page
      2. Chọn bộ lọc user/date
    Expected Result: dữ liệu từ endpoint attendance render thành bảng/list/visual phù hợp với response thực tế; nếu contract không đủ thì blocker hiển thị rõ
    Evidence: .omo/evidence/task-10-attendance-overview.png

  Scenario: Backend lỗi được xử lý trên attendance page
    Tool: Playwright
    Preconditions: backend fail hoặc endpoint thiếu
    Steps:
      1. Mở attendance page
      2. Quan sát trạng thái lỗi
    Expected Result: error state/message rõ ràng
    Evidence: .omo/evidence/task-10-attendance-error.png
  ```

- [x] 11. `features/*`: Tách component lớn và chuẩn hóa page composition - expect component dễ bảo trì hơn

  **What to do**:
  - Tách các page lớn theo ngưỡng hợp lý: template/style/helpers/subcomponents.
  - Ưu tiên admin shell, users, roles, tasks, leaves.
  - Giữ behavior và selector test hiện có.

  **Must NOT do**:
  - Không refactor lan man ngoài page lớn.
  - Không đổi UI behavior chỉ vì tách file.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: refactor cơ học có kiểm soát theo component.
  - **Skills**: [`gitnexus-refactoring`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 16, 17, 18, 19
  - **Blocked By**: 6, 7, 8, 9, 10

  **References**:
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts` - shell lớn.
  - `apps/admin/src/app/features/users/users-page.component.ts` - page all-in-one.
  - `apps/admin/src/app/features/rbac/roles-page.component.ts` - page phức tạp.

  **Acceptance Criteria**:
  - [ ] Các component lớn được tách hoặc có rationale giữ nguyên.
  - [ ] Existing data-testid vẫn hoạt động.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Users page giữ behavior sau refactor
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở `/users`
      2. Dùng filter active/inactive
    Expected Result: table filter đúng như trước
    Evidence: .omo/evidence/task-11-users-refactor.png

  Scenario: Shell vẫn render đúng sau tách component
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở dashboard
      2. Toggle sidebar
    Expected Result: sidebar/header/breadcrumb hoạt động
    Evidence: .omo/evidence/task-11-shell-refactor.png
  ```

- [x] 12. `shared/state`: Chuẩn hóa async/loading/error state pattern - expect giảm lặp code fetch/mutate

  **What to do**:
  - Nhận diện repeated pattern `loading/saving/firstValueFrom/try-catch`.
  - Tạo helper/facade nhẹ hoặc convention thống nhất.
  - Áp dụng cho các page đã mở rộng ở Wave 2.

  **Must NOT do**:
  - Không đưa state library mới nếu không có lý do bắt buộc.
  - Không over-abstract các flow đơn giản.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: refactor cross-page cần cân bằng abstraction.
  - **Skills**: [`gitnexus-refactoring`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 16, 17, 18, 19
  - **Blocked By**: 3, 4, 6, 7, 8, 9, 10

  **References**:
  - `apps/admin/src/app/features/users/users-page.component.ts:144-193` - load/mutate pattern.
  - `apps/admin/src/app/features/tasks/tasks-page.component.ts` - task action pattern.
  - `apps/admin/src/app/shared/components/sync-resource-panel.component.ts` - reusable async flow tốt để học pattern.

  **Acceptance Criteria**:
  - [ ] Ít nhất users, tasks, leaves, notifications và sync panel dùng chung convention loading/error đã chốt.
  - [ ] Không còn catch rỗng hoặc catch không phân loại ở các flow mới được thêm trong plan.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Loading state thống nhất trên list page
    Tool: Playwright
    Preconditions: backend phản hồi chậm hoặc mock delay
    Steps:
      1. Mở users/tasks page
      2. Quan sát loading indicator
    Expected Result: loading hiển thị và tắt đúng
    Evidence: .omo/evidence/task-12-loading-state.png

  Scenario: Mutation error không bị silent fail
    Tool: Playwright
    Preconditions: API mutation trả lỗi
    Steps:
      1. Thử action update/delete
      2. Quan sát message lỗi
    Expected Result: lỗi hiển thị rõ ràng
    Evidence: .omo/evidence/task-12-mutation-error.png
  ```

- [x] 13. `forms`: Chuẩn hóa form strategy và validation rules - expect reactive/template-driven không lẫn lộn vô tội vạ

  **What to do**:
  - Chọn convention form cho create/edit/reset flows.
  - Bổ sung validation tối thiểu cho password, required fields, email, select IDs.
  - Giữ login form hiện có làm reference cho reactive form nếu phù hợp.

  **Must NOT do**:
  - Không thêm validation tùy tiện trái backend.
  - Không đổi UX form cũ nếu không cần.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: chuẩn hóa form theo màn hình, rõ acceptance.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 16, 17, 19
  - **Blocked By**: 6, 7, 8, 9, 10

  **References**:
  - `apps/admin/src/app/features/auth/login-page.component.ts:103-130` - reactive form baseline.
  - `apps/admin/src/app/features/users/users-page.component.ts:180-194` - reset password validation hiện nông.
  - `apps/admin/src/app/features/rbac/roles-page.component.ts` - create/manage form patterns.

  **Acceptance Criteria**:
  - [ ] Form mới có validation rõ ràng và disabled/error states.
  - [ ] Các input quan trọng có testable selectors hoặc accessible labels.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Form create user chặn dữ liệu thiếu
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Mở create user form
      2. Submit khi thiếu email/password/name
    Expected Result: form không submit và hiển thị lỗi field
    Evidence: .omo/evidence/task-13-user-validation.png

  Scenario: Form hợp lệ submit thành công
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Nhập dữ liệu hợp lệ
      2. Submit form
    Expected Result: API được gọi và UI cập nhật
    Evidence: .omo/evidence/task-13-valid-submit.png
  ```

- [x] 14. `styles/shared`: Chuẩn hóa styling primitives và giảm copy-paste CSS - expect visual consistency dựa trên reusable classes/tokens

  **What to do**:
  - Gom các pattern lặp: page-root, page-header, eyebrow, subtitle, cards, table states.
  - Giảm inline CSS copy-paste ở các feature pages.
  - Hạn chế `::ng-deep`/`!important` nếu có thể thay bằng theme/class rõ ràng.

  **Must NOT do**:
  - Không redesign toàn bộ visual identity.
  - Không thay NG Zorro/Tailwind stack.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: liên quan visual consistency và CSS architecture.
  - **Skills**: [`frontend-ui-ux`, `visual-qa`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 17, 18, 19
  - **Blocked By**: 6, 7, 8, 9, 10

  **References**:
  - `apps/admin/src/styles.css:1-2` - global style entry.
  - `apps/admin/src/app/features/users/users-page.component.ts:101-122` - repeated page CSS.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:103-275` - shell styles.

  **Acceptance Criteria**:
  - [ ] Các pattern `page-root`, `page-header`, `eyebrow`, `subtitle`, `filter-card`, `table-card` được gom vào primitive dùng chung hoặc được thay bằng convention file/class có tài liệu rõ.
  - [ ] Screenshot users, tasks, leaves và roles trước/sau thay đổi không có sai khác bố cục nghiêm trọng (header lệch, card vỡ, table unreadable).

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Users/tasks/leaves pages giữ layout nhất quán
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Chụp screenshot users/tasks/leaves
      2. So sánh header/card/table layout
    Expected Result: layout không vỡ và primitives thống nhất
    Evidence: .omo/evidence/task-14-visual-consistency.png

  Scenario: Dark table contrast vẫn đọc được
    Tool: Playwright
    Preconditions: page có bảng dữ liệu
    Steps:
      1. Mở roles/users table
      2. Kiểm tra text visible
    Expected Result: text đủ tương phản, không bị màu trùng nền
    Evidence: .omo/evidence/task-14-table-contrast.png
  ```

- [x] 15. `i18n/a11y`: Chuẩn hóa copy, accessibility hooks và UX states - expect ngôn ngữ/keyboard/error states nhất quán hơn

  **What to do**:
  - Chọn convention copy tiếng Việt/Anh cho admin app và áp dụng cho flow chính.
  - Thêm accessible labels cho icon buttons/action buttons.
  - Bổ sung empty/error states cho list pages.

  **Must NOT do**:
  - Không triển khai full i18n framework nếu chưa cần.
  - Không dịch bừa business terms chưa rõ.

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: UX text, accessibility, page states.
  - **Skills**: [`frontend-ui-ux`, `visual-qa`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: 17, 19
  - **Blocked By**: 4, 6, 7, 8, 9, 10

  **References**:
  - `apps/admin/src/app/features/auth/login-page.component.ts:17-50` - mixed copy.
  - `apps/admin/src/app/layouts/admin-shell/admin-shell.component.ts:46-86` - shell copy/actions.
  - `apps/admin/src/app/features/users/users-page.component.ts:83-87` - icon action buttons.

  **Acceptance Criteria**:
  - [ ] Mọi icon/action button quan trọng có accessible name/label rõ ràng trong DOM.
  - [ ] Ít nhất users, tasks, leaves và notifications có empty state và error state quan sát được.
  - [ ] Copy language convention cho admin flow chính được ghi thành quy ước trong plan/task note và được áp dụng nhất quán ở các màn hình mới chỉnh.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Keyboard user thao tác action chính
    Tool: Playwright
    Preconditions: admin đăng nhập
    Steps:
      1. Tab tới action button trong users table
      2. Kích hoạt bằng Enter/Space
    Expected Result: focus visible và action hoạt động
    Evidence: .omo/evidence/task-15-keyboard-actions.png

  Scenario: Empty state hiển thị rõ
    Tool: Playwright
    Preconditions: filter trả về rỗng
    Steps:
      1. Chọn filter không có dữ liệu
      2. Quan sát table/page state
    Expected Result: empty state rõ ràng, không blank confusing
    Evidence: .omo/evidence/task-15-empty-state.png
  ```

- [x] 16. `tests/unit`: Mở rộng unit/integration coverage cho service/guard/component trọng yếu - expect regression logic được khóa

  **What to do**:
  - Thêm tests cho auth/error interceptor, service abstraction, guards, form validation, critical helpers.
  - Dựa trên test style hiện có.
  - Không test implementation details quá mức.

  **Must NOT do**:
  - Không viết snapshot mơ hồ không có giá trị.
  - Không bỏ qua failing tests bằng skip.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: test bổ sung theo scope rõ.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F2, F3
  - **Blocked By**: 3, 11, 12, 13

  **References**:
  - `apps/admin/src/app/services/auth-store.service.spec.ts` - service spec pattern.
  - `apps/admin/src/app/core/guards/auth.guard.spec.ts` - guard test pattern.
  - `apps/admin/src/app/app.spec.ts` - app smoke test.

  **Acceptance Criteria**:
  - [ ] Unit tests mới pass.
  - [ ] Critical service/guard/form logic có coverage.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Unit suite pass
    Tool: Bash
    Preconditions: dependencies installed
    Steps:
      1. Chạy `npm run test:unit`
    Expected Result: tất cả tests pass
    Evidence: .omo/evidence/task-16-unit-tests.txt

  Scenario: Interceptor/guard negative cases được test
    Tool: Bash
    Preconditions: test files mới tồn tại
    Steps:
      1. Chạy targeted test cho guard/interceptor
    Expected Result: 401/403/unauthorized paths pass
    Evidence: .omo/evidence/task-16-auth-tests.txt
  ```

- [x] 17. `e2e`: Mở rộng Playwright coverage cho capability mới và regression cũ - expect admin workflows được verify bằng browser

  **What to do**:
  - Thêm Playwright tests cho users/tasks/leaves/attendance/departments/permissions theo capability triển khai.
  - Giữ regression login, permission route, sync flow.
  - Capture evidence cho happy/error paths.

  **Must NOT do**:
  - Không tạo e2e phụ thuộc thứ tự chạy mong manh.
  - Không hard-code dữ liệu không seed được.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: browser QA cần setup/test data/flow cẩn thận.
  - **Skills**: [`playwright`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F2, F3
  - **Blocked By**: 4, 6, 7, 8, 9, 10, 11, 12, 14, 15

  **References**:
  - `apps/admin/e2e/admin.spec.ts` - existing Playwright style.
  - `apps/admin/README.md` - local backend/test fixture accounts.

  **Acceptance Criteria**:
  - [ ] E2E suite có coverage cho capability mới hoặc blocker note rõ nếu backend data chưa sẵn.
  - [ ] `npm run e2e` pass trong môi trường local documented.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Regression e2e hiện có vẫn pass
    Tool: Bash
    Preconditions: backend/frontend running theo README
    Steps:
      1. Chạy `npm run e2e`
    Expected Result: tests pass
    Evidence: .omo/evidence/task-17-e2e-regression.txt

  Scenario: Capability mới có browser happy path
    Tool: Playwright
    Preconditions: test data seeded
    Steps:
      1. Mở capability page mới
      2. Thực hiện action chính
    Expected Result: UI cập nhật đúng và không lỗi console nghiêm trọng
    Evidence: .omo/evidence/task-17-new-capability.png
  ```

- [x] 18. `build/performance`: Đo bundle/performance và chốt regression guard - expect initial bundle warning được xử lý có chủ đích

  **What to do**:
  - Chạy build production và ghi lại bundle sau lazy loading.
  - Nếu vẫn vượt budget, phân tích nguyên nhân còn lại: global CSS, NG Zorro, icons, shared chunks.
  - Cập nhật budget hoặc tối ưu với rationale rõ.

  **Must NOT do**:
  - Không tăng budget để che vấn đề nếu chưa phân tích.
  - Không remove library tùy tiện.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: đo/build/analyze bundle có command rõ.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F2
  - **Blocked By**: 1, 2, 11, 12, 14

  **References**:
  - `apps/admin/package.json:4-13` - build command.
  - `apps/admin/angular.json` - budget config nếu cần kiểm tra.
  - `apps/admin/src/styles.css:1-2` - global CSS imports.

  **Acceptance Criteria**:
  - [ ] Có before/after bundle report.
  - [ ] Build pass không warning hoặc warning được xử lý bằng rationale/budget hợp lý.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Production build pass và bundle được ghi nhận
    Tool: Bash
    Preconditions: dependencies installed
    Steps:
      1. Chạy `npm run build`
      2. Lưu output bundle sizes
    Expected Result: build pass, bundle report có số liệu
    Evidence: .omo/evidence/task-18-build-bundle.txt

  Scenario: Không có eager feature import ngoài chủ đích
    Tool: Bash
    Preconditions: route lazy-load đã áp dụng
    Steps:
      1. Kiểm tra `app.routes.ts`
      2. Tìm import trực tiếp feature page còn lại
    Expected Result: chỉ còn eager imports có chủ đích
    Evidence: .omo/evidence/task-18-eager-import-check.txt
  ```

- [x] 19. `coverage-matrix`: Rà soát screen-to-API coverage và dọn dead paths - expect backlog/API/UI trạng thái rõ ràng

  **What to do**:
  - Tạo matrix cuối: backend endpoint/domain → frontend service → route/page → UI action → test.
  - Đánh dấu fully covered/partial/missing/blocker.
  - Dọn hoặc ghi chú các path/service không còn dùng.

  **Must NOT do**:
  - Không coi endpoint backend nào cũng bắt buộc phải có UI nếu domain cố ý không expose admin.
  - Không xóa dead path nếu chưa chứng minh không dùng.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: cần synthesis toàn repo giữa backend routes và frontend UI.
  - **Skills**: [`gitnexus-exploring`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4
  - **Blocks**: F1, F4
  - **Blocked By**: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15

  **References**:
  - `app/presentation/api/v1/*.py` - backend API surface.
  - `apps/admin/src/app/services/*.ts` - frontend service surface.
  - `apps/admin/src/app/app.routes.ts` - visible route/page surface.

  **Acceptance Criteria**:
  - [ ] Matrix cuối có đầy đủ domain chính.
  - [ ] Mọi partial/missing đều có lý do hoặc follow-up rõ.

  **QA Scenarios (MANDATORY)**:
  ```
  Scenario: Coverage matrix sinh ra đầy đủ
    Tool: Bash
    Preconditions: source tree hiện tại
    Steps:
      1. Liệt kê backend routes
      2. Liệt kê frontend services/routes
      3. Ghi matrix coverage
    Expected Result: matrix có covered/partial/missing/blocker
    Evidence: .omo/evidence/task-19-coverage-matrix.md

  Scenario: Dead path không bị xóa nhầm
    Tool: Bash
    Preconditions: phát hiện route/service nghi ngờ dead
    Steps:
      1. Tìm references của route/service
      2. Ghi quyết định giữ/xóa/blocker
    Expected Result: không xóa khi còn reference
    Evidence: .omo/evidence/task-19-dead-path-check.md
  ```

---

## Final Verification Wave

> 4 review agents chạy song song sau khi tất cả implementation task hoàn tất. Không được tự đánh dấu hoàn thành trước khi có kết quả review và user okay.

- [x] F1. **Audit tuân thủ plan**

  **What to do**:
  - Đọc plan end-to-end và đối chiếu với các thay đổi thực tế trong `apps/admin`.
  - Kiểm tra tất cả Must Have có hiện diện và Must NOT Have không bị vi phạm.
  - Đối chiếu coverage matrix giữa backend contract, service layer, route/page, và test.
  - Kiểm tra evidence files của từng task trong `.omo/evidence/`.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần review đa chiều trên plan, diff, file tree, evidence.
  - **Skills**: `[]`
  - **Skills Evaluated but Omitted**:
    - `gitnexus-impact-analysis`: không cần vì đây là verification tổng thể, không phải phân tích blast radius trước edit.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F2, F3, F4)
  - **Blocks**: Hoàn tất verification cuối
  - **Blocked By**: 16, 17, 18, 19

  **Acceptance Criteria**:
  - [ ] Có báo cáo `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT`
  - [ ] Mọi sai lệch đều có file/path cụ thể

- [x] F2. **Review chất lượng code/build/test**

  **What to do**:
  - Chạy build/test/lint liên quan trong `apps/admin`.
  - Soát các file thay đổi để tìm pattern xấu: workaround cast, empty catch, dead import, commented code, hard-coded config mới.
  - Xác nhận service abstraction đã thống nhất.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần kết hợp command verification và code review thực dụng.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F3, F4)
  - **Blocks**: Hoàn tất verification cuối
  - **Blocked By**: 16, 17, 18

  **Acceptance Criteria**:
  - [ ] `npm run build` pass
  - [ ] `npm run test:unit` pass
  - [ ] Không còn pattern cast URL workaround trong service layer admin

- [x] F3. **QA thực chiến toàn flow admin**

  **What to do**:
  - Chạy đầy đủ Playwright và QA scenarios của các task.
  - Kiểm tra regression của login, permission routing, sync flows, và capability mới.
  - Kiểm tra negative cases: unauthorized, forbidden, network/API error, empty states.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: cần chạy hệ thống thật theo end-to-end flows.
  - **Skills**: [`playwright`]
    - `playwright`: bắt buộc để xác thực browser flows và capture evidence.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F4)
  - **Blocks**: Hoàn tất verification cuối
  - **Blocked By**: 16, 17, 15

  **Acceptance Criteria**:
  - [ ] Có báo cáo `Scenarios [N/N pass] | Integration [N/N] | Edge Cases [N tested] | VERDICT`
  - [ ] Evidence lưu tại `.omo/evidence/final-qa/`

- [x] F4. **Scope fidelity + contamination check**

  **What to do**:
  - Kiểm tra từng task trong plan so với diff thực tế.
  - Xác định có task nào làm quá scope, chạm file không liên quan, hoặc bỏ sót deliverable.
  - Xác định backend blockers có bị “lén xử lý” ngoài phạm vi guardrail hay không.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: cần reasoning chặt về phạm vi và dependency contamination.
  - **Skills**: [`gitnexus-exploring`]
    - `gitnexus-exploring`: hữu ích để map flow/symbol/file liên quan trong phạm vi admin.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave FINAL (with F1, F2, F3)
  - **Blocks**: Hoàn tất verification cuối
  - **Blocked By**: 19

  **Acceptance Criteria**:
  - [ ] Có báo cáo `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `refactor(admin): harden routing config and api access` — routing, config, service abstraction, auth/error infra
- **Wave 2**: `feat(admin): expand operational capabilities` — users/tasks/leaves/attendance/departments/permissions theo nhóm nhỏ nếu cần tách commit
- **Wave 3**: `refactor(admin): standardize component state form and styling` — cleanup có kiểm soát theo page groups
- **Wave 4**: `test(admin): expand coverage and performance guards` — tests, Playwright, performance checks

---

## Success Criteria

### Verification Commands
```bash
cd /home/pdat/Documents/master-operation/apps/admin && npm run build
# Expected: build PASS, initial bundle không vượt budget hoặc có rationale/config update được chấp nhận

cd /home/pdat/Documents/master-operation/apps/admin && npm run test:unit
# Expected: tất cả unit tests PASS

cd /home/pdat/Documents/master-operation/apps/admin && npm run e2e
# Expected: regression + capability mới PASS

cd /home/pdat/Documents/master-operation && grep -R "127.0.0.1:8010" apps/admin/src/app || true
# Expected: không còn hard-code runtime API base URL trong app config chính

cd /home/pdat/Documents/master-operation && grep -R "as unknown as { apiBaseUrl: string }" apps/admin/src/app/services || true
# Expected: không còn cast workaround trong service layer
```

### Final Checklist
- [x] Tất cả Must Have hiện diện
- [x] Tất cả Must NOT Have vắng mặt
- [x] Không còn route feature ưu tiên bị eager-load ngoài chủ đích
- [x] Capability attendance/departments/leave balances được giải quyết theo plan (triển khai hoặc blocker note rõ ràng)
- [x] User/task/leave/permission workflows được mở rộng đúng với backend contract hoặc blocker note rõ ràng
- [x] Tests và QA evidence đầy đủ
