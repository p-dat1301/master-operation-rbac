# Kế hoạch triển khai Agentic RAG theo Pipeline

## TL;DR

> **Tóm tắt nhanh**: Xây dựng hệ thống Agentic RAG theo kiến trúc **pipeline-first**, dùng **LangGraph cố định ở orchestration layer**, bắt đầu với ingestion tài liệu **PDF text-based + DOCX**, có **phân quyền dữ liệu theo role/scope** ngay tại retrieval-time, và giữ các thành phần như **LLM / embeddings / vector DB / parser / storage** ở dạng **adapter có thể thay thế**.
>
> **Deliverables chính**:
> - Bộ contract lõi cho document / chunk / access policy / answer / graph state
> - Pipeline ingest → parse → normalize → chunk → policy tag → index → retrieve → answer → audit
> - LangGraph workflow cố định cho luồng query
> - Session memory ngắn hạn bằng Redis cho hội thoại nhiều lượt, có TTL, chỉ dùng làm context phụ trợ và không thay thế retrieval/citation
> - LangSmith observability layer để trace/debug/evaluate LangGraph flow mà không thay audit log nội bộ
> - Adapter boundary rõ ràng để đổi model, embedding, vector DB, parser, storage, cache/session store mà không viết lại core flow
> - Lộ trình triển khai **tuần tự từng module**, không xây song song nhiều module
>
> **Ước lượng**: Large
> **Chiến lược thực thi**: Tuần tự theo pipeline
> **Critical Path**: Contracts → ingestion → parsing → chunking → access control → indexing → retrieval → LangGraph orchestration → answer generation → audit → extension boundary

---

## Bối cảnh

### Yêu cầu gốc
Người dùng muốn triển khai một hệ thống agentic RAG cho dự án này theo hướng **flow/pipeline**, không ưu tiên Clean Architecture cho AI module. Hệ thống cần dễ mở rộng về sau, nhưng giai đoạn đầu chỉ cần hỗ trợ tài liệu **DOCX và PDF**, đồng thời phải dễ thay đổi framework / tech stack ở các thành phần như model, embeddings, vector DB, parser, storage.

### Quyết định kiến trúc đã chốt
- **Giữ cố định LangGraph** vì đây là framework orchestration phù hợp và phổ biến nhất cho agentic workflow.
- **Không cố định** các thành phần còn lại như:
  - model provider
  - embedding provider
  - vector database
  - parser implementation
  - storage backend
- **Không đi theo Clean Architecture đầy đủ** cho AI module.
- **Vẫn phải có boundary rõ** để tránh lock-in vào vendor/framework không cần thiết.
- **Tổ chức code theo pipeline stage**, không theo CRUD/layer truyền thống.

### Kết luận từ bước tư vấn
- V1 chỉ hỗ trợ **PDF text-based + DOCX**.
- **OCR, XLSX, PPTX, Notion, Confluence, DB/API records** là extension về sau.
- **Deny-by-default** khi access policy không đủ rõ.
- **Không cho LLM nhìn thấy chunk không được phép**.
- Câu trả lời phải **có citation** hoặc **trả về insufficient evidence / insufficient permission / unsupported scope**.
- Mục tiêu là **hoàn thành module trước rồi mới sang module tiếp theo**.

---

## Mục tiêu công việc

### Mục tiêu cốt lõi
Thiết kế và triển khai một hệ thống Agentic RAG theo pipeline, trong đó:
- ingestion tài liệu đi qua các stage rõ ràng,
- LangGraph đảm nhiệm orchestration cho luồng truy vấn,
- phân quyền dữ liệu được áp dụng trước khi evidence vào model,
- các adapter hạ tầng có thể thay thế mà không phá core flow.

### Deliverables cụ thể
- Cấu trúc code chuẩn cho module `app/agentic/`
- Contract lõi cho source / document / chunk / access policy / answer / audit / graph state
- Pipeline ingest tài liệu PDF/DOCX
- Chunking + citation metadata propagation
- Access control ở retrieval-time
- Indexing + retrieval có filter theo quyền
- LangGraph query flow cố định
- Session memory ngắn hạn bằng Redis cho multi-turn context, TTL và context summary
- Answer generation có citation
- Audit logging nội bộ cho compliance/security
- LangSmith observability cho tracing/debug/evaluation của LangGraph flow
- Extension boundary cho future sources, future adapters và future memory stores

### Định nghĩa hoàn thành
- [ ] PDF text-based và DOCX đi hết pipeline từ source → answer → audit
- [ ] Retrieval chặn đúng dữ liệu không được phép trước khi build context cho model
- [ ] Answer luôn có citation hoặc trả lời từ chối / thiếu bằng chứng rõ ràng
- [ ] Có thể thay model/vector DB/parser/storage qua adapter/config mà không sửa core pipeline
- [ ] MVP chỉ triển khai một default concrete adapter cho từng capability; provider-specific adapters khác được defer sau MVP
- [ ] LangGraph được dùng cố định ở orchestration layer, không lan khắp business logic

### Bắt buộc phải có
- Triển khai **tuần tự theo module**
- LangGraph là **framework orchestration cố định**
- Kiến trúc **pipeline-first**
- PDF/DOCX là source đầu tiên
- Access control ở retrieval-time
- Citation bắt buộc trong answer
- Audit log nội bộ cho ingest / retrieve / deny
- LangSmith tracing cho dev observability, có redaction và không thay audit log nội bộ
- Adapter boundary cho các tech stack có thể thay thế

### Tuyệt đối không được có
- Không xây song song nhiều module lớn
- Không để business logic phụ thuộc trực tiếp vào vendor cụ thể như OpenAI/Qdrant/S3
- Không để LangGraph node chứa toàn bộ business logic
- Không để parser PDF/DOCX rò vào contract lõi
- Không cho unauthorized chunk đi vào LLM context
- Không mở rộng quá scope sang OCR / XLSX / PPTX / Notion / Confluence / DB/API records trong MVP
- Không triển khai DB tool / reporting tool / action-history lookup trong MVP
- Không gửi raw restricted content / PII lên LangSmith trace mặc định
- Không dùng LangSmith thay audit log nội bộ

---

## Kiến trúc code đề xuất

### Nguyên tắc tổ chức
Kiến trúc code phải là:

> **Pipeline-oriented modular architecture with LangGraph as orchestration spine and replaceable adapters for model/vector DB/parser/storage/session memory**

### Cây thư mục mục tiêu
```text
app/
  agentic/
    contracts/
      document.py
      chunk.py
      source.py
      access_policy.py
      retrieval.py
      answer.py
      audit.py
      graph_state.py
      memory.py

    memory/
      memory_policy.py
      session_memory.py
      memory_summary.py

    adapters/
      session/
        base.py
        redis_session_store.py

    ingestion/
      ingest_source.py
      source_registry.py
      checksum.py

    parsing/
      parser_registry.py
      parse_document.py
      normalize_document.py

    chunking/
      chunk_config.py
      chunk_document.py

    access_control/
      resolve_policy.py
      evaluate_access.py
      build_retrieval_filter.py

    indexing/
      index_document.py
      index_status.py

    retrieval/
      evidence_bundle.py
      retrieve_evidence.py
      rerank.py

    generation/
      citation_policy.py
      generate_answer.py
      prompts.py

    audit/
      log_rag_event.py

    observability/
      langsmith_config.py
      trace_helpers.py
      run_metadata.py
      redaction.py

    orchestration/
      graph_state.py
      rag_graph.py
      nodes/
        load_user_context.py
        classify_query.py
        route_query.py
        retrieve_evidence.py
        validate_policy.py
        generate_answer.py
        deny_request.py
        audit_event.py


    adapters/
      parsers/
        base.py
        pdf_parser.py
        docx_parser.py
      llm/
        base.py
        default_llm.py
      embeddings/
        base.py
        default_embeddings.py
      vector_store/
        base.py
        default_vector_store.py
      storage/
        base.py
        local_storage.py
```

### Quy tắc dependency
- `contracts/` là lõi ổn định
- `ingestion/ parsing/ chunking/ access_control/ indexing/ retrieval/ generation/ audit/ memory/` dùng contract lõi
- `orchestration/` gọi các module pipeline để tạo flow LangGraph
- `observability/` cấu hình LangSmith tracing/redaction/run metadata, không chứa business rule và không thay audit nội bộ
- `adapters/` chỉ implement tech cụ thể, không chứa business rule
- MVP chỉ có **1 concrete adapter mặc định cho mỗi capability**: LLM, embeddings, vector store, storage, session store (Redis), parser.

### Quy tắc memory
- **Session memory chỉ là context phụ trợ**, không phải evidence và không thay thế retrieval-time authorization.
- **Redis chỉ dùng cho short-lived session memory / cache / lock / buffer**, không là source of truth cho audit và không thay thế vector DB chính trong v1.
- **Session memory phải có TTL rõ ràng** và giới hạn số turn / kích thước summary.
- MVP default session-store adapter: Redis.
- **Cache key và session key phải permission-aware**: tối thiểu gồm `user_id` hoặc `tenant_id`, `role_names`, `department_id`, `policy_version`, `index_version`, `session_id` khi phù hợp.
- **Session memory không được bypass citation**: mọi factual answer vẫn phải đi qua retrieval và evidence bundle hợp lệ.
- **Không lưu raw restricted content lâu dài trong memory layer mặc định**.
- **DB/tool layer không thuộc MVP**.
- **Khi triển khai sau MVP**, DB/tool layer phải read-only, whitelist-based, không gọi raw SQL trực tiếp từ graph/node và phải đi qua use case/query service.

### Quy tắc LangGraph
- **LangGraph là fixed choice**
- Nhưng LangGraph chỉ sống ở `app/agentic/orchestration/`
- Business logic phải nằm ở các module pipeline
- Node LangGraph chỉ là lớp điều phối mỏng

### Quy tắc chọn adapter cho MVP
- Chỉ chọn **một concrete adapter mặc định cho mỗi capability**: parser, LLM, embeddings, vector store, storage, session store.
- **Embedding model và answer LLM phải là hai adapter tách biệt**; không dùng chung config/interface cho hai mục đích này.
- Ưu tiên adapter local/dev-friendly hoặc adapter đơn giản nhất phù hợp dependency thực tế của repo.
- Nếu repo chưa có dependency provider-specific rõ ràng, dùng tên `default_*` cho concrete adapter thay vì hard-code vendor trong plan.
- Provider-specific adapters bổ sung (OpenAI/Anthropic/Qdrant/Weaviate/S3/MinIO...) được defer sau MVP.
- Executor phải chốt một implementation concrete duy nhất trước khi bắt đầu Task 7/9/10; không mở rộng thành multi-provider matrix trong MVP.

### Token Budget / Counting Policy
- Token counting là bắt buộc ở **3 stage**: chunking-time, embedding-time, query-time / generation-time.
- Chunking phải lưu `token_count` và `chunker_version`; token-aware splitting ưu tiên hơn character-based splitting.
- Embedding adapter phải validate token budget trước khi gửi chunk/query vào embedding model.
- Query/generation phải có context budget manager: `query tokens + memory summary tokens + retrieved evidence tokens + output reserve tokens`.
- Khi vượt budget, ưu tiên truncate/re-split ở ingestion; query-time thì giảm số evidence chunks hoặc rerank lại.
- Tokenizer mặc định của MVP phải được chốt theo model default adapter và ghi rõ trong task tương ứng.

### Model Strategy / Auxiliary Model Policy
- **Answer LLM** dùng cho answer generation, deny/no-evidence response và follow-up rewrite nếu cần.
- **Embedding model** dùng riêng cho document chunk embedding và query embedding.
- **Auxiliary model** (nếu có) chỉ dùng cho query classification / memory summarization / routing; không tạo factual answer.
- Token budget, output budget và latency budget phải cấu hình riêng cho từng loại model.
- Đổi embedding model không được ảnh hưởng answer generation, và ngược lại.

### Retrieval / Rerank / Citation Policy
- Retrieval v1 dùng metadata filter + vector search trước khi build evidence; access policy phải được re-check trước expose.
- `top_k`, similarity threshold, max evidence tokens và filter ordering phải config được.
- Rerank MVP là rule-based/lightweight; không dùng LLM reranker trong v1.
- Citation chỉ hợp lệ nếu reference tới `chunk_id` / `document_id` / page-or-section metadata tồn tại trong authorized evidence bundle.
- Không chấp nhận citation do LLM tự bịa; answer post-processor phải validate citation ids trước khi trả response.
- Nếu evidence không trực tiếp support answer, trả `insufficient_evidence`; nếu query ngoài corpus, trả `unsupported_scope`.

### Data Lifecycle / Versioning / Security Policy
- Mỗi document/index phải có version để hỗ trợ re-index idempotent và invalidation an toàn.
- Retrieval filter phải include `policy_version` và `index_version`; session memory stale phải bị bỏ qua.
- Prompt builder chỉ nhận authorized evidence; không gửi raw restricted content hoặc PII vào prompt/telemetry mặc định.
- Error taxonomy phải bao phủ: unsupported source / unsupported mime / parse failed / OCR required / policy denied / insufficient evidence / embedding failed / vector store unavailable / LLM unavailable.
- Config strategy phải rõ: `answer_model_name`, `embedding_model_name`, `chunk_max_tokens`, `retrieval_top_k`, `retrieval_score_threshold`, `max_context_tokens`, `session_ttl_seconds`, `langsmith_enabled`.
- Phải có eval/fixture strategy để kiểm thử deny/leak/no-evidence cases bằng dataset cố định.

---

## Quy tắc gợi ý file theo từng bước

> Không tạo trước toàn bộ file map. Executor chỉ xem phần **Gợi ý file cho bước này** trong task đang làm. Nếu repo đã có file tương đương, ưu tiên mở rộng file hiện có thay vì tạo trùng tên.

---

## Chiến lược kiểm thử

> **Không yêu cầu user test tay.** Mọi xác nhận phải agent-executed.

### Quyết định test
- **Hạ tầng test riêng cho AI pipeline**: chưa có sẵn
- **Chiến lược**: tests-after + QA scenario cụ thể cho từng module
- **Nguyên tắc**:
  - test độc lập từng module
  - test integration theo pipeline stage
  - test end-to-end cho graph flow
  - test authorization leak

### Chính sách QA
Mỗi task phải có:
- acceptance criteria rõ ràng
- ít nhất 1 happy path
- ít nhất 1 failure/edge case
- evidence file trong `.omo/evidence/`

---

## Chiến lược thực thi

### Triển khai tuần tự theo module
> Người dùng đã chốt rõ: **ưu tiên hoàn thành từng module theo pipeline**, không làm song song nhiều module.

```text
Wave 1 (Nền tảng)
1. Định nghĩa contracts lõi và data model
2. Tạo ingestion entrypoint source-agnostic

Wave 2 (Parsing)
3. Implement PDF parser + normalizer
4. Implement DOCX parser + normalizer

Wave 3 (Chunk + policy)
5. Implement chunking + citation propagation
6. Implement access-policy tagging + deny-by-default

Wave 4 (Index + retrieve)
7. Implement indexing/storage abstraction
8. Implement role-aware retrieval

Wave 5 (LangGraph orchestration + session memory)
9. Implement LangGraph query flow + short-lived session memory
10. Implement answer generation + citation enforcement

Wave 6 (Audit + observability)
11. Implement audit logging + memory-safe audit policy
12. Implement LangSmith observability layer

Wave 7 (Extension boundary)
13. Implement extension boundary cho future sources / adapters

Wave FINAL (Verification)
F1. End-to-end pipeline validation
F2. Authorization leak check
F3. Regression / quality review
F4. Scope fidelity check
```

### Dependency Matrix
- **1**: mở đường cho tất cả task còn lại
- **2**: phụ thuộc 1, mở đường cho 3-4
- **3**: phụ thuộc 2, mở đường cho 5+
- **4**: phụ thuộc 3, mở đường cho 5+
- **5**: phụ thuộc 4, mở đường cho 6+
- **6**: phụ thuộc 5, mở đường cho 7+
- **7**: phụ thuộc 6, mở đường cho 8+
- **8**: phụ thuộc 7, mở đường cho 9+
- **9**: phụ thuộc 8, mở đường cho 10+ và memory/session integration
- **10**: phụ thuộc 9, mở đường cho 11+
- **11**: phụ thuộc 6, 8, 9, 10
- **12**: phụ thuộc 11 và toàn bộ contract/pipeline trước đó
- **13**: phụ thuộc 12 và toàn bộ contract/pipeline trước đó
- **F1-F4**: chạy sau khi 1-13 hoàn thành

### Agent dispatch summary
- **1-2**: `unspecified-high`, `quick`
- **3-4**: `quick`, `quick`
- **5-6**: `deep`, `unspecified-high`
- **7-8**: `unspecified-high`, `deep`
- **9-10**: `deep`, `unspecified-high`
- **11-12**: `unspecified-high`, `unspecified-high`
- **13**: `deep`
- **F1-F4**: `oracle`, `unspecified-high`, `unspecified-high`, `deep`

---

## TODOs

- [ ] 1. Định nghĩa contracts lõi và normalized data model

  **Trạng thái**: DONE — đã xác minh trong codebase.

  **Bằng chứng implementation**:
  - `app/agentic/contracts/source.py`: `SourceType`, `SourceMetadata` với `source_type`, `mime_type`, `source_uri`.
  - `app/agentic/contracts/document.py`: `ParsedDocument`, `NormalizedDocument`, `ContentBlock`, `CitationMetadata`, `DocumentRecord`.
  - `app/agentic/contracts/chunk.py`: `DocumentChunk`, `RetrievalCandidate`, `RetrievalRequest`, `RetrievalOutcome` với `chunk_id`, `chunker_version`, citation và access policy.
  - `app/agentic/contracts/access_policy.py`: `AccessPolicyMetadata`, `Classification`, `VisibilityScope`, `UserAccessContext`; validate fail-closed cho role/department/owner/manager scope.
  - `app/agentic/contracts/retrieval.py`: `RetrievalFilter`, `EvidenceBundle`.
  - `app/agentic/contracts/answer.py`: `AnswerResult`, `AnswerCitation` với citation-enforced response statuses gồm tối thiểu `answered`, `insufficient_evidence`, `insufficient_permission`, `unsupported_scope`.
  - `app/agentic/contracts/audit.py`: `AuditEvent` cho ingest/parse/retrieval/answer events.
  - `app/agentic/contracts/graph_state.py`: serializable `GraphState` không phụ thuộc LangGraph runtime object.
  - `tests/unit/ai/test_contracts.py`: test normalized PDF-like document hợp lệ, fail-closed khi thiếu scope metadata, và yêu cầu `access_policy`.

  **Việc cần làm**:
  - Tạo các contract cốt lõi cho:
    - source input
    - parsed document
    - normalized document
    - content block
    - document chunk
    - access policy metadata
    - answer result
    - audit event
    - graph state
  - Bảo đảm contract không gắn cứng vào PDF/DOCX.
  - Bổ sung field cần thiết như:
    - `source_type`
    - `mime_type`
    - `source_uri`
    - `document_id`
    - `chunk_id`
    - `classification`
    - `visibility_scope`
    - `allowed_roles`
    - `department_id`
    - `owner_id`
    - `parser_version`
    - `chunker_version`
    - citation metadata

  **Không được làm**:
  - Chưa implement parser ở task này.
  - Không tạo contract phụ thuộc trực tiếp vào LangGraph runtime object.
  - Không nhúng logic vendor cụ thể vào contract.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Đây là phần nền tảng quyết định sự ổn định của toàn bộ pipeline.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1
  - **Blocks**: 2-13
  - **Blocked By**: None

  **References**:
  - RBAC models hiện có của dự án để map access policy
  - Convention đặt tên model/schema của backend hiện tại

  **Gợi ý file cho bước này**:
  - `app/agentic/__init__.py`
  - `app/agentic/contracts/__init__.py`
  - `app/agentic/contracts/source.py`
  - `app/agentic/contracts/document.py`
  - `app/agentic/contracts/chunk.py`
  - `app/agentic/contracts/access_policy.py`
  - `app/agentic/contracts/retrieval.py`
  - `app/agentic/contracts/answer.py`
  - `app/agentic/contracts/audit.py`
  - `app/agentic/contracts/graph_state.py`
  - `tests/unit/ai/test_contracts.py`

  **Acceptance Criteria**:
  - [ ] Có đầy đủ contract lõi cho toàn pipeline.
  - [ ] Contract source-agnostic, không branch theo PDF/DOCX ngoài adapter boundary.
  - [ ] Có test/validation cho ít nhất một normalized document fixture.

  **QA Scenarios**:
  ```
  Scenario: contract chấp nhận normalized document tối thiểu
    Tool: Bash / project test runner
    Preconditions: Có contract module và fixture mẫu.
    Steps:
      1. Chạy test validate một document mẫu có source_type="uploaded_file" và mime_type="application/pdf".
      2. Assert có document_id, classification, visibility_scope, citation metadata.
      3. Assert không có parser-specific runtime object trong contract.
    Expected Result: Contract hợp lệ và source-agnostic.
    Evidence: .omo/evidence/task-1-contract-ok.txt

  Scenario: contract fail khi thiếu access metadata
    Tool: Bash / project test runner
    Preconditions: Có fixture thiếu classification/visibility.
    Steps:
      1. Chạy validation với fixture thiếu access metadata.
      2. Assert validation fail rõ ràng.
    Expected Result: Fail closed khi thiếu metadata.
    Evidence: .omo/evidence/task-1-contract-fail.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): define core contracts`
  - Pre-commit: contract/unit tests

- [ ] 2. Tạo ingestion entrypoint source-agnostic

  **Trạng thái**: DONE — đã xác minh trong codebase.

  **Bằng chứng implementation**:
  - `app/agentic/ingestion/ingest_source.py`: `IngestSource.ingest()` nhận `SourceMetadata` generic cùng `AccessPolicyMetadata`, trả `IngestionResult` có checksum, status `pending_parse`, parser target, source và policy metadata.
  - `app/agentic/ingestion/source_registry.py`: `SourceRegistry` dispatch theo `source_type` / `mime_type`, v1 chỉ nhận `uploaded_file` PDF/DOCX và reject unsupported source/mime bằng controlled `ValueError`.
  - `app/agentic/ingestion/checksum.py`: checksum SHA-256 ổn định từ source metadata khi input chưa có checksum.
  - `tests/unit/ai/test_ingestion.py`: test PDF/DOCX happy path, XLSX reject, external URI reject trong v1, và bắt buộc truyền access policy.
  - `.omo/evidence/task-2-docx-ok.txt` và `.omo/evidence/task-2-xlsx-reject.txt`: evidence QA cho DOCX accepted và XLSX rejected.

  **Việc cần làm**:
  - Tạo entrypoint nhận source generic.
  - Dispatch theo `source_type` / `mime_type`.
  - V1 chỉ hỗ trợ uploaded-file path.
  - Ghi nhận checksum, ingestion status, parser target.
  - Chuẩn bị chỗ cắm `source_registry` để sau này thêm source mới.

  **Không được làm**:
  - Không parse nội dung thực tế ở task này.
  - Không thêm connector Notion/Confluence/Drive.
  - Không bỏ qua access metadata.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Task scaffolding hẹp sau khi contract đã ổn định.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1
  - **Blocks**: 3-4
  - **Blocked By**: 1

  **References**:
  - Contract từ task 1
  - Pattern backend service/use-case hiện có

  **Gợi ý file cho bước này**:
  - `app/agentic/ingestion/__init__.py`
  - `app/agentic/ingestion/ingest_source.py`
  - `app/agentic/ingestion/source_registry.py`
  - `app/agentic/ingestion/checksum.py`
  - `tests/unit/ai/test_ingestion.py`

  **Acceptance Criteria**:
  - [ ] Entry point nhận PDF/DOCX metadata cho `uploaded_file` trong scope v1.
  - [ ] Trả về ingestion result có checksum/status/parser target.
  - [ ] Ingestion result giữ lại `source` và `access_policy` metadata để parse/index stages dùng tiếp.
  - [ ] Unsupported `source_type` hoặc MIME ngoài scope trả controlled error.

  **QA Scenarios**:
  ```
  Scenario: nhận DOCX source thành công
    Tool: Bash / project test runner
    Preconditions: Có DOCX metadata fixture.
    Steps:
      1. Chạy ingestion entrypoint với MIME DOCX.
      2. Assert status là accepted/pending_parse.
      3. Assert có checksum và source metadata.
    Expected Result: Source được nhận mà chưa parse nội dung.
    Evidence: .omo/evidence/task-2-docx-ok.txt

  Scenario: từ chối XLSX trong v1
    Tool: Bash / project test runner
    Preconditions: Có XLSX metadata fixture.
    Steps:
      1. Chạy ingestion entrypoint với MIME XLSX.
      2. Assert controlled unsupported error.
    Expected Result: XLSX bị từ chối đúng scope v1.
    Evidence: .omo/evidence/task-2-xlsx-reject.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add ingestion entrypoint`
  - Pre-commit: ingestion tests

- [ ] 3. Implement PDF parser + normalizer cho PDF text-based

  **Trạng thái**: DONE — đã xác minh trong codebase.

  **Bằng chứng implementation**:
  - `app/agentic/adapters/parsers/base.py`: `BaseParser` và `ParserError` làm boundary cho parser adapter và controlled failure.
  - `app/agentic/adapters/parsers/pdf_parser.py`: `PdfTextParser.parse()` dùng LangChain `PyPDFLoader` cho PDF text-based, chuẩn hóa page metadata về 1-based citation, và fail closed với `ocr_not_supported_yet` khi không có text extractable.
  - `app/agentic/parsing/parser_registry.py`: registry parser cho MIME `application/pdf`.
  - `app/agentic/parsing/parse_document.py`: `parse_document()` dispatch parser theo MIME; `normalize_document()` chuyển `ParsedDocument` thành `NormalizedDocument` với `ContentBlock` và `CitationMetadata(...)` từ extracted block metadata.
  - `app/agentic/parsing/normalize_document.py`: wrapper normalize để giữ module boundary rõ ràng.
  - `tests/unit/ai/test_parsing_pdf.py`: test parse PDF text-based, normalize thành block có page citation, và reject PDF không có text.
  - `tests/fixtures/ai/sample_text.pdf` và `tests/fixtures/ai/sample_scanned_or_empty.pdf`: fixtures cho happy path và no-text failure path.
  - `.omo/evidence/task-3-pdf-ok.txt` và `.omo/evidence/task-3-pdf-no-text.txt`: evidence QA cho parse success và no-text controlled failure.

  **Việc cần làm**:
  - Chọn parser library phù hợp cho PDF text-based.
  - Parse nội dung PDF.
  - Normalize thành content blocks theo contract task 1.
  - Giữ page metadata và citation path.
  - Detect scanned/no-text PDF và trả trạng thái OCR-not-supported-yet.

  **Không được làm**:
  - Không implement OCR ở v1.
  - Không index/embedding ở task này.
  - Không coi parse rỗng là success.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adapter cụ thể, input/output rõ.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: 4-13
  - **Blocked By**: 2

  **References**:
  - Contract task 1
  - Ingestion result task 2

  **Gợi ý file cho bước này**:
  - `app/agentic/adapters/parsers/__init__.py`
  - `app/agentic/adapters/parsers/base.py`
  - `app/agentic/adapters/parsers/pdf_parser.py`
  - `app/agentic/parsing/__init__.py`
  - `app/agentic/parsing/parser_registry.py`
  - `app/agentic/parsing/parse_document.py`
  - `app/agentic/parsing/normalize_document.py`
  - `tests/fixtures/ai/sample_text.pdf`
  - `tests/fixtures/ai/sample_scanned_or_empty.pdf`
  - `tests/unit/ai/test_parsing_pdf.py`

  **Acceptance Criteria**:
  - [ ] PDF text-based parse được thành normalized blocks.
  - [ ] Page citation metadata được giữ lại.
  - [ ] PDF không có text trả trạng thái controlled failure.

  **QA Scenarios**:
  ```
  Scenario: parse PDF text-based thành normalized blocks
    Tool: Bash / project test runner
    Preconditions: Có PDF fixture text-based.
    Steps:
      1. Chạy parser PDF trên fixture.
      2. Assert có content block chứa text mong đợi.
      3. Assert mỗi block có page/citation metadata.
    Expected Result: Parse thành công và có citation metadata.
    Evidence: .omo/evidence/task-3-pdf-ok.txt

  Scenario: scanned/no-text PDF fail closed
    Tool: Bash / project test runner
    Preconditions: Có fixture PDF không có text.
    Steps:
      1. Chạy parser trên fixture no-text.
      2. Assert trạng thái OCR_NOT_SUPPORTED hoặc tương đương.
    Expected Result: Hệ thống từ chối xử lý OCR ở v1 một cách rõ ràng.
    Evidence: .omo/evidence/task-3-pdf-no-text.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add pdf parser`
  - Pre-commit: parser tests

- [ ] 4. Implement DOCX parser + normalizer

  **Trạng thái**: DONE — đã xác minh trong codebase.

  **Bằng chứng implementation**:
  - `app/agentic/adapters/parsers/docx_parser.py`: `DocxParser.parse()` đọc `.docx` từ zip/XML, giữ structure cho heading / paragraph / table và reject `.doc` legacy bằng controlled `ParserError`.
  - `app/agentic/parsing/parser_registry.py`: routing parser theo MIME cho cả PDF, DOCX và `.doc` legacy vào parser phù hợp.
  - `app/agentic/parsing/parse_document.py`: `normalize_document()` dùng `extracted_metadata["blocks"]` để map parser-specific structure thành `ContentBlock` / `CitationMetadata` chuẩn chung.
  - `tests/unit/ai/test_parsing_docx.py`: test DOCX happy path và reject `.doc` legacy.
  - `tests/fixtures/ai/sample.docx`: fixture DOCX cho heading / paragraph / table.
  - `.omo/evidence/task-4-docx-ok.txt` và `.omo/evidence/task-4-doc-legacy.txt`: evidence QA cho parse success và legacy reject.

  **Việc cần làm**:
  - Parse `.docx`
  - Normalize heading / paragraph / table thành content blocks
  - Gắn section/title/citation metadata nếu có
  - Từ chối `.doc` legacy ở v1

  **Không được làm**:
  - Không hỗ trợ `.doc` legacy ở v1
  - Không hỗ trợ Google Docs / SharePoint
  - Không index/embedding ở task này

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adapter parser hẹp, dễ kiểm thử.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocks**: 5-13
  - **Blocked By**: 3

  **References**:
  - Parser PDF task 3 làm shape chuẩn tham chiếu
  - Contract task 1

  **Gợi ý file cho bước này**:
  - `app/agentic/adapters/parsers/docx_parser.py`
  - `tests/fixtures/ai/sample.docx`
  - `tests/unit/ai/test_parsing_docx.py`
  - Có thể sửa tiếp `app/agentic/parsing/parser_registry.py`
  - Có thể sửa tiếp `app/agentic/parsing/normalize_document.py`

  **Acceptance Criteria**:
  - [ ] DOCX parse được thành normalized blocks.
  - [ ] Có ghi nhận behavior với heading/paragraph/table.
  - [ ] `.doc` legacy bị reject controlled.

  **QA Scenarios**:
  ```
  Scenario: parse DOCX thành normalized blocks
    Tool: Bash / project test runner
    Preconditions: Có DOCX fixture.
    Steps:
      1. Chạy parser DOCX.
      2. Assert heading và paragraph xuất hiện trong normalized output.
      3. Assert có source/citation metadata.
    Expected Result: DOCX parse được cùng shape với PDF.
    Evidence: .omo/evidence/task-4-docx-ok.txt

  Scenario: reject DOC legacy trong v1
    Tool: Bash / project test runner
    Preconditions: Có fixture hoặc metadata cho `.doc`.
    Steps:
      1. Chạy ingestion/parser dispatch với `.doc`.
      2. Assert controlled unsupported error.
    Expected Result: `.doc` không bị coi như `.docx`.
    Evidence: .omo/evidence/task-4-doc-legacy.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add docx parser`
  - Pre-commit: parser tests

- [x] 5. Implement chunking + citation propagation

  **Trạng thái**: DONE — đã triển khai trong codebase.

  **Bằng chứng implementation**:
  - `app/agentic/chunking/__init__.py`: public chunking API `ChunkConfig`, `DocumentChunker`, `chunk_document`, tokenizer adapters.
  - `app/agentic/chunking/chunk_config.py`: versioned token budget config với `chunker_version`, `max_chunk_tokens`, `overlap_tokens`, `tokenizer_policy` default theo HuggingFace policy.
  - `app/agentic/chunking/tokenizer.py`: tokenizer adapter boundary; ưu tiên `transformers.AutoTokenizer` cho `intfloat/multilingual-e5-base`, fallback an toàn sang whitespace tokenizer khi runtime không có dependency/model cache.
  - `app/agentic/chunking/chunk_document.py`: token-aware chunking từ `NormalizedDocument.blocks`, giữ `document_id`, `chunk_id`, `chunk_index`, `token_count`, `chunker_version`, access policy và provenance citation/metadata.
  - `app/agentic/contracts/chunk.py`: `DocumentChunk` là output contract retrieval-ready cho chunk stage.
  - `tests/unit/ai/test_chunking.py`: test chunking PDF và DOCX normalized input, verify token budget + citation/provenance retention + adapter fallback.
  - `app/agentic/contracts/document.py`: `NormalizedDocument`/`ContentBlock`/`CitationMetadata` là input chuẩn hóa cho chunking.

  **Việc cần làm**:
  - Chia normalized content thành chunk retrieval-ready theo **token budget**, không chỉ theo ký tự.
  - Giữ document/page/section/title provenance trong từng chunk.
  - Version hóa chunking strategy và lưu `token_count`/`chunker_version`.
  - Đảm bảo citation còn dùng được sau chunking.
  - Chốt tokenizer policy dùng cho chunk sizing để cùng chuẩn với model strategy của MVP.
  - Thiết kế ngưỡng chunk overlap / max chunk tokens / max evidence tokens cho retrieval sau này.

  **Không được làm**:
  - Không embed/retrieve ở task này
  - Không mất provenance trong chunk
  - Không dùng contract riêng cho PDF hoặc DOCX

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Chất lượng chunking ảnh hưởng trực tiếp tới retrieval và citation.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: 6-13
  - **Blocked By**: 4

  **References**:
  - Normalized outputs từ task 3-4
  - Chunk contract task 1

  **Gợi ý file cho bước này**:
  - `app/agentic/chunking/__init__.py`
  - `app/agentic/chunking/chunk_config.py`
  - `app/agentic/chunking/chunk_document.py`
  - `tests/unit/ai/test_chunking.py`

  **Acceptance Criteria**:
  - [x] Chunk có content, chunk_id, document_id, citation metadata.
  - [x] Chunking có version/config.
  - [x] Provenance đủ để cite page/section sau retrieval.
  - [x] Mỗi chunk có `token_count`, `chunker_version`, và token budget config rõ ràng.
  - [x] Chunking vượt threshold phải split theo token-aware policy, không chỉ theo character count.

  **QA Scenarios**:
  ```
  Scenario: tạo chunk retrieval-ready từ PDF/DOCX
    Tool: Bash / project test runner
    Preconditions: Có normalized fixtures.
    Steps:
      1. Chạy chunking trên output PDF và DOCX.
      2. Assert tạo ra nhiều chunk khi vượt threshold.
      3. Assert mỗi chunk có document_id, chunk_id, provenance.
    Expected Result: Chunk retrieval-ready và có citation metadata.
    Evidence: .omo/evidence/task-5-chunks.txt

  Scenario: giữ đúng provenance cho text đã biết
    Tool: Bash / project test runner
    Preconditions: Có fixture với page/heading đã biết.
    Steps:
      1. Tìm chunk chứa text đã biết.
      2. Assert chunk trỏ đúng page hoặc section metadata.
    Expected Result: Citation dùng lại được.
    Evidence: .omo/evidence/task-5-provenance.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add chunking`
  - Pre-commit: chunking tests

- [ ] 6. Implement access-policy tagging + deny-by-default

  **Việc cần làm**:
  - Gắn access policy metadata vào document/chunk
  - Thiết kế `resolve_policy`, `evaluate_access`, `build_retrieval_filter`
  - Hỗ trợ ít nhất:
    - role-based access
    - department scope
    - owner-only
    - placeholder cho manager subtree
  - Fail closed khi policy không xác định rõ

  **Không được làm**:
  - Không dựa vào UI để chặn quyền
  - Không cho chunk thiếu metadata đi vào retrieval
  - Không gắn chặt policy logic với PDF/DOCX parser

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Đây là task security-critical.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3
  - **Blocks**: 7-13
  - **Blocked By**: 5

  **References**:
  - RBAC hiện có của dự án
  - Access metadata contract task 1

  **Gợi ý file cho bước này**:
  - `app/agentic/access_control/__init__.py`
  - `app/agentic/access_control/resolve_policy.py`
  - `app/agentic/access_control/evaluate_access.py`
  - `app/agentic/access_control/build_retrieval_filter.py`
  - `tests/unit/ai/test_access_control.py`

  **Acceptance Criteria**:
  - [ ] Chunk thiếu access metadata không retrievable.
  - [ ] Access evaluator hỗ trợ ít nhất admin/global, department-scoped, owner-only.
  - [ ] Access evaluator trả reason code allow/deny rõ ràng.

  **QA Scenarios**:
  ```
  Scenario: authorized chunk được allow
    Tool: Bash / project test runner
    Preconditions: Có chunk metadata đúng role/scope.
    Steps:
      1. Chạy evaluate_access cho user hợp lệ.
      2. Assert decision là ALLOW và có reason code.
    Expected Result: Access được cho phép đúng.
    Evidence: .omo/evidence/task-6-allow.txt

  Scenario: thiếu classification thì deny
    Tool: Bash / project test runner
    Preconditions: Có chunk metadata thiếu classification hoặc visibility.
    Steps:
      1. Chạy evaluate_access với metadata thiếu.
      2. Assert decision là DENY với fail-closed reason.
    Expected Result: Quyền không rõ thì deny.
    Evidence: .omo/evidence/task-6-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add access control`
  - Pre-commit: access-control tests

- [ ] 7. Implement indexing/storage abstraction

  **Việc cần làm**:
  - Tạo abstraction cho document storage / chunk storage / vector index reference.
  - Chốt default MVP với đúng **một concrete adapter cho mỗi capability liên quan** và vẫn có adapter boundary.
  - Lưu parser/chunker/index versions, `policy_version`, `index_version`, và indexing status.
  - Bảo đảm retry-safe, không duplicate chunk identity, và hỗ trợ re-index idempotent.
  - Ưu tiên adapter mặc định đơn giản, local/dev-friendly; không mở matrix nhiều provider trong MVP.
  - Đảm bảo vector metadata/index state hỗ trợ lookup theo `chunk_id`, `document_id`, `token_count`, `source_type`, `mime_type`.

  **Không được làm**:
  - Không build nhiều backend production cùng lúc trong v1
  - Không implement nhiều concrete adapters cho cùng một capability trong MVP
  - Không lưu chunk retrievable mà thiếu access metadata
  - Không để indexing status bị ẩn khỏi pipeline

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Đây là chỗ cần boundary tốt để đổi tech stack sau này.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: 8-13
  - **Blocked By**: 6

  **References**:
  - Contract document/chunk task 1
  - Policy requirements task 6

  **Gợi ý file cho bước này**:
  - `app/agentic/indexing/__init__.py`
  - `app/agentic/indexing/index_document.py`
  - `app/agentic/indexing/index_status.py`
  - `app/agentic/adapters/storage/__init__.py`
  - `app/agentic/adapters/storage/base.py`
  - `app/agentic/adapters/storage/local_storage.py`
  - `app/agentic/adapters/vector_store/__init__.py`
  - `app/agentic/adapters/vector_store/base.py`
  - `app/agentic/adapters/vector_store/default_vector_store.py`
  - `app/agentic/adapters/embeddings/__init__.py`
  - `app/agentic/adapters/embeddings/base.py`
  - `app/agentic/adapters/embeddings/default_embeddings.py`
  - `tests/unit/ai/test_indexing.py`

  **Acceptance Criteria**:
  - [ ] Document/chunk persist được với stable id.
  - [ ] Có indexing status và version metadata.
  - [ ] Retry indexing không tạo duplicate record.
  - [ ] Embedding adapter và vector store adapter tách biệt với answer LLM adapter.
  - [ ] Indexed metadata có `token_count`, `policy_version`, `index_version`, và active/stale state.
  - [ ] Re-index cùng document/version không làm stale chunk retrievable.

  **QA Scenarios**:
  ```
  Scenario: index document và chunk với stable identity
    Tool: Bash / project test runner
    Preconditions: Có parsed + chunked fixture.
    Steps:
      1. Chạy indexing cho một sample document.
      2. Assert document_id và chunk_ids ổn định và liên kết đúng.
      3. Assert có status/version fields.
    Expected Result: Index persist được và audit được.
    Evidence: .omo/evidence/task-7-index.txt

  Scenario: retry indexing không duplicate
    Tool: Bash / project test runner
    Preconditions: Document đã index 1 lần.
    Steps:
      1. Chạy lại indexing cho cùng document version.
      2. Assert không tạo thêm duplicate records.
    Expected Result: Retry idempotent.
    Evidence: .omo/evidence/task-7-retry.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add indexing abstraction`
  - Pre-commit: indexing tests

- [ ] 8. Implement role-aware retrieval

  **Việc cần làm**:
  - Implement retrieval dùng metadata filters từ access control.
  - Retrieval chỉ trả evidence đã được phép.
  - Trả về evidence bundle có citation hoặc deny/no-evidence semantics.
  - Tách retrieval khỏi answer generation.
  - Hỗ trợ lookup/fetch-by-chunk-id cho các `last_cited_chunk_ids` từ session memory, nhưng luôn re-check access policy trước khi trả evidence.
  - Chừa điểm cắm cho retrieval cache có phân quyền nếu sau này bật Redis cache layer.
  - Thiết lập mặc định cho `top_k`, similarity threshold, max evidence tokens, và filter ordering.
  - Cho phép rerank lightweight/rule-based sau filter nhưng trước khi dựng evidence bundle.
  - Không cho chunk dưới threshold hoặc ngoài budget đi vào context cuối.

  **Không được làm**:
  - Không cho unauthorized chunks vào LLM context
  - Không trả chunk thiếu citation metadata
  - Không gắn retrieval chặt với một vector DB cụ thể ở higher-level flow

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Đây là trung tâm của RAG đúng/sai và leak/không leak.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: 9-13
  - **Blocked By**: 7

  **References**:
  - Access evaluator task 6
  - Indexed chunk/document structures task 7

  **Gợi ý file cho bước này**:
  - `app/agentic/retrieval/__init__.py`
  - `app/agentic/retrieval/evidence_bundle.py`
  - `app/agentic/retrieval/retrieve_evidence.py`
  - `app/agentic/retrieval/rerank.py`
  - `tests/unit/ai/test_retrieval.py`

  **Acceptance Criteria**:
  - [ ] User hợp lệ chỉ lấy được chunk được phép.
  - [ ] User không hợp lệ không lấy được restricted chunk.
  - [ ] Retrieval response có citation hoặc deny/no-evidence rõ ràng.
  - [ ] Fetch-by-chunk-id từ session memory vẫn re-check quyền và không trả stale/unauthorized chunk.
  - [ ] Retrieval dùng `top_k`, score threshold, max evidence tokens, và config filter ordering.
  - [ ] Không chunk nào ngoài budget/threshold được đưa vào evidence bundle cuối.
  - [ ] Rerank MVP không dùng LLM và luôn chạy sau access filtering.

  **QA Scenarios**:
  ```
  Scenario: user hợp lệ retrieve được evidence trong scope
    Tool: Bash / project test runner
    Preconditions: Có indexed chunks với department scope.
    Steps:
      1. Chạy retrieval cho user thuộc đúng department.
      2. Assert chunk trả về có text mong đợi và citation fields.
      3. Assert không có chunk ngoài scop
  **Acceptance Criteria**:
  - [ ] Document/chunk persist được với stable id.
  - [ ] Có indexing status và version metadata.
  - [ ] Retry indexing không tạo duplicate record.
  - [ ] Embedding adapter và vector store adapter tách biệt với answer LLM adapter.
  - [ ] Indexed metadata có `token_count`, `policy_version`, `index_version`, và active/stale state.
  - [ ] Re-index cùng document/version không làm stale chunk retrievable.

  **QA Scenarios**:
  ```
  Scenario: index document và chunk với stable identity
    Tool: Bash / project test runner
    Preconditions: Có parsed + chunked fixture.
    Steps:
      1. Chạy indexing cho một sample document.
      2. Assert document_id và chunk_ids ổn định và liên kết đúng.
      3. Assert có status/version fields.
    Expected Result: Index persist được và audit được.
    Evidence: .omo/evidence/task-7-index.txt

  Scenario: retry indexing không duplicate
    Tool: Bash / project test runner
    Preconditions: Document đã index 1 lần.
    Steps:
      1. Chạy lại indexing cho cùng document version.
      2. Assert không tạo thêm duplicate records.
    Expected Result: Retry idempotent.
    Evidence: .omo/evidence/task-7-retry.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add indexing abstraction`
  - Pre-commit: indexing tests

- [ ] 8. Implement role-aware retrieval

  **Việc cần làm**:
  - Implement retrieval dùng metadata filters từ access control.
  - Retrieval chỉ trả evidence đã được phép.
  - Trả về evidence bundle có citation hoặc deny/no-evidence semantics.
  - Tách retrieval khỏi answer generation.
  - Hỗ trợ lookup/fetch-by-chunk-id cho các `last_cited_chunk_ids` từ session memory, nhưng luôn re-check access policy trước khi trả evidence.
  - Chừa điểm cắm cho retrieval cache có phân quyền nếu sau này bật Redis cache layer.
  - Thiết lập mặc định cho `top_k`, similarity threshold, max evidence tokens, và filter ordering.
  - Cho phép rerank lightweight/rule-based sau filter nhưng trước khi dựng evidence bundle.
  - Không cho chunk dưới threshold hoặc ngoài budget đi vào context cuối.

  **Không được làm**:
  - Không cho unauthorized chunks vào LLM context
  - Không trả chunk thiếu citation metadata
  - Không gắn retrieval chặt với một vector DB cụ thể ở higher-level flow

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Đây là trung tâm của RAG đúng/sai và leak/không leak.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 4
  - **Blocks**: 9-13
  - **Blocked By**: 7

  **References**:
  - Access evaluator task 6
  - Indexed chunk/document structures task 7

  **Gợi ý file cho bước này**:
  - `app/agentic/retrieval/__init__.py`
  - `app/agentic/retrieval/evidence_bundle.py`
  - `app/agentic/retrieval/retrieve_evidence.py`
  - `app/agentic/retrieval/rerank.py`
  - `tests/unit/ai/test_retrieval.py`e.
    Expected Result: Retrieval vừa đúng vừa an toàn.
    Evidence: .omo/evidence/task-8-allow.txt

  Scenario: user không hợp lệ bị deny không leak content
    Tool: Bash / project test runner
    Preconditions: Có restricted chunks đã index.
    Steps:
      1. Chạy retrieval cho user ngoài scope.
      2. Assert không có restricted content trong kết quả.
      3. Assert có deny/no-evidence reason rõ ràng.
    Expected Result: Retrieval fail closed.
    Evidence: .omo/evidence/task-8-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add role-aware retrieval`
  - Pre-commit: retrieval tests

- [ ] 9. Implement LangGraph query flow cố định

  **Việc cần làm**:
  - Tạo `rag_graph.py` và các node trong `orchestration/nodes/`.
  - LangGraph state phải explicit, serializable.
  - Flow tối thiểu:
    - load user context
    - classify query
    - hydrate short-lived session memory (nếu có)
    - rewrite follow-up query bằng `topic_summary` / recent turns khi query phụ thuộc ngữ cảnh
    - ưu tiên fetch-by-chunk-id nếu session memory có `last_cited_chunk_ids` phù hợp
    - fallback sang vector retrieval khi không đủ cited chunk refs hoặc cần evidence mới
    - validate policy/no-evidence
    - generate answer
    - update session memory bằng summary + cited refs + status an toàn
    - audit event
  - Query rewrite chỉ làm rõ intent, không tạo factual answer và không mở rộng scope.
  - Query ngoài phạm vi tài liệu indexed phải trả `unsupported_scope` hoặc `insufficient_evidence`.
  - Answer generation phải dùng model tách biệt với embedding model.
  - Prompt/context budget phải được quản lý riêng trong graph trước khi gọi answer model.
  - Có conditional branch cho deny và no-evidence
  - Session memory chỉ dùng làm context phụ trợ, không thay thế retrieval/citation
  - Memory record tối thiểu gồm: `session_id`, `user_id`, `topic_summary`, `recent_turns`, `last_answer_status`, `last_cited_documents`, `last_cited_chunk_ids`, `policy_version`, `index_version`, `expires_at`
  - **Redis session memory schema (MVP)**:
    - Key format: `rag:session:{user_id}:{session_id}`
    - Value fields: `session_id`, `user_id`, `topic_summary`, `recent_turns`, `last_answer_status`, `last_cited_documents`, `last_cited_chunk_ids`, `policy_version`, `index_version`, `expires_at`
    - TTL: default short-lived TTL; refresh khi session còn active, hard-expire khi hết hạn
    - Invalidation: bỏ qua memory cũ khi `policy_version` hoặc `index_version` thay đổi, hoặc khi user/session không khớp
    - Security rule: không lưu raw restricted chunk text hay evidence đầy đủ; chỉ lưu metadata + refs đủ để rewrite/fetch-by-id an toàn

  **Không được làm**:
  - Không để LangGraph node ôm business logic quá dày
  - Không bỏ qua authorization checks trong graph
  - Không trộn ingestion pipeline vào query graph runtime
  - Không dùng session memory làm evidence hoặc nguồn trả lời không citation
  - Không lưu raw restricted chunk text dài hạn trong Redis/session memory
  - Không route sang DB/API/backend tools trong MVP
  - Query ngoài phạm vi tài liệu indexed phải trả insufficient evidence hoặc unsupported scope

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Đây là orchestration spine cố định của hệ thống.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5
  - **Blocks**: 10-13
  - **Blocked By**: 8

  **References**:
  - Retrieval output task 8
  - Policy evaluator task 6
  - Graph state contract task 1

  **Gợi ý file cho bước này**:
  - `app/agentic/orchestration/__init__.py`
  - `app/agentic/orchestration/graph_state.py`
  - `app/agentic/orchestration/rag_graph.py`
  - `app/agentic/orchestration/nodes/__init__.py`
  - `app/agentic/orchestration/nodes/load_user_context.py`
  - `app/agentic/orchestration/nodes/classify_query.py`
  - `app/agentic/orchestration/nodes/route_query.py`
  - `app/agentic/orchestration/nodes/retrieve_evidence.py`
  - `app/agentic/orchestration/nodes/validate_policy.py`
  - `app/agentic/orchestration/nodes/generate_answer.py`
  - `app/agentic/orchestration/nodes/deny_request.py`
  - `app/agentic/orchestration/nodes/audit_event.py`
  - `app/agentic/memory/__init__.py`
  - `app/agentic/memory/memory_policy.py`
  - `app/agentic/memory/session_memory.py`
  - `app/agentic/memory/memory_summary.py`
  - `app/agentic/adapters/session/__init__.py`
  - `app/agentic/adapters/session/base.py`
  - `app/agentic/adapters/session/redis_session_store.py`
  - `tests/unit/ai/test_session_memory.py`
  - `tests/integration/ai/test_graph_flow.py`

  **Acceptance Criteria**:
  - [ ] Query chạy qua đúng các stage của graph.
  - [ ] Graph branch đúng ở deny/no-evidence.
  - [ ] Graph state inspect/debug được.
  - [ ] Session memory có TTL, giới hạn số turn/summary size, và key theo user/session/policy context.
  - [ ] Session memory record tối thiểu có `topic_summary`, `last_cited_chunk_ids`, `last_cited_documents`, `last_answer_status`, `policy_version`, `index_version`.
  - [ ] Redis key dùng format `rag:session:{user_id}:{session_id}` và session memory bị bỏ qua khi `policy_version`/`index_version` không khớp.
  - [ ] Follow-up query có thể được rewrite từ session context; khi có cited refs phù hợp thì ưu tiên fetch-by-id trước, không phù hợp thì fallback sang vector retrieval.
  - [ ] Query ngoài phạm vi tài liệu indexed trả `unsupported_scope` hoặc `insufficient_evidence`, không route sang DB/API tool.
  - [ ] Session memory chỉ bổ sung context phụ trợ; answer vẫn phải có authorized evidence/citation hoặc explicit deny/no-evidence.
  - [ ] Graph quản lý prompt/context token budget trước khi gọi answer LLM.
  - [ ] Query rewrite lưu cả original query và rewritten query để audit/debug, không sinh factual answer.

  **QA Scenarios**:
  ```
  Scenario: query đi đúng qua pipeline LangGraph
    Tool: Bash / project test runner
    Preconditions: Có query mẫu và document hợp lệ.
    Steps:
      1. Chạy graph với query đã biết.
      2. Assert flow gọi đúng context → classify → retrieve → answer → audit.
      3. Assert output có citation.
    Expected Result: Graph chạy đúng pipeline.
    Evidence: .omo/evidence/task-9-graph.txt

  Scenario: query bị deny đi đúng deny branch
    Tool: Bash / project test runner
    Preconditions: Có restricted document và user không có quyền.
    Steps:
      1. Chạy graph với query restricted.
      2. Assert deny branch được kích hoạt.
      3. Assert answer node không nhận restricted chunks.
    Expected Result: Graph fail closed khi deny.
    Evidence: .omo/evidence/task-9-deny-branch.txt

  Scenario: session memory được hydrate nhưng không bypass retrieval
    Tool: Bash / project test runner
    Preconditions: Có session trước đó chứa summary ngắn và query follow-up hợp lệ.
    Steps:
      1. Ghi session memory cho `user_id/session_id` với `topic_summary`, `last_cited_documents`, `last_cited_chunk_ids` và `policy_version/index_version` tham chiếu tới một tài liệu đã hỏi trước đó.
      2. Chạy follow-up query qua graph.
      3. Assert graph dùng session memory để rewrite/ngầm làm rõ query và vẫn tạo evidence bundle hợp lệ.
      4. Assert output cuối vẫn có citation từ evidence hiện tại.
    Expected Result: Session memory chỉ giúp continuity, không thay evidence.
    Evidence: .omo/evidence/task-9-session-context.txt

  Scenario: session memory hết TTL thì graph vẫn hoạt động an toàn
    Tool: Bash / project test runner
    Preconditions: Có session memory đã expire hoặc không tồn tại.
    Steps:
      1. Chạy follow-up query khi session memory đã hết TTL.
      2. Assert graph không crash và fallback về flow retrieval chuẩn.
      3. Assert không có dữ liệu session cũ bị dùng lại.
    Expected Result: Hết TTL không làm sai quyền hoặc sai ngữ cảnh.
    Evidence: .omo/evidence/task-9-session-ttl.txt

  Scenario: cited chunk refs hợp lệ được ưu tiên fetch-by-id trước vector search
    Tool: Bash / project test runner
    Preconditions: Có session memory chứa `last_cited_chunk_ids` hợp lệ và user vẫn trong đúng scope.
    Steps:
      1. Chạy follow-up query kiểu "giải thích kỹ hơn đoạn đó".
      2. Assert graph thử lookup/fetch các cited chunk ids trước.
      3. Assert nếu evidence từ cited refs đủ thì không cần vector search rộng.
      4. Assert nếu cited refs không đủ hoặc stale thì graph fallback sang vector retrieval.
    Expected Result: Cơ chế memory tối ưu retrieval nhưng vẫn an toàn và grounded.
    Evidence: .omo/evidence/task-9-fetch-by-id.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add langgraph query flow`
  - Pre-commit: graph integration tests

- [ ] 10. Implement answer generation + citation enforcement

  **Việc cần làm**:
  - Tạo answer generator chỉ dùng authorized evidence bundles.
  - Bắt buộc citation trong câu trả lời.
  - Có explicit response cho:
    - insufficient evidence
    - insufficient permission
    - unsupported scope
  - Giữ generation tách khỏi retrieval/policy.
  - Cho phép dùng session summary để làm rõ follow-up wording, nhưng factual claims chỉ được lấy từ authorized evidence bundle.
  - Validate citation ids/page/section metadata trước khi return response.
  - Chốt answer LLM riêng, tách khỏi embedding model và auxiliary model.
  - Tôn trọng output token reserve và context budget trước khi sinh câu trả lời.

  **Không được làm**:
  - Không trả lời bằng “trí nhớ” không citation
  - Không fabricate citation
  - Không lộ hidden chunk qua fallback text

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Kiểm soát grounded answer và answer policy.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 5
  - **Blocks**: 11-13
  - **Blocked By**: 9

  **References**:
  - Evidence bundle từ task 8
  - Citation metadata từ task 1 và 5

  **Gợi ý file cho bước này**:
  - `app/agentic/generation/__init__.py`
  - `app/agentic/generation/citation_policy.py`
  - `app/agentic/generation/generate_answer.py`
  - `app/agentic/generation/prompts.py`
  - `app/agentic/adapters/llm/__init__.py`
  - `app/agentic/adapters/llm/base.py`
  - `app/agentic/adapters/llm/default_llm.py`
  - `tests/unit/ai/test_generation.py`

  **Acceptance Criteria**:
  - [ ] Answer có citation từ authorized sources.
  - [ ] Query thiếu evidence trả explicit insufficient-evidence.
  - [ ] Query thiếu quyền trả explicit insufficient-permission.
  - [ ] Session summary có thể hỗ trợ rewrite/follow-up wording nhưng không tạo ra factual claim ngoài evidence bundle.
  - [ ] Query yêu cầu dữ liệu ngoài indexed evidence, ví dụ dữ liệu DB realtime/reporting, phải trả unsupported scope hoặc insufficient evidence trong MVP.
  - [ ] Citation validator reject citation không nằm trong authorized evidence bundle.
  - [ ] Answer LLM config tách biệt với embedding model config.
  - [ ] Output token reserve và max context tokens được enforce trước khi gọi LLM.

  **QA Scenarios**:
  ```
  Scenario: grounded answer có citation
    Tool: Bash / project test runner
    Preconditions: Có authorized evidence bundle.
    Steps:
      1. Chạy answer generation với query grounded.
      2. Assert response cite source/page/section.
      3. Assert không có factual claim uncited.
    Expected Result: Answer grounded và citation-backed.
    Evidence: .omo/evidence/task-10-grounded.txt

  Scenario: query không đủ evidence bị từ chối trả lời
    Tool: Bash / project test runner
    Preconditions: Query không có authorized supporting evidence.
    Steps:
      1. Chạy answer generation với unsupported query.
      2. Assert response nói insufficient evidence.
    Expected Result: Hệ thống không hallucinate.
    Evidence: .omo/evidence/task-10-no-evidence.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add citation-grounded answers`
  - Pre-commit: answer-policy tests

- [ ] 11. Implement audit logging

  **Việc cần làm**:
  - Log các event:
    - source ingestion
    - parse success/failure
    - retrieval access
    - deny
    - answer generation summary
    - session memory write/expire nếu có
  - Ghi lại:
    - user
    - source/document
    - decision
    - timestamp
    - memory policy / TTL summary khi liên quan
  - Không log raw restricted content mặc định
  - Không dùng session memory làm nguồn audit thay cho DB audit

  **Không được làm**:
  - Không bỏ qua deny events
  - Không log sensitive payloads mặc định
  - Không couple audit trực tiếp vào answer text builder

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Cross-cutting concern quan trọng cho enterprise AI.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 6
  - **Blocks**: 12, 13 và final verification
  - **Blocked By**: 6, 8, 10

  **References**:
  - Access decision outputs task 6
  - Runtime graph outputs task 9-10

  **Gợi ý file cho bước này**:
  - `app/agentic/audit/__init__.py`
  - `app/agentic/audit/log_rag_event.py`
  - `tests/unit/ai/test_audit.py`

  **Acceptance Criteria**:
  - [ ] Ingest/retrieve/deny events đều được log.
  - [ ] Log có user, source/document, decision, timestamp.
  - [ ] Không log sensitive payload mặc định.
  - [ ] Session memory write/expire events (nếu có) chỉ log metadata an toàn, không log raw restricted content.

  **QA Scenarios**:
  ```
  Scenario: retrieval thành công sinh audit event
    Tool: Bash / project test runner
    Preconditions: Có authorized query và document.
    Steps:
      1. Chạy một retrieval qua pipeline.
      2. Assert có audit event với user/source/decision.
    Expected Result: Access thành công được audit.
    Evidence: .omo/evidence/task-11-success.txt

  Scenario: deny vẫn sinh audit event nhưng không lộ payload
    Tool: Bash / project test runner
    Preconditions: Có restricted document và unauthorized user.
    Steps:
      1. Chạy denied retrieval.
      2. Assert audit event ghi nhận deny và reason.
      3. Assert log không chứa raw restricted content.
    Expected Result: Deny được audit an toàn.
    Evidence: .omo/evidence/task-11-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add audit logging`
  - Pre-commit: audit tests

- [ ] 12. Implement LangSmith observability layer

  **Việc cần làm**:
  - Thêm module `app/agentic/observability/` để cấu hình LangSmith tracing cho LangGraph runs.
  - Gắn run metadata an toàn cho các node quan trọng: query type, role/scope summary, node name, branch chosen, retrieval count, filtered count, answer status, latency.
  - Thêm redaction helper để không gửi raw restricted content, PII, salary/legal/security-sensitive data lên LangSmith mặc định.
  - Trace các nhánh answered / denied / insufficient_evidence để debug graph flow.
  - Tách rõ LangSmith observability khỏi audit log nội bộ.
  - Đảm bảo telemetry mặc định chỉ nhận metadata đã redact, không nhận raw prompt/evidence trừ khi bật debug có kiểm soát.
  - Cung cấp cờ config bật/tắt tracing riêng, không ảnh hưởng logic production.

  **Không được làm**:
  - Không dùng LangSmith thay audit log nội bộ.
  - Không gửi raw restricted chunks hoặc PII lên trace mặc định.
  - Không làm business logic phụ thuộc vào LangSmith.
  - Không fail request production chỉ vì LangSmith unavailable.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Observability cho agent flow cần đúng boundary và bảo vệ dữ liệu nhạy cảm.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 6
  - **Blocks**: 13 và final verification
  - **Blocked By**: 9, 10, 11

  **References**:
  - LangGraph query flow task 9
  - Answer status task 10
  - Audit logging task 11
  - Access decision task 6

  **Gợi ý file cho bước này**:
  - `app/agentic/observability/__init__.py`
  - `app/agentic/observability/langsmith_config.py`
  - `app/agentic/observability/trace_helpers.py`
  - `app/agentic/observability/run_metadata.py`
  - `app/agentic/observability/redaction.py`
  - `tests/unit/ai/test_observability.py`
  - Có thể sửa `app/agentic/orchestration/rag_graph.py` để gắn trace metadata/redaction hooks

  **Acceptance Criteria**:
  - [ ] LangSmith tracing có thể bật/tắt qua config.
  - [ ] LangGraph run trace ghi nhận node flow, branch, answer status, latency, retrieval/filter counts.
  - [ ] Trace payload mặc định không chứa raw restricted chunks, PII, hoặc full prompt.
  - [ ] Redaction helper có test cho prompt/evidence/memory metadata.
  - [ ] Redaction mặc định không gửi raw restricted content hoặc PII lên LangSmith.
  - [ ] Audit log nội bộ vẫn tồn tại độc lập và không phụ thuộc LangSmith.
  - [ ] Trace metadata cho session memory chỉ ở mức `session_id`/TTL/turn count an toàn, không chứa raw sensitive content mặc định.

  **QA Scenarios**:
  ```
  Scenario: LangSmith trace ghi nhận flow answered với metadata an toàn
    Tool: Bash / project test runner
    Preconditions: Có LangGraph flow test và LangSmith tracing bật ở chế độ test/mock.
    Steps:
      1. Chạy query authorized qua graph.
      2. Assert trace/run metadata có node names, branch answered, retrieval_count, filtered_count, answer_status.
      3. Assert trace không chứa raw chunk text restricted hoặc PII.
    Expected Result: Có trace hữu ích để debug nhưng đã redact dữ liệu nhạy cảm.
    Evidence: .omo/evidence/task-12-langsmith-answered.txt

  Scenario: LangSmith trace ghi nhận deny branch nhưng không thay audit log
    Tool: Bash / project test runner
    Preconditions: Có restricted document và unauthorized user.
    Steps:
      1. Chạy denied query qua graph.
      2. Assert LangSmith/mock trace ghi branch denied và deny reason dạng metadata an toàn.
      3. Assert audit log nội bộ vẫn ghi deny event độc lập.
    Expected Result: Observability và audit cùng tồn tại nhưng không phụ thuộc nhau.
    Evidence: .omo/evidence/task-12-langsmith-deny.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add langsmith observability`
  - Pre-commit: observability/redaction tests

- [ ] 13. Implement extension boundary cho future sources và adapters

  **Việc cần làm**:
  - Chốt boundary để sau này thêm:
    - OCR
    - XLSX
    - PPTX
    - Notion
    - Confluence
    - DB/API records (deferred after MVP)
    - model provider mới
    - vector DB mới
    - storage backend mới
    - session/memory store mới
    - tool mới cho query DB/reporting (deferred after MVP)
  - Document rõ cách một adapter/tool mới cắm vào pipeline
  - Bảo đảm thêm source/adapter/memory store/tool mới không cần sửa contract lõi

  **Không được làm**:
  - Không implement future connectors ở v1
  - Không biến hệ thống thành plugin zoo quá sớm
  - Không nới scope v1 ra ngoài PDF/DOCX

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Boundary này quyết định khả năng mở rộng lâu dài.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 7
  - **Blocks**: final verification
  - **Blocked By**: 12

  **References**:
  - Toàn bộ contracts và pipeline từ task 1-12

  **Gợi ý file cho bước này**:
  - `app/agentic/adapters/parsers/base.py` (hoàn thiện extension contract nếu chưa đủ)
  - `app/agentic/ingestion/source_registry.py` (đảm bảo registry mở rộng được)
  - `app/agentic/parsing/parser_registry.py` (đảm bảo registry mở rộng được)
  - `tests/unit/ai/test_extension_boundary.py`
  - Có thể thêm `app/agentic/README.md` nếu executor cần tài liệu kỹ thuật ngắn trong repo; nếu không, ghi chú trong test/contract là đủ.

  **Acceptance Criteria**:
  - [ ] Source/adapter mới có thể được thêm qua boundary đã định nghĩa.
  - [ ] Pipeline stages giữ nguyên khi thêm source mới.
  - [ ] Có tài liệu/interface note chỉ rõ điểm cắm adapter mới.
  - [ ] Có guideline rõ để thêm session/memory store mới mà không đổi LangGraph flow hoặc retrieval policy lõi.
  - [ ] Có ghi chú deferred rằng DB/API tools sau MVP phải đi qua whitelist và không dùng raw SQL từ graph.

  **QA Scenarios**:
  ```
  Scenario: mock adapter mới đi qua boundary mà không đổi contract lõi
    Tool: Bash / project test runner
    Preconditions: Có mock adapter contract.
    Steps:
      1. Tạo mock adapter theo interface đã định nghĩa.
      2. Assert mock adapter đi qua pipeline mà không sửa core contracts.
    Expected Result: Boundary đủ sạch để mở rộng.
    Evidence: .omo/evidence/task-13-mock-adapter.txt

  Scenario: v1 chỉ active PDF/DOCX adapters
    Tool: Bash / project test runner
    Preconditions: Có danh sách adapter đăng ký.
    Steps:
      1. Inspect adapter registry.
      2. Assert chỉ PDF/DOCX active mặc định trong v1.
    Expected Result: Future adapters chưa bị activate.
    Evidence: .omo/evidence/task-13-v1-scope.txt

  Scenario: memory store mới cắm được qua boundary mà không đổi core flow
    Tool: Bash / project test runner
    Preconditions: Có mock session store theo interface memory/session adapter.
    Steps:
      1. Tạo mock session store mới theo interface đã định nghĩa.
      2. Gắn mock store vào graph/session layer.
      3. Assert LangGraph flow và retrieval policy lõi không phải sửa.
    Expected Result: Memory layer mở rộng được mà không phá core pipeline.
    Evidence: .omo/evidence/task-13-memory-boundary.txt
  ```

  **Commit**: YES
  - Message: `feat(rag): add extension boundary`
  - Pre-commit: boundary tests

---

## Final Verification Wave (bắt buộc sau khi xong toàn bộ implementation tasks)

- [ ] F1. **Kiểm tra end-to-end toàn pipeline** — `oracle`
  Đọc toàn bộ implementation. Xác minh PDF/DOCX đi hết pipeline: ingest → parse → normalize → chunk → policy tag → index → retrieve → LangGraph → answer → audit → LangSmith trace.

  **Acceptance Criteria**:
  - [ ] PDF fixture đi hết pipeline end-to-end.
  - [ ] DOCX fixture đi hết pipeline end-to-end.
  - [ ] Mỗi stage đều có evidence thật, không phải stub.
  - LangSmith trace/mock trace ghi nhận flow an toàn và không thay thế audit log nội bộ.

  Output: `Pipeline Stages [N/N] | Evidence [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Kiểm tra authorization leak** — `unspecified-high`
  Test với identity kiểu admin/manager/employee. Xác minh unauthorized user không retrieve được chunk restricted và không leak qua answer text, citations, logs, metadata, session memory hoặc Redis cache/session layer.

  **Acceptance Criteria**:
  - [ ] Authorized identity chỉ thấy chunk trong scope.
  - [ ] Unauthorized identity không thấy restricted content ở bất kỳ output nào.
  - [ ] Tất cả deny path đều có reason và audit event.
  - [ ] Session memory/cache không bypass retrieval-time authorization hoặc citation enforcement.

  Output: `Access Tests [N/N] | Leak Checks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F3. **Regression / quality review** — `unspecified-high`
  Chạy test/build/type-check phù hợp. Review xem có parser-specific coupling, uncited answer path, duplicate indexing path, unsafe logging path, unsafe LangSmith tracing path hay không.

  **Acceptance Criteria**:
  - [ ] Unit/integration/type/build checks pass.
  - [ ] Không có parser-specific coupling rò vào contract lõi.
  - [ ] Không còn path uncited answer / duplicate indexing / unsafe logging / unsafe LangSmith tracing.

  Output: `Tests [PASS/FAIL] | Build [PASS/FAIL] | Quality [PASS/FAIL] | VERDICT`

- [ ] F4. **Kiểm tra fidelity với scope đã chốt** — `deep`
  So sánh implementation với plan này. Xác minh v1 vẫn chỉ PDF/DOCX, LangGraph vẫn fixed, các adapter khác vẫn replaceable, không creep sang OCR/Notion/XLSX/DB hoặc CRUD/admin không liên quan, và DB/tool layer vẫn là deferred item ngoài MVP.

  **Acceptance Criteria**:
  - [ ] Active adapters của v1 chỉ là PDF text-based và DOCX.
  - [ ] OCR/XLSX/PPTX/Notion/Confluence/DB/API chỉ tồn tại ở extension notes/boundary.
  - [ ] Implementation bám đúng thứ tự pipeline và không scope creep.

  Output: `Scope [PASS/FAIL] | Sequential Build [PASS/FAIL] | Creep [CLEAN/N issues] | VERDICT`

---

## Commit Strategy

- **1**: `feat(rag): add core contracts and ingestion foundation`
- **2**: `feat(rag): add pdf docx parsing and chunk pipeline`
- **3**: `feat(rag): add access-controlled retrieval and langgraph flow`
- **4**: `feat(rag): add grounded answers audit langsmith and extension boundary`

---

## Deferred after MVP

- DB/tool layer cho action history, snapshot và aggregation
- DB/API record sources
- Tool routing trong LangGraph
- Query whitelist/use-case layer cho backend nghiệp vụ
- OCR, XLSX, PPTX, Notion, Confluence

---

## Success Criteria

### Verification Commands
```bash
# executor chọn theo stack thực tế khi triển khai
```

### Final Checklist
- PDF/DOCX ingest end-to-end
- Role-aware retrieval chặn unauthorized content
- LangGraph là orchestration fixed choice
- Model/vector DB/parser/storage đổi được qua adapter/config
- Mỗi capability chính trong MVP chỉ có một concrete adapter mặc định.
- Answer luôn có citation hoặc deny/no-evidence rõ ràng
- Audit log ghi lại access decisions
- LangSmith trace/debug layer hoạt động với redaction và không thay audit log nội bộ
