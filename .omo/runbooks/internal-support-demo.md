# Internal Support Bot Demo Runbook

## Overview

This runbook demonstrates the internal support chatbot - a minimal RAG system that answers questions from indexed internal documents while maintaining session context during active conversations.

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** running with pgvector extension
3. **Dependencies** installed: `pip install -r requirements.txt`
4. **Database** initialized: `alembic upgrade head`
5. **Environment variables** configured in `.env`

## Quick Start

### 1. Start the Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: `curl http://localhost:8000/health` → should return `{"status": "ok"}`

### 2. Seed Demo Data

```bash
python scripts/agentic-demo-seed.py
```

Expected output:
```
✓ Created demo document: demo-doc-vacation-policy (Vacation Policy)
✓ Created 3 chunks for demo-doc-vacation-policy
✓ Created demo document: demo-doc-expense-reimbursement (Expense Reimbursement Policy)
✓ Created 2 chunks for demo-doc-expense-reimbursement
Successfully seeded 2 demo documents with 5 total chunks.
```

### 3. Demo Flow

#### Step 1: List Documents (Verify Seeding)

```bash
curl -X GET http://localhost:8000/api/v1/agentic/documents \
  -H "Authorization: Bearer <admin-token>"
```

**Expected:** 2 documents with status `indexed`

#### Step 2: Upload a Document (Admin/Manager Only)

```bash
curl -X POST http://localhost:8000/api/v1/agentic/documents \
  -H "Authorization: Bearer <admin-token>" \
  -F "file=@path/to/document.txt"
```

**Expected:** `{"status": "indexed", "document_id": "...", "filename": "document.txt"}`

#### Step 3: Upload as Employee (Should Fail)

```bash
curl -X POST http://localhost:8000/api/v1/agentic/documents \
  -H "Authorization: Bearer <employee-token>" \
  -F "file=@path/to/document.txt"
```

**Expected:** `403 Forbidden` with message: `"Only admin and manager can upload documents"`

#### Step 4: Ask a Question (Retrieval + Answer)

```bash
curl -X POST http://localhost:8000/api/v1/agentic/chat \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "How many vacation days do I get per year?", "top_k": 3}'
```

**Expected:**
```json
{
  "conversation_id": "...",
  "thread_id": "...",
  "answer": "According to the vacation policy, you get 15 vacation days per year.",
  "status": "answered",
  "cited_chunk_ids": ["chunk-1"],
  "cited_document_ids": ["demo-doc-vacation-policy"],
  "citations": [{"chunk_id": "chunk-1", "document_id": "demo-doc-vacation-policy", "page_number": 1}]
}
```

#### Step 5: Follow-up Question (Session Context)

```bash
curl -X POST http://localhost:8000/api/v1/agentic/chat \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I carry them over to next year?", "top_k": 3}'
```

**Expected:** Answer uses context from previous turn ("them" = "vacation days")

#### Step 6: Empty Retrieval (No Indexed Docs Match)

```bash
curl -X POST http://localhost:8000/api/v1/agentic/chat \
  -H "Authorization: Bearer <user-token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the office wifi password?", "top_k": 3}'
```

**Expected:** `{"status": "insufficient_evidence", "answer": "Insufficient evidence."}`

#### Step 7: Document Status

```bash
curl -X GET http://localhost:8000/api/v1/agentic/documents/<document-id> \
  -H "Authorization: Bearer <user-token>"
```

**Expected:** `{"document_id": "...", "status": "indexed", "filename": "...", "mime_type": "..."}`

### 4. Reset Demo Data

```bash
python scripts/agentic-demo-reset.py
```

Expected output:
```
Deleted 5 chunks for demo document: demo-doc-vacation-policy
Deleted 2 chunks for demo document: demo-doc-expense-reimbursement
Deleted 2 demo documents.
Successfully reset demo data.
```

## Demo Script

### Scenario 1: Happy Path - Upload, Index, Retrieve, Answer

1. Seed demo data
2. Ask: "How many vacation days do I get?"
3. Verify: Answer cites vacation policy document
4. Ask follow-up: "Can I roll them over?"
5. Verify: Answer uses session context

### Scenario 2: Permission Enforcement

1. Try to upload as employee role
2. Verify: 403 Forbidden response

### Scenario 3: Empty Retrieval

1. Ask question not in indexed documents
2. Verify: "Insufficient evidence" response (not hallucinated answer)

### Scenario 4: Session Context

1. Ask: "What are the vacation days?"
2. Ask: "And the expense policy?"
3. Verify: Second answer doesn't confuse topics

## Success Criteria

- ✅ Upload restricted to admin/manager (403 for employee)
- ✅ Documents persist and are indexed
- ✅ Retrieval returns relevant chunks
- ✅ Answers include citations
- ✅ Session context preserved during active conversation
- ✅ Empty retrieval returns safe fallback (no hallucination)
- ✅ Seed/reset commands work repeatably

## Troubleshooting

### Issue: "No module named langgraph"

**Solution:** `pip install langgraph langgraph-checkpoint`

### Issue: "relation 'agentic_documents' does not exist"

**Solution:** `alembic upgrade head`

### Issue: Upload returns 500 Internal Server Error

**Check:** Parser compatibility - only text/plain, PDF, DOCX supported

### Issue: Retrieval returns empty results

**Check:**
1. Document status is `indexed` (not `pending_parse` or `failed`)
2. Chunks exist: `SELECT COUNT(*) FROM agentic_chunks WHERE document_id = '...'`

## Architecture Notes

- **Persistent:** Documents, chunks, metadata (PostgreSQL)
- **Ephemeral:** Session context, checkpoints (in-memory)
- **No long-term conversation memory** - session context exists only during active chat
- **Keyword retrieval** - simple matching, no embeddings (can upgrade to vector search later)

## Next Steps (Out of Scope for Demo)

- Add vector embeddings for semantic search
- Add document update/delete APIs
- Add conversation history persistence
- Add multi-user conversation isolation
- Add advanced answer policies (tone, length, refusal)
