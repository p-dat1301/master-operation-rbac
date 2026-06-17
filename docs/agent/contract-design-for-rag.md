# Tư duy thiết kế Contract cho dự án RAG

## Mục tiêu tài liệu

Tài liệu này giúp trả lời 3 câu hỏi:

1. Khi bắt đầu một dự án, phải tư duy thế nào để thiết kế contract?
2. Với dự án RAG thông thường, nên thiết kế contract ra sao?
3. Với dự án RAG có permission như dự án này, contract sẽ khác ở đâu?

Mục tiêu là thiết kế được **contract đủ dùng cho MVP**, không quá mỏng để thiếu kiểm soát, nhưng cũng không quá dày dẫn tới over-engineering.

---

## 1. Contract là gì?

Trong ngữ cảnh dự án AI / RAG, **contract** là mô tả dữ liệu ổn định đi qua các stage của pipeline.

Nói đơn giản:

- stage này nhận dữ liệu gì
- stage này trả dữ liệu gì
- field nào bắt buộc
- field nào optional
- dữ liệu nào tuyệt đối không được thiếu
- trạng thái lỗi nào phải biểu diễn rõ ràng

Contract **không phải** là nơi nhét toàn bộ business logic.
Contract là nơi giữ cho các module nói chuyện với nhau bằng một ngôn ngữ thống nhất.

---

## 2. Tư duy cốt lõi khi thiết kế contract

Đừng bắt đầu bằng câu hỏi:

> "Tôi cần bao nhiêu file contract?"

Hãy bắt đầu bằng câu hỏi:

> **Những sự thật nào phải tồn tại xuyên suốt pipeline?**

Ví dụ với RAG:

- tài liệu này là gì?
- nó đến từ đâu?
- chunk này thuộc document nào?
- citation của chunk nằm ở đâu trong tài liệu gốc?
- query này lấy ra evidence nào?
- answer này dựa trên evidence nào?
- user có được phép nhìn thấy evidence đó không?

Những "sự thật" này chính là nguồn gốc của contract.

---

## 3. Quy trình 7 bước để tự thiết kế contract

## Bước 1 - Xác định output cuối cùng

Đây là bước quan trọng nhất.

Hãy tự hỏi:

> Hệ thống cuối cùng phải trả về cái gì?

Ví dụ với RAG, output cuối thường là:

- câu trả lời
- citation
- trạng thái trả lời thành công hay thất bại
- lý do thất bại nếu có

Ví dụ contract đầu ra:

- `AnswerResult`
- `AnswerCitation`

Nếu output cuối chưa rõ, contract ở giữa sẽ rất dễ bị lan man.

---

## Bước 2 - Đi ngược từ output về các input cần thiết

Muốn có `AnswerResult`, hệ thống cần gì?

Ví dụ:

- query từ user
- evidence đã retrieve
- metadata của chunk
- citation metadata
- trạng thái permission
- model metadata nếu cần audit/debug

Từ đó mới suy ra những contract trung gian cần có.

---

## Bước 3 - Vẽ pipeline dữ liệu trước khi vẽ class

Đừng vội code class ngay.

Hãy viết pipeline dạng text:

```text
source -> parsed -> normalized -> chunked -> indexed -> retrieved -> answered -> audited
```

Sau đó hỏi ở từng bước:

- input là gì?
- output là gì?
- có mất dữ liệu quan trọng nào không?
- có cần chuẩn hóa dữ liệu ở bước này không?

Ví dụ:

- `SourceMetadata`: dữ liệu đầu vào trước parse
- `ParsedDocument`: output sau parse
- `NormalizedDocument`: output sau normalize
- `DocumentChunk`: output sau chunking
- `RetrievalRequest` / `RetrievalOutcome`: dữ liệu retrieval
- `AnswerResult`: output cuối

---

## Bước 4 - Xác định invariant

**Invariant** là điều luôn phải đúng.

Nếu contract không bảo vệ được invariant, contract đó quá yếu.

Ví dụ invariant trong RAG:

- chunk luôn phải có `document_id`
- answer phải có citation hoặc reason rõ ràng
- status phải thuộc tập giá trị hợp lệ
- query không được rỗng

Ví dụ invariant trong permission-based RAG:

- unauthorized chunk không được vào LLM context
- policy metadata không được thiếu ở document/chunk restricted
- deny phải có `reason_code`
- retrieval phải fail closed khi thiếu permission metadata cần thiết

---

## Bước 5 - Tách business truth khỏi vendor detail

Đây là chỗ rất dễ sai khi mới thiết kế contract.

### Business truth
Là dữ liệu thuộc domain của sản phẩm:

- document_id
- chunk_id
- access policy
- citation
- answer status
- user access context

### Vendor detail
Là dữ liệu chỉ thuộc implementation cụ thể:

- tên parser của một thư viện cụ thể
- định dạng filter riêng của Qdrant / pgvector
- payload request riêng của OpenAI / Anthropic
- callback format của LangGraph node runtime

Nguyên tắc:

- contract lõi nên giữ business truth
- vendor detail nên đẩy ra adapter

---

## Bước 6 - Chỉ giữ field thật sự cần cho một stage

Một lỗi phổ biến là nhét quá nhiều field vào cùng một model.

Ví dụ không nên để `DocumentChunk` mang toàn bộ `SourceMetadata` nếu retrieval chỉ cần:

- `source_type`
- `mime_type`

Tương tự, không nên để `AnswerResult` mang raw parser output nếu nó không phục vụ answer/audit.

Rule đơn giản:

> Field nào không phục vụ output, invariant, security, audit hoặc extension boundary thì chưa cần có trong MVP.

---

## Bước 7 - Thiết kế cả happy path lẫn failure path

Rất nhiều thiết kế contract chỉ nghĩ tới đường thành công.

Nhưng hệ thống thật cần biểu diễn cả lỗi.

Ví dụ với RAG:

- `answered`
- `no_evidence`
- `denied`
- `parse_failed`

Nếu không thiết kế failure path sớm, code sau này sẽ phải dùng:

- `None`
- `dict` tự phát
- string reason không thống nhất
- exception khó kiểm soát

---

## 4. Checklist để biết contract có đang tốt không

Một contract tốt thường trả lời được các câu sau:

- Field này có phục vụ pipeline thật không?
- Field này là domain truth hay chỉ là implementation detail?
- Nếu bỏ field này đi, hệ thống có mất một invariant quan trọng không?
- Contract này có giúp fail fast không?
- Contract này có hỗ trợ audit/debug khi có lỗi không?
- Contract này có khiến module khác phụ thuộc chặt vào vendor/framework không?

Nếu trả lời được phần lớn các câu trên, contract đang đi đúng hướng.

---

## 5. Dấu hiệu của over-engineering trong contract

Các dấu hiệu thường gặp:

- enum đã tạo ra nhưng chưa có logic nào dùng
- export model nhưng không có caller thật
- contract tách quá nhỏ dù chưa có stage nào tiêu thụ riêng
- field chỉ thêm vào vì "sau này có thể cần"
- dùng `dict[str, Any]` ở quá nhiều chỗ quan trọng thay vì typed contract
- hoặc ngược lại: typed quá sâu cho những phần chưa chắc tồn tại trong MVP

Rule thực dụng:

> Nếu một contract chưa có role rõ ràng trong pipeline hiện tại, hãy coi nó là candidate để cắt khỏi MVP.

---

## 6. RAG thông thường cần contract gì?

Với một dự án chỉ có RAG cơ bản, mối quan tâm chính là:

- tài liệu đi vào thế nào
- chunk thế nào
- retrieve thế nào
- answer thế nào
- citation có chính xác không

### Contract tối thiểu thường gồm

- `SourceMetadata`
- `ParsedDocument`
- `NormalizedDocument` hoặc một biến thể nhẹ hơn
- `DocumentChunk`
- `RetrievalRequest`
- `RetrievalCandidate` / `RetrievalResult`
- `AnswerResult`
- `AnswerCitation`

### Ưu tiên của RAG thông thường

- retrieval relevance
- citation quality
- chunking quality
- khả năng đổi parser / vector store / model
- latency và chi phí

### Điều chưa nhất thiết cần ở MVP

- audit event chi tiết
- deny status phức tạp
- access policy phức tạp
- user access context

---

## 7. Permission-based RAG khác gì?

Permission-based RAG không chỉ hỏi:

> "Làm sao tìm đúng nội dung nhất?"

mà còn hỏi:

> **"Làm sao chỉ cho model thấy đúng phần người dùng được phép thấy?"**

Đây là khác biệt bản chất.

### Ngoài contract retrieval/answer cơ bản, hệ thống cần thêm:

- `AccessPolicyMetadata`
- `UserAccessContext`
- trạng thái deny rõ ràng trong retrieval/answer
- audit event
- retrieval filter theo permission

### Mối quan tâm chính

- deny-by-default
- không leak unauthorized chunk
- retrieval-time access control
- answer phải phân biệt rõ `no_evidence` và `insufficient_permission`
- audit lại được ai đã hỏi gì và bị chặn vì sao

---

## 8. So sánh trực tiếp: RAG thường vs RAG có permission

| Khía cạnh | RAG thường | RAG có permission |
|---|---|---|
| Mục tiêu chính | Tìm đúng nội dung | Tìm đúng nội dung + không rò dữ liệu |
| User context | Có thể không cần | Bắt buộc |
| Access policy | Thường không có | Bắt buộc |
| Deny state | Ít quan trọng | Rất quan trọng |
| Audit | Có thể nhẹ | Nên có rõ ràng |
| Retrieval filter | Chủ yếu theo relevance | Theo relevance + permission |
| Invariant quan trọng | citation, answer quality | citation, answer quality, authorization safety |

---

## 9. Tư duy thiết kế contract cho dự án này

Dự án này không phải RAG thông thường.
Đây là **permission-based Agentic RAG**.

Vì vậy contract phải xoay quanh 5 câu hỏi:

1. Tài liệu này là gì?
2. Chunk này thuộc tài liệu nào và có citation thế nào?
3. User này là ai trong ngữ cảnh phân quyền?
4. Chunk này có được phép đi vào retrieval result và LLM context không?
5. Nếu bị chặn thì trả gì và audit ra sao?

Nếu contract không trả lời được 5 câu hỏi này, thiết kế vẫn chưa đủ.

---

## 10. Bộ contract MVP gợi ý cho dự án này

Sau khi đơn giản hóa scope permission, bộ contract MVP nên ưu tiên các model sau.

### 10.1. Source

Dùng để mô tả nguồn tài liệu đầu vào.

Ví dụ:

- `SourceType`
- `SourceMetadata`

### 10.2. Document parsing / normalization

Dùng để biểu diễn dữ liệu sau parse và normalize.

Ví dụ:

- `ParsedDocument`
- `NormalizedDocument`
- `CitationMetadata`
- `ContentBlock`

### 10.3. Chunk

Dùng cho indexing / retrieval.

Ví dụ:

- `DocumentChunk`
- `RetrievalCandidate`
- `RetrievalRequest`
- `RetrievalOutcome`

### 10.4. Permission

Dùng cho authorization.

Với scope MVP hiện tại, nên giữ:

- `VisibilityScope.GLOBAL`
- `VisibilityScope.ROLE`
- `VisibilityScope.DEPARTMENT`

và bỏ:

- `OWNER`
- `MANAGER_SUBTREE`

cho tới khi có use case và hierarchy service rõ ràng.

### 10.5. Answer

Dùng để biểu diễn output cuối.

Ví dụ:

- `AnswerCitation`
- `AnswerResult`

Status nên phân biệt rõ:

- `answered`
- `insufficient_evidence`
- `insufficient_permission`

### 10.6. Audit

Nếu có compliance/security, nên giữ:

- `AuditEvent`

nhưng ở mức vừa đủ cho MVP.

---

## 11. Cách suy nghĩ về permission contract cho đúng mức MVP

Đừng bắt đầu bằng tất cả tình huống phức tạp nhất.

Nên đi từ các rule dễ verify nhất:

- global
- role
- department

Lý do:

- dễ hiểu
- dễ kiểm tra
- dễ build retrieval filter
- ít phụ thuộc vào tổ chức/cây phân cấp

Các scope như `owner` hay `manager_subtree` thường kéo theo domain logic lớn hơn nhiều:

- ownership thật sự nghĩa là gì?
- manager subtree tính đến mấy tầng?
- cần org hierarchy service hay không?
- direct manager hay ancestor manager?

Nếu chưa có câu trả lời chắc chắn, không nên đưa vào MVP contract.

---

## 12. Một mẫu tư duy trước khi thêm field mới

Mỗi khi muốn thêm field vào contract, hãy tự hỏi:

1. Field này phục vụ stage nào?
2. Nếu bỏ field này, invariant nào bị mất?
3. Field này thuộc domain hay chỉ là implementation detail?
4. Có đang thêm vì nhu cầu hiện tại hay vì "biết đâu sau này cần"?
5. Field này có khiến model khác phải phụ thuộc chặt hơn không?

Nếu không trả lời rõ được 5 câu này, đừng thêm field đó vào contract lõi.

---

## 13. Áp dụng ngay cho `source_type`, `mime_type`, `RetrievalFilter`

### `source_type`

Nếu hệ thống đã có enum `SourceType`, nên ưu tiên dùng typed enum thay vì `str` ở nơi cần giữ dữ liệu chuẩn hóa.

### `mime_type`

Để `str` là hợp lý vì MIME type là tập giá trị mở.

### `RetrievalFilter`

Nếu chưa có module nào thực sự dùng `RetrievalFilter`, thì nó đang là **placeholder / dead code**.

Với MVP có 2 lựa chọn rõ ràng hơn:

- bỏ `RetrievalFilter`, chỉ giữ `RetrievalRequest.filters`
- hoặc thay `filters: dict[str, Any]` bằng `RetrievalFilter` typed rõ ràng

Không nên giữ cả hai song song quá lâu nếu chưa có use case thật.

---

## 14. Kết luận thực dụng

Nếu chỉ nhớ 4 ý, hãy nhớ 4 ý này:

1. Thiết kế contract bắt đầu từ **output cuối**, không bắt đầu từ danh sách class.
2. Contract phải bảo vệ **invariant quan trọng nhất của hệ thống**.
3. Permission-based RAG cần thêm **policy, user context, deny state, audit** - đây là khác biệt lớn nhất với RAG thường.
4. MVP chỉ nên giữ những contract nào có vai trò thật trong pipeline hiện tại.

---

## 15. Hướng dẫn áp dụng nhanh cho team

Khi bắt đầu module mới, có thể dùng template sau trong buổi design:

### A. Output cuối của module là gì?
- ví dụ: `RetrievalOutcome`

### B. Input tối thiểu là gì?
- ví dụ: query, top_k, user_context, policy metadata

### C. Invariant nào không được phá?
- ví dụ: unauthorized chunk không được đi vào evidence

### D. Failure states là gì?
- ví dụ: no_evidence, denied

### E. Field nào là domain truth?
- ví dụ: document_id, visibility_scope, department_id

### F. Field nào là vendor detail?
- ví dụ: qdrant filter syntax, langgraph runtime config

### G. Có field nào chưa có caller/use case thật không?
- nếu có, cân nhắc bỏ khỏi MVP
