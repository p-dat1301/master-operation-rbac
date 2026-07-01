# Draft: document-module

## Requirements (confirmed)
- user_request: lên kế hoạch xây một module document cho dự án
- language: user is communicating in Vietnamese
- current_state: planning only, not implementation
- document_type: tài liệu nội bộ + file người dùng upload
- mvp_scope: CRUD tài liệu + thêm vào pipeline indexing
- access_rule: viewer chỉ đọc; admin và manager được thêm/sửa/xóa
- goal_mode_selected: builder / side project

## Technical Decisions
- workflow: office-hours style discovery first, then convert into a work plan when requirements are clear
- intent_type: build from scratch / mid-sized feature unless later clarified otherwise

## Research Findings
- repo_sdd_frameworks: no openspec/, .specify/, or _bmad/ directories detected via initial repository scan
- pending_research:
  - codebase module pattern scan: bg_d56facd6
  - test infrastructure scan: bg_0bf9e0f0
  - external document-module research: bg_8378b594

## Open Questions
- goal_mode: startup / intrapreneurship / hackathon-demo / open source-research / learning / fun
- document_scope: documents here mean what exactly? internal docs, user-uploaded files, legal documents, product knowledge base, or project attachments?
- primary_users: who will use this module first?
- mvp_boundaries: what must be in v1 and what is explicitly out of scope?
- test_strategy: TDD / tests-after / no automated tests
- user_question: clarify how the modes differ so a choice can be made

## Scope Boundaries
- INCLUDE: planning the document module
- EXCLUDE: implementation at this stage
