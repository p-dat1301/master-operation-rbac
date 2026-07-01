# Kế hoạch xây dựng module Document CRUD + MinIO + RAG indexing

## TL;DR
> Xây một module Document thuần backend theo hướng CRUD trước, lưu file gốc vào MinIO, rồi nối pipeline index/RAG vào kho Document đó.
>
> **Deliverables**:
> - Module Document CRUD backend tách biệt rõ với RAG
> - Tích hợp lưu file gốc vào MinIO
> - Luồng index/chunk/embed đọc từ Document store
> - Bộ kiểm chứng để bạn tự chạy từng phase
>
> **Ước lượng**: Medium
> **Thực thi song song**: YES - 4 waves
> **Critical Path**: Thiết kế domain Document → lưu file MinIO → CRUD API → index pipeline → RAG đọc dữ liệu

---

## Context

### Yêu cầu gốc
- Người dùng muốn làm một module Document riêng, backend CRUD thuần.
- RAG chỉ đọc dữ liệu từ kho Document đó để index và trả lời.
- File gốc cần lưu vào MinIO.
- Document phải có access policy rõ ràng ngay từ domain.
- Chỉ `admin` / `manager` được upload, còn người upload sẽ chọn phạm vi xem tài liệu.
- Kế hoạch phải viết bằng tiếng Việt và chia phase nhỏ để tự viết mã.

### Access policy đã chốt
- Quyền upload: chỉ `admin` và `manager`.
- Phạm vi xem tài liệu: `public`, `company`, `department`, `role`, `owner`, `manager_subtree`.
- Field quyền cần có trong domain Document:
  - `uploaded_by`
  - `owner_id`
  - `visibility_scope`
  - `allowed_role_names`
  - `allowed_department_ids`
  - `classification`
- **Quyết định sau eng review**: MVP dùng policy denormalized trong bảng `documents`, evaluate trong Document service/use case. Không tách bảng ACL riêng ở MVP.
- **Guardrail**: cùng một hàm/utility policy phải được dùng cho list/detail/retrieval để tránh leak quyền do mỗi nơi tự filter khác nhau.

### Tóm tắt trao đổi
- Role CRUD đã tồn tại; không nên phá vỡ module agentic hiện tại ngay lập tức.
- Upload document hiện nay đang trộn lẫn với indexing/RAG, nên cần tách trách nhiệm.
- Hiện tượng upload không index được là do file chưa được lưu đúng nơi trước khi parser chạy.
- Hướng mong muốn: Document là nguồn dữ liệu chuẩn, RAG là consumer.
- **Quyết định sau eng review**:
  - Giữ nguyên scope CRUD + MinIO + indexing + RAG cutover.
  - Indexing ở MVP chạy sync trước để giảm moving parts.
  - Migration sẽ cutover dứt điểm sau MVP, không dual-write dài hạn.
  - Test policy phải là full matrix, không chỉ happy path.

### Phát hiện kỹ thuật
- Hệ thống hiện có nhánh `agentic` cho upload/index/chunk/retrieval.
- Upload route hiện đọc file vào memory nhưng không có kho file gốc chuẩn.
- MinIO là đích lưu file gốc hợp lý để Document store quản lý file, RAG đọc lại từ đó.

---

## Mục tiêu công việc

### Mục tiêu cốt lõi
Tạo một module Document backend độc lập, lưu file gốc vào MinIO, quản lý metadata bằng CRUD, và cung cấp nguồn dữ liệu ổn định để pipeline index/RAG tiêu thụ.

### Deliverables cụ thể
- API CRUD cho Document.
- Bảng/ORM/model cho Document với access policy.
- Tích hợp MinIO để lưu file gốc.
- Luồng index đọc file từ Document store/MinIO.
- Tài liệu vận hành tối thiểu để tự kiểm thử.

### Định nghĩa hoàn thành
- [ ] Có thể tạo document và upload file vào MinIO bằng API.
- [ ] Có thể xem danh sách/chi tiết/sửa/xóa Document bằng API.
- [ ] Pipeline index đọc file từ kho Document thay vì phụ thuộc flow upload cũ.
- [ ] RAG/chunk/index hoạt động với file đã lưu trong MinIO.

### Bắt buộc phải có
- Document là nguồn dữ liệu chuẩn cho file gốc.
- MinIO là nơi lưu file gốc.
- RAG chỉ tiêu thụ dữ liệu từ Document store, không sở hữu dữ liệu gốc.
- Access policy phải nằm ngay trong domain Document.
- Kế hoạch phải chia nhỏ theo phase để có thể tự code từng bước.

### Không được làm
- Không giữ nguyên kiến trúc upload cũ như nguồn chính.
- Không để RAG vừa là nơi upload vừa là nơi lưu trữ chính.
- Không trộn CRUD nghiệp vụ với pipeline index.
- Không làm quá nhiều abstraction ngay từ đầu.

## Tích hợp framework đặc tả
- Không phát hiện SDD framework chuyên dụng trong ngữ cảnh này.
- Nếu sau này repo có OpenSpec/Spec Kit, có thể bổ sung map vào plan.

---

## Chiến lược kiểm chứng

### Quyết định test
- **Hạ tầng test hiện có**: Có
- **Test tự động**: Tests-after
- **Framework**: pytest
- **Chiến lược**: Mỗi phase có kiểm chứng bằng test hoặc chạy API/command trực tiếp

### Chính sách QA
Mỗi phase phải có bước kiểm chứng do agent thực thi bằng lệnh/API.

- Backend/API: dùng `pytest` hoặc `curl`
- File/MinIO: kiểm tra object đã được ghi đúng bucket/key
- RAG/index: chạy pipeline và xác nhận output/chunks/embeddings

---

## Chiến lược thực thi

### Tổng quan wave
- **Wave 1**: Thiết kế domain và storage nền tảng
- **Wave 2**: CRUD Document + upload file vào MinIO
- **Wave 3**: Tích hợp index pipeline vào kho Document
- **Wave 4**: Rà soát, harden, và hoàn tất luồng RAG tiêu thụ dữ liệu

---

## TODOs

- [ ] 1. Xác định mô hình dữ liệu Document và ranh giới với RAG

  **Mục tiêu phase**:
  - Chốt Document là source of truth.
  - Chốt dữ liệu nào thuộc CRUD, dữ liệu nào thuộc indexing.
  - Tránh để `agentic_documents` tiếp tục đóng vai trò kho dữ liệu gốc.

  **Bạn cần tự viết**:
  - Phác thảo entity `Document` với các field tối thiểu:
    - `id`
    - `title`
    - `description`
    - `storage_bucket`
    - `storage_object_key`
    - `original_filename`
    - `mime_type`
    - `size_bytes`
    - `status`
    - `created_at`
    - `updated_at`
  - Bổ sung access policy ngay từ domain:
    - `uploaded_by`
    - `owner_id`
    - `visibility_scope`
    - `allowed_role_names`
    - `allowed_department_ids`
    - `classification`
  - Ghi rõ ranh giới:
    - CRUD module quản lý metadata + file gốc.
    - RAG module quản lý chunks/embeddings/index.

  **Kết quả đầu ra mong đợi**:
  - Có một mô tả ngắn về entity Document.
  - Có danh sách field bắt buộc và field tùy chọn.
  - Có quyết định rõ: không dùng `agentic_documents` làm bảng CRUD chính.

  **Tự kiểm chứng**:
  -vào.
  - Lưu access policy đủ để kiểm tra quyền  Bạn có thể giải thích bằng 3 câu:
    1. Document lưu gì?
    2. MinIO lưu gì?
    3. RAG lưu gì?

- [ ] 2. Thiết kế schema DB cho module Document

  **Mục tiêu phase**:
  - Tạo bảng dữ liệu riêng cho CRUD document.
  - Chuẩn bị nền để MinIO và indexing bám xem theo role/department/company/public.

  **Bạn cần tự viết**:
  - Tạo model/bảng `documents` riêng.
  - Nếu cần, thêm enum hoặc string status như: `draft`, `uploaded`, `indexing`, `indexed`, `failed`.
  - Thêm field access policy:
    - `uploaded_by`: user id người upload.
    - `owner_id`: người sở hữu document; MVP có thể bằng `uploaded_by`.
    - `visibility_scope`: một trong `public`, `company`, `department`, `role`, `owner`, `manager_subtree`.
    - `allowed_role_names`: JSON/JSONB list string, dùng khi scope là `role`.
    - `allowed_department_ids`: JSON/JSONB list int, dùng khi scope là `department`.
    - `classification`: một trong `public`, `internal`, `confidential`, `restricted`.
  - Viết migration cho bảng `documents`.
  - Thêm index cho các cột hay query nhiều như `status`, `created_at`, `visibility_scope`, `uploaded_by`, `owner_id`.

  **Kết quả đầu ra mong đợi**:
  - Bảng `documents` tồn tại độc lập.
  - Không phụ thuộc trực tiếp vào `agentic_documents`.
  - Có chỗ lưu `storage_bucket` và `storage_object_key` để truy xuất file từ MinIO.
  - Có đủ field access policy để RAG filter quyền sau này.

  **Tự kiểm chứng**:
  - Chạy migration thành công.
  - Query thử DB thấy bảng `documents` có đủ cột đã thiết kế.
  - Tạo thử record với `visibility_scope = role` và `allowed_role_names = ["manager"]`.
  - Tạo thử record với `visibility_scope = department` và `allowed_department_ids = [1]`.

- [ ] 3. Chuẩn bị cấu hình MinIO và contract lưu trữ file

  **Mục tiêu phase**:
  - Có cơ chế lưu file gốc chuẩn vào object storage.
  - Tránh việc parser phụ thuộc vào `file.filename` như hiện tại.

  **Bạn cần tự viết**:
  - Thêm config cần thiết cho MinIO trong settings/env, ví dụ:
    - `MINIO_ENDPOINT`
    - `MINIO_ACCESS_KEY`
    - `MINIO_SECRET_KEY`
    - `MINIO_BUCKET`
    - `MINIO_SECURE`
  - Viết một adapter/service nhỏ cho MinIO với các hàm tối thiểu:
    - upload object
    - get object / download stream
    - delete object
    - check bucket tồn tại
  - Quy ước object key, ví dụ: `documents/{document_id}/{original_filename}`.

  **Kết quả đầu ra mong đợi**:
  - Có nơi duy nhất chịu trách nhiệm giao tiếp với MinIO.
  - Object key được chuẩn hóa ngay từ đầu.

  **Tự kiểm chứng**:
  - Chạy thử upload một file mẫu lên MinIO.
  - Dùng MinIO console hoặc SDK để xác nhận object đã tồn tại đúng bucket/key.

- [ ] 4. Viết use case Create Document + upload file vào MinIO

  **Mục tiêu phase**:
  - Hoàn thiện đường đi cốt lõi: nhận file → kiểm tra quyền upload → lưu MinIO → lưu metadata DB.

  **Bạn cần tự viết**:
  - API tạo Document có nhận multipart file.
  - Chặn upload nếu actor không phải `admin` hoặc `manager`.
  - Nhận thêm access policy từ form/body:
    - `visibility_scope`
    - `allowed_role_names`
    - `allowed_department_ids`
    - `classification`
  - Validation tối thiểu:
    - filename hợp lệ
    - mime type được hỗ trợ
    - size limit
    - nếu `visibility_scope = role` thì `allowed_role_names` không được rỗng
    - nếu `visibility_scope = department` thì `allowed_department_ids` không được rỗng
    - nếu `visibility_scope = public/company/owner` thì không bắt buộc role/department
  - Logic:
    1. xác thực actor là `admin` hoặc `manager`
    2. sinh `document_id`
    3. upload file vào MinIO
    4. lưu metadata + access policy vào bảng `documents`
    5. trả response chứa thông tin document
  - Nếu upload MinIO fail thì không commit metadata nửa chừng.

  **Kết quả đầu ra mong đợi**:
  - Có endpoint tạo Document hoạt động.
  - File gốc xuất hiện trong MinIO.
  - DB có metadata khớp với object vừa upload.
  - DB có access policy khớp lựa chọn khi upload.

  **Tự kiểm chứng**:
  - Gọi API create document bằng Postman/curl với actor `manager` hoặc `admin`.
  - Thử actor `employee` upload và phải bị từ chối.
  - Kiểm tra record trong DB.
  - Kiểm tra object trong MinIO.

- [ ] 5. Hoàn thiện Read/List Document

  **Mục tiêu phase**:
  - Có thể xem danh sách và chi tiết Document mà không đụng tới pipeline RAG.

  **Bạn cần tự viết**:
  - Endpoint list documents.
  - Endpoint get document detail.
  - Response trả đúng metadata cần thiết cho frontend/admin, bao gồm access policy.
  - Nếu cần, thêm phân trang đơn giản và filter theo `status`, `visibility_scope`, `classification`.

  **Kết quả đầu ra mong đợi**:
  - Có thể xem document vừa upload.
  - Không cần dùng bảng `agentic_documents` để render danh sách CRUD.

  **Tự kiểm chứng**:
  - Gọi API list thấy record mới tạo.
  - Gọi API detail theo `document_id` thấy đúng bucket/key, filename, mime type, status.
  - Kiểm tra response có `visibility_scope`, `allowed_role_names`, `allowed_department_ids`, `classification`.

- [ ] 6. Hoàn thiện Update Document

  **Mục tiêu phase**:
  - Cho phép chỉnh sửa metadata nghiệp vụ mà không phá file gốc.

  **Bạn cần tự viết**:
  - Endpoint update cho các field nên cho sửa, ví dụ: `title`, `description`, `status hiển thị`.
  - Xác định rõ field nào không được sửa trực tiếp, ví dụ: `storage_object_key`, `size_bytes`.
  - Nếu thay file gốc là một use case khác, chưa nên trộn ngay trong phase này.

  **Kết quả đầu ra mong đợi**:
  - Có thể đổi title/description an toàn.
  - Không làm sai metadata storage.

  **Tự kiểm chứng**:
  - Gọi API update.
  - Gọi lại detail thấy field đã đổi.
  - Kiểm tra object trên MinIO không bị thay đổi ngoài ý muốn.

- [ ] 7. Hoàn thiện Delete Document

  **Mục tiêu phase**:
  - Xóa Document theo một quy tắc nhất quán.

  **Bạn cần tự viết**:
  - Chọn chiến lược xóa:
    - soft delete trước, hoặc
    - hard delete ngay.
  - Nếu hard delete:
    - xóa object khỏi MinIO
    - xóa metadata DB
    - xóa/đánh dấu dữ liệu index liên quan
  - Nếu soft delete:
    - đánh dấu DB
    - chặn RAG sử dụng document đã xóa

  **Kết quả đầu ra mong đợi**:
  - Delete có quy tắc rõ và không để dữ liệu mồ côi.

  **Tự kiểm chứng**:
  - Xóa một document thử.
  - Kiểm tra DB.
  - Kiểm tra object trong MinIO.
  - Kiểm tra document không còn xuất hiện trong list.

- [ ] 8. Tạo use case Index Document tách khỏi CRUD

  **Mục tiêu phase**:
  - Biến indexing thành bước xử lý sau CRUD, không còn là upload flow chính.

  **Bạn cần tự viết**:
  - Một use case/service kiểu `index_document(document_id)`.
  - Flow đề xuất:
    1. đọc metadata document từ DB
    2. lấy file từ MinIO
    3. kiểm tra access policy của document để quyết định tài liệu nào được index/phục vụ
    4. tạo file tạm local hoặc stream phù hợp cho parser
    5. parse document
    6. normalize/chunk
    7. embed/index
    8. cập nhật `index_status`
  - Quyết định chạy sync hay async:
    - trước mắt có thể sync để đơn giản
    - sau này tách job queue nếu cần

  **Kết quả đầu ra mong đợi**:
  - Indexing có thể chạy độc lập chỉ với `document_id`.
  - Không phụ thuộc route upload cũ.
  - Access policy được carry theo document để filter khi retrieval.

  **Tự kiểm chứng**:
  - Gọi hàm/endpoint index cho document đã tồn tại.
  - Kiểm tra chunks/embeddings/index được tạo.
  - Kiểm tra `index_status` cập nhật đúng.

- [ ] 9. Nối RAG đọc từ kho Document mới thay vì upload flow cũ

  **Mục tiêu phase**:
  - Chuyển vai trò RAG về đúng vị trí consumer.

  **Bạn cần tự viết**:
  - Thay chỗ nào trong pipeline đang giả định upload trực tiếp thì chuyển sang lấy từ `documents`.
  - Nếu cần giữ tương thích tạm thời, tạo adapter trung gian map `Document` → contract mà parser/indexing cũ cần.
  - Đảm bảo chat/retrieval chỉ dùng dữ liệu đã được index từ kho Document.
  - Khi retrieval, lọc theo access policy của user hiện tại:
    - cùng role nếu scope là `role`
    - cùng department nếu scope là `department`
    - toàn công ty nếu scope là `company`
    - public nếu scope là `public`
    - owner/manager subtree nếu scope tương ứng

  **Kết quả đầu ra mong đợi**:
  - RAG không cần endpoint upload riêng để sở hữu dữ liệu gốc nữa.
  - Document CRUD trở thành đầu vào chuẩn cho indexing.
  - Evidence trả về từ RAG không vượt quyền xem tài liệu.

  **Tự kiểm chứng**:
  - Tạo document mới.
  - Chạy index.
  - Thực hiện truy vấn chat/RAG và xác nhận có thể truy xuất document đó.
  - Thử user không đủ quyền và phải không thấy tài liệu đó trong kết quả.

- [ ] 10. Quy hoạch chuyển đổi dần khỏi module agentic document cũ

  **Mục tiêu phase**:
  - Không đập bỏ code cũ ngay, mà di trú an toàn.

  **Bạn cần tự viết**:
  - Gắn cờ những phần cũ sẽ deprecated.
  - Quyết định phần nào giữ tạm để tránh gãy frontend/chat hiện hữu.
  - Nếu có endpoint cũ `POST /api/v1/agentic/documents`, quyết định:
    - đổi sang gọi Document CRUD mới, hoặc
    - khóa endpoint cũ sau khi migration xong.

  **Kết quả đầu ra mong đợi**:
  - Có lộ trình chuyển đổi an toàn.
  - Không cần xóa toàn bộ code cũ ở bước đầu.

  **Tự kiểm chứng**:
  - Liệt kê rõ những phần cũ: giữ, thay thế, xóa sau.
  - Xác nhận không có route mới nào lại đi vòng về upload flow cũ.

- [ ] 11. Bổ sung test và checklist vận hành tối thiểu

  **Mục tiêu phase**:
  - Tự tin rằng module Document hoạt động độc lập trước khi mở rộng.

  **Bạn cần tự viết**:
  - Test cho create/list/detail/update/delete document.
  - Test cho upload MinIO thành công/thất bại.
  - Test cho index document từ kho MinIO.
  - Checklist manual tối thiểu:
    1. upload file
    2. thấy metadata DB
    3. thấy object MinIO
    4. chạy index
    5. truy vấn RAG ra được dữ liệu

  **Kết quả đầu ra mong đợi**:
  - Có test bao phủ happy path.
  - Có ít nhất 1-2 case lỗi chính: MinIO fail, parser fail.

  **Tự kiểm chứng**:
  - Chạy `pytest`.
  - Chạy một kịch bản end-to-end bằng API.

---

## Final Verification Wave

- F1. Kiểm tra plan bám đúng yêu cầu Document CRUD + MinIO + RAG
- F2. Kiểm tra tính hợp lý của phase, phụ thuộc và khả năng tự viết mã
- F3. Kiểm tra tiêu chí kiểm chứng, không cần người test thủ công
- F4. Kiểm tra scope không bị trộn với module agentic cũ

---

## Chiến lược commit

- 1: `docs(plan): document crud minio rag`

---

## Hướng dẫn chạy

- Khi bạn muốn bắt đầu thực thi, hãy chạy `/start-work`.
- Plan này đã tách theo phase nhỏ để bạn có thể code từng bước mà không phải viết lại toàn bộ module cùng lúc.
- Nếu muốn, trước khi chạy `/start-work` bạn có thể yêu cầu mình chỉnh lại field Document, cách đặt tên bucket/object key, hoặc mức độ chi tiết của từng phase.

---

## Tiêu chí thành công

### Lệnh kiểm chứng
```bash
pytest
```

### Checklist cuối
- [ ] Document CRUD hoạt động
- [ ] File lưu vào MinIO
- [ ] Index pipeline đọc từ kho Document
- [ ] RAG không còn phụ thuộc vào upload flow cũ
