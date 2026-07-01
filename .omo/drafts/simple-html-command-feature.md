# Draft: Simple HTML-to-Command Feature Ideas

## Requirements (confirmed)
- User wants a new feature/use case for the project.
- The feature should be simple so the user can operate it manually.
- The flow should minimize HTML-to-backend data transmission.
- User prefers a solution that can be triggered via commands.

## Technical Decisions
- Module Document sẽ là backend CRUD thuần, là nguồn dữ liệu chuẩn cho file gốc và metadata.
- File gốc sẽ lưu ở MinIO, DB chỉ lưu metadata và object key/bucket.
- RAG/indexing sẽ là consumer: đọc Document từ DB, tải file từ MinIO, rồi parse/chunk/embed/index.
- Kế hoạch viết bằng tiếng Việt, chia phase nhỏ để người dùng tự code.

## Research Findings
- Upload/index hiện tại trong `app/presentation/api/v1/agentic/router.py` đang đọc file vào memory nhưng không lưu file gốc vào storage chuẩn.
- `AgenticDocumentModel` hiện liên quan đến agentic/RAG; không nên xóa toàn bộ ngay, nên xây Document CRUD riêng rồi nối indexing sau.
- MinIO phù hợp làm object store cho file gốc trước khi RAG xử lý.

## Open Questions
- What exact user action should this feature support?
- Is the target interaction form submission, file upload, search/filter, or command execution?
- What data must be sent from HTML, and what must stay client-side?
- Should the feature be purely terminal/CLI-based, or web UI + command hybrid?

## Scope Boundaries
- INCLUDE: A lightweight, easy-to-use feature with minimal HTML payload.
- EXCLUDE: Complex workflows, multi-step approvals, or heavy frontend/backend coupling for now.
