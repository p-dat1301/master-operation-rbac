# Internal Support Bot: Story and Demo Criteria

## Story

**Who:** Internal employees across the organization who need quick answers to questions about company policies, procedures, technical documentation, and internal knowledge.

**What:** A conversational support bot that searches uploaded internal documents and returns accurate answers with citations, maintaining context throughout the active chat session.

**Why:** Employees currently spend time searching through scattered internal documentation or waiting for answers from colleagues. The bot provides instant, evidence-based responses that reference the exact source material.

**Expected result:** An employee asks a question, the bot retrieves relevant internal evidence, answers correctly with citations, and continues the conversation with full context until the session ends.

## Demo Flow

The demo proves the bot works end-to-end with real internal documents:

1. **Upload:** Admin uploads an internal policy document (PDF or text file) via `/api/v1/agentic/documents`
2. **Verify:** Check document appears in `/api/v1/agentic/documents` list with "indexed" status
3. **Ask:** Employee sends a question via `/api/v1/agentic/chat` that requires information from the uploaded document
4. **Retrieve:** Bot searches the knowledge base and returns relevant chunks
5. **Answer:** Bot responds with an accurate answer citing specific document sections
6. **Follow-up:** Employee asks a related question that depends on previous context
7. **Context retention:** Bot answers using both the knowledge base and prior conversation context
8. **Session end:** Employee closes the app; conversation context is lost but uploaded documents remain

## Success Criteria

Pass/fail checks that prove the bot works as specified:

### Upload and Indexing
- [ ] Document upload returns `200 OK` with `document_id` and `status: "indexed"`
- [ ] GET `/api/v1/agentic/documents/{document_id}` returns the document metadata
- [ ] Document content is searchable within 30 seconds of upload

### Chat and Retrieval
- [ ] Question about uploaded content returns an answer with `cited_chunk_ids` length > 0
- [ ] Answer text contains information that exists in the uploaded document
- [ ] Answer includes citations that link back to specific document sections
- [ ] Incorrect or hallucinated information (not in the source) fails the test

### Context Retention (Active Session)
- [ ] Follow-up question like "Can you elaborate on that?" or "What about the second point?" references prior answer
- [ ] Bot correctly interprets pronouns and references from earlier in the conversation
- [ ] `thread_id` remains constant across messages in the same conversation

### Context Scope
- [ ] New conversation thread starts with no memory of previous threads
- [ ] Uploaded documents remain available across all conversations (persistent knowledge base)
- [ ] After simulated app restart, bot can still answer questions from uploaded documents
- [ ] After simulated app restart, bot does NOT remember prior conversation turns

## Out of Scope

The following are explicitly excluded from the minimal viable demo:

**Long-term conversation memory:** The bot does NOT remember past conversations after the user closes the app or starts a new session. Once the active chat session ends, only the knowledge base (uploaded documents) persists. Conversation history is ephemeral.

**Multi-session continuity:** Users cannot resume a previous conversation with context intact. Each new session starts fresh, though uploaded documents remain available.

**User preference learning:** The bot does not learn user preferences, writing style, or personalization across sessions.

**Proactive suggestions:** The bot does not suggest questions, anticipate needs, or initiate conversations.

**External integrations:** No connections to Slack, email, ticketing systems, or external knowledge sources. Only uploaded internal documents.

**Advanced reasoning:** No multi-hop reasoning, complex analysis, or decision-making beyond retrieving and summarizing document content.

## Architecture Alignment

This story aligns with the minimal architecture decision:
- **Persistent:** Uploaded documents and their indexed vectors (knowledge base)
- **Ephemeral:** Active chat session context (thread_id, message history)
- **Not stored:** Past conversation threads after session ends

The demo proves the core value: employees get accurate, cited answers from internal knowledge without building a full conversational memory system.
