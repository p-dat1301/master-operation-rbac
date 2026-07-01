# Kế hoạch Hybrid Retrieval: LangChain EnsembleRetriever với PGVector + Elasticsearch cho Agentic RAG

## TL;DR

> **Quick Summary**: Nâng cấp retrieval node của LangGraph để dùng **LangChain EnsembleRetriever** gồm **LangChain PGVector retriever** cho semantic similarity và **LangChain Elasticsearch retriever** cho lexical/BM25 search, sau đó trả ranked evidence cho Agentic RAG.
>
> **Deliverables**:
> - LangChain dependencies: `langchain`, `langchain-postgres`, `langchain-elasticsearch`
> - Elasticsearch service + config + index sync
> - LangChain PGVector retriever wired to existing pgvector embeddings
> - LangChain Elasticsearch retriever wired to BM25 lexical index
> - LangChain EnsembleRetriever for hybrid ranking/fusion
> - Tests + benchmark so với baseline SQL `contains(...)`
>
> **Estimated Effort**: Large
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: ES infra → index sync → hybrid retriever → ranking/verification

---

## Context

### Original Request
User wants LangGraph orchestration with retrieve node using **LangChain EnsembleRetriever**, composed of **LangChain PGVector retriever** for similarity search and **LangChain Elasticsearch retriever** for lexical/BM25 search.

### Interview Summary
**Key Discussions**:
- Current implementation is not Elasticsearch-backed; it is pgvector-backed with SQL keyword fallback.
- `app/agentic/adapters/search/elasticsearch_client.py` exists but is empty scaffold.
- Current vector search lives in `app/agentic/adapters/vector_store/pgvector_retrieval_store.py`.
- Current hybrid behavior is semantic search + PostgreSQL `contains(...)`, which is not the requested ES hybrid.

**Research Findings**:
- Embeddings are generated with `intfloat/multilingual-e5-large` and stored in pgvector.
- Retrieval currently uses `cosine_distance` in pgvector plus SQL keyword fallback.
- No ES config/service/wiring exists today.
- Current reranking is lightweight and deterministic; no ES fusion layer exists.

### Metis Review
**Identified Gaps** (addressed):
- Missing ES config/service/adapter/indexing flow.
- Missing explicit sync strategy between pgvector source of truth and Elasticsearch derived index.
- Missing measurable acceptance criteria for hybrid quality/latency.
- Missing fallback and operational controls for ES downtime.
- Missing real lexical search backend; SQL contains is not a replacement for BM25.

---

## Work Objectives

### Core Objective
Implement a LangGraph retrieve node backed by **LangChain EnsembleRetriever**, combining **LangChain PGVector retriever** for semantic similarity and **LangChain Elasticsearch retriever** for BM25 lexical search, while preserving access-control and citation behavior.

### Concrete Deliverables
- LangChain retriever dependencies added and version-pinned.
- Elasticsearch runtime service added to local/dev infra.
- ES index mapping and reindex/sync path for chunk text + metadata.
- LangChain PGVector retriever configured against existing pgvector data.
- LangChain Elasticsearch retriever configured against ES BM25 index.
- LangChain EnsembleRetriever wired into LangGraph retrieve node through DI, not router.
- Tests and benchmarks proving LangChain hybrid retrieval works and degrades safely.

### Definition of Done
- [ ] A query can be answered via **pgvector semantic retrieval** + **Elasticsearch lexical retrieval** fused into one ranked candidate list.
- [ ] Elasticsearch can be disabled and the system falls back to vector-only retrieval.
- [ ] Existing citations/access control behavior still passes.
- [ ] Hybrid retrieval has automated tests and benchmark evidence versus baseline SQL `contains(...)`.
- [ ] Plan uses `.omo/plans/` path and is executable by `/start-work`.

### Must Have
- Preserve existing chunk/embedding pipeline as source of truth.
- Keep pgvector semantic search active.
- Add Elasticsearch as a lexical/BM25 retrieval source through LangChain Elasticsearch retriever.
- Add pgvector semantic retrieval through LangChain PGVector retriever.
- Make EnsembleRetriever fusion deterministic and testable.
- Keep access-control checks in the retrieval pipeline.
- Add graceful fallback when Elasticsearch is unavailable.

### Must NOT Have
- Do not change embedding model or vector dimension.
- Do not replace pgvector with Elasticsearch.
- Do not put retrieval logic in `router.py`.
- Do not add query-expansion/synonyms/multi-modal search in this plan.
- Do not refactor unrelated auth/session flows.
- Do not treat SQL `contains(...)` as the final lexical backend.

---

## Spec / Architecture Notes

### Current Architecture Baseline
- LangGraph orchestration already exists in the codebase.
- Current semantic retrieval uses a custom pgvector retrieval store:
  - `app/agentic/adapters/vector_store/pgvector_retrieval_store.py`
- Current retrieval orchestration boundary is:
  - `app/agentic/pipeline/retrieval/core.py`
- Current DI wiring is:
  - `app/di/agentic.py`
- Elasticsearch scaffold exists but is empty:
  - `app/agentic/adapters/search/elasticsearch_client.py`
- LangChain retriever abstractions are not yet wired.

### Intended Architecture
```text
LangGraph orchestration
  └── retrieve node
        └── LangChain EnsembleRetriever
              ├── LangChain PGVector retriever
              │     └── pgvector (PostgreSQL)
              └── LangChain Elasticsearch retriever
                    └── Elasticsearch BM25 index
```

- **Semantic layer**: LangChain PGVector retriever over existing pgvector embeddings.
- **Lexical layer**: LangChain Elasticsearch retriever over ES BM25 index.
- **Fusion layer**: LangChain EnsembleRetriever as the hybrid retriever.
- **Ranking layer**: EnsembleRetriever ranking + deterministic post-filtering where needed.
- **Fallback layer**: vector-only retrieval if ES fails or is disabled.

### Spec Framework Integration
- **Detected Framework**: None
- No OpenSpec / Spec Kit detected for this change.
- Use existing plan tasks and `/start-work` for execution.

---

## Verification Strategy (MANDATORY)

> **ZERO HUMAN INTERVENTION** - all verification must be agent-executed.

### Test Decision
- **Infrastructure exists**: YES, partial
- **Automated tests**: Tests-after + integration tests for ES path
- **Framework**: pytest
- **Benchmarking**: compare ES hybrid vs current SQL `contains(...)` baseline

### QA Policy
Every task must include agent-executed QA scenarios with exact commands and evidence paths.

- **Backend/API**: use `curl` or direct Python client calls
- **Integration**: run Elasticsearch container and pytest integration suite
- **Retrieval logic**: run unit tests for fusion/ranking behavior
- **Fallback**: simulate ES unavailability and verify graceful degradation

### Evidence
- Save command outputs, test logs, and benchmark summaries in `.omo/evidence/`.

---

## Execution Strategy

### Parallel Execution Waves

#### Wave 1 — LangChain + Elasticsearch foundation
Focus: dependencies, config, ES service, and retriever prerequisites.

#### Wave 2 — Index sync + retriever setup
Focus: feed chunk data into ES and configure LangChain PGVector / Elasticsearch retrievers.

#### Wave 3 — EnsembleRetriever wiring
Focus: LangChain EnsembleRetriever inside LangGraph retrieve node.

#### Wave 4 — Verification + fallback hardening
Focus: tests, benchmark, ES-down scenarios, and final wiring validation.

---

## TODOs

- [x] 1. `requirements.txt`, `app/core/config.py`, `.env.example`: Add LangChain dependencies, Elasticsearch settings, and retrieval feature flag - expect LangChain packages + runtime config

  **What to do**:
  - Add `langchain`, `langchain-postgres`, `langchain-elasticsearch` to `requirements.txt` with pinned versions.
  - Add ES connection settings, index name, and feature flag for enabling hybrid retrieval in config.
  - Keep defaults safe for local/dev.

  **Must NOT do**:
  - Do not change unrelated config keys.
  - Do not add ES-specific logic to router code.
  - Do not use unpinned or `latest` tags for LangChain packages.

  **Recommended Agent Profile**:
  - **Category**: quick
    - Reason: small config-focused change.
  - **Skills**: []
    - No specialized skill required.

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocks**: ES service wiring, DI conditionals, adapter config.
  - **Blocked By**: None

  **References**:
  - `app/core/config.py` - existing RAG config pattern to extend.
  - `.env.example` - example runtime variables.

  **Acceptance Criteria**:
  - [ ] `langchain`, `langchain-postgres`, `langchain-elasticsearch` added to requirements.txt with exact versions.
  - [ ] Config exposes ES host/port/index/flag values.
  - [ ] App still boots with ES disabled.
  - [ ] `pytest` config-related unit tests pass.

  **QA Scenarios**:
  ```
  Scenario: ES config loads with defaults
    Tool: Bash
    Preconditions: `.env` does not define ES vars
    Steps:
      1. Import settings in a Python shell.
      2. Read ES config fields.
    Expected Result: Settings load and ES flag defaults to disabled.
    Evidence: .omo/evidence/task-1-es-config-defaults.txt

  Scenario: Invalid ES connection settings fail fast
    Tool: Bash
    Preconditions: Set malformed ES URL
    Steps:
      1. Start app config import.
      2. Inspect raised validation error.
    Expected Result: Clear config error, no silent fallback.
    Evidence: .omo/evidence/task-1-es-config-invalid.txt
  ```

- [x] 2. `docker-compose.yml` and local infra: Add Elasticsearch service for dev/test hybrid retrieval - expect runnable ES container

  **What to do**:
  - Add Elasticsearch service, port, volume, and healthcheck.
  - Keep current pgvector Postgres service intact.

  **Must NOT do**:
  - Do not remove pgvector Postgres.
  - Do not couple ES startup to API startup without healthcheck.

  **Recommended Agent Profile**:
  - **Category**: quick
    - Reason: infra wiring is localized.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: After Task 1 completes
  - **Parallel Group**: Wave 1 (can run alongside Task 3 after Task 1)
  - **Blocks**: Tasks 3, integration benchmarks
  - **Blocked By**: Task 1

  **References**:
  - `docker-compose.yml` - current service topology.
  - Elasticsearch official Docker docs - healthcheck and JVM heap guidance.

  **Acceptance Criteria**:
  - [ ] `docker compose up` starts ES successfully.
  - [ ] ES health endpoint becomes ready before retrieval tests.
  - [ ] PGVector DB service remains unchanged.

  **QA Scenarios**:
  ```
  Scenario: Elasticsearch container starts and reports healthy
    Tool: Bash
    Preconditions: Docker available
    Steps:
      1. Run `docker compose up -d elasticsearch`.
      2. Query health endpoint.
    Expected Result: ES returns healthy status.
    Evidence: .omo/evidence/task-2-es-health.txt

  Scenario: API remains runnable with ES stopped
    Tool: Bash
    Preconditions: ES container stopped
    Steps:
      1. Start API service.
      2. Verify app boots.
    Expected Result: App starts and falls back to vector-only mode if configured.
    Evidence: .omo/evidence/task-2-api-without-es.txt
  ```

- [x] 3. Set up LangChain Elasticsearch retriever and ES index mapping - expect LangChain ElasticsearchRetriever ready for lexical search

  **What to do**:
  - Configure LangChain `ElasticsearchRetriever` from `langchain-elasticsearch` package.
  - Define ES index mapping/settings for BM25 search on chunk text + metadata.
  - Provide index creation/update helpers for the ingestion pipeline to use.
  - Test that the retriever can query ES and return documents in LangChain `Document` format.

  **Must NOT do**:
  - Do not build a custom ES client adapter from scratch; use LangChain's abstraction.
  - Do not put hybrid fusion logic here; that belongs in EnsembleRetriever.
  - Do not make this file own retrieval ranking.

  **Recommended Agent Profile**:
  - **Category**: unspecified-high
    - Reason: adapter design impacts retrieval architecture and wiring.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: After Tasks 1 and 2 complete
  - **Parallel Group**: Wave 1 completion
  - **Blocks**: Tasks 4, 5, 6
  - **Blocked By**: Tasks 1 and 2

  **References**:
  - LangChain Elasticsearch retriever docs - `ElasticsearchRetriever` setup and configuration.
  - `langchain-elasticsearch` package docs - index mapping and BM25 query patterns.
  - Elasticsearch Python client docs - underlying client behavior.

  **Acceptance Criteria**:
  - [ ] LangChain `ElasticsearchRetriever` can be instantiated and connects to ES.
  - [ ] ES index mapping supports chunk text and metadata fields.
  - [ ] Retriever returns results in LangChain `Document` format with chunk IDs and scores.

  **QA Scenarios**:
  ```
  Scenario: LangChain ElasticsearchRetriever returns documents from ES
    Tool: Bash
    Preconditions: ES running with indexed test chunks
    Steps:
      1. Instantiate ElasticsearchRetriever with test config.
      2. Call retriever.get_relevant_documents("test query").
      3. Inspect returned Document objects.
    Expected Result: Documents returned with chunk text, metadata, and scores.
    Evidence: .omo/evidence/task-3-langchain-es-retriever.txt

  Scenario: Retriever returns empty list when no matches found
    Tool: Bash
    Preconditions: ES running, query has no lexical match
    Steps:
      1. Query ElasticsearchRetriever with nonsense string.
      2. Inspect returned document list.
    Expected Result: Empty list with no exception.
    Evidence: .omo/evidence/task-3-es-empty-search.txt
  ```

- [x] 4. `app/agentic/pipeline/indexing/core.py` and ES sync helpers: Index chunk text/metadata into Elasticsearch during ingestion - expect derived lexical index kept in sync

  **What to do**:
  - Extend indexing flow so chunks are written to ES as a derived index.
  - Keep pgvector as the source of truth for semantic storage.
  - Define reindex/backfill path from stored chunks.
  - ES indexing error policy: log error but do NOT fail ingestion; pgvector remains source of truth.

  **Must NOT do**:
  - Do not change chunking/embedding semantics.
  - Do not block ingestion if ES write fails; log warning and continue with vector-only indexing.

  **Recommended Agent Profile**:
  - **Category**: deep
    - Reason: indexing sync must be safe and fault-tolerant.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential within Wave 2)
  - **Parallel Group**: Wave 2 start
  - **Blocks**: Tasks 5 and 6
  - **Blocked By**: Task 3

  **References**:
  - `app/agentic/pipeline/indexing/core.py` - current embedding/persist orchestration.
  - `tests/unit/ai/test_indexing.py` - indexing failure/shape patterns.
  - Elasticsearch bulk indexing docs - efficient sync pattern.

  **Acceptance Criteria**:
  - [ ] New chunks are indexed into ES when ingestion succeeds.
  - [ ] ES indexing errors are logged as warnings and do NOT fail ingestion (pgvector write still succeeds).
  - [ ] Reindex/backfill command can rebuild ES index from pgvector-stored chunks.

  **QA Scenarios**:
  ```
  Scenario: Ingest one document and verify ES receives chunk docs
    Tool: Bash
    Preconditions: ES running, sample document available
    Steps:
      1. Run ingestion for sample document.
      2. Query ES for chunk text and metadata.
    Expected Result: Indexed docs appear in ES.
    Evidence: .omo/evidence/task-4-ingest-to-es.txt

  Scenario: ES write failure does not silently corrupt ingestion state
    Tool: Bash
    Preconditions: ES stopped or returns 500
    Steps:
      1. Run ingestion.
      2. Inspect ingestion status/error metadata.
    Expected Result: Failure is visible and policy-compliant.
    Evidence: .omo/evidence/task-4-es-write-failure.txt
  ```

- [x] 5. LangChain PGVector retriever setup: Configure LangChain PGVector retriever against existing pgvector embeddings - expect semantic retriever usable by EnsembleRetriever

  **What to do**:
  - Configure LangChain PGVector retriever using `langchain-postgres` against the existing PostgreSQL/pgvector connection.
  - Map existing chunk IDs, text, metadata, and embeddings into the LangChain retriever contract.
  - Ensure LangChain retriever output can be converted back to the project `RetrievalCandidate` / evidence format.
  - Keep access-control filtering in the retrieval pipeline after documents are retrieved.

  **Must NOT do**:
  - Do not replace pgvector with Elasticsearch.
  - Do not rebuild embeddings or change embedding dimension.
  - Do not move retrieval logic into router.

  **Recommended Agent Profile**:
  - **Category**: quick
    - Reason: mostly wiring preservation and small adjustments.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: After Task 4 (can run alongside other independent Wave 2 tasks)
  - **Parallel Group**: Wave 2 middle
  - **Blocks**: Task 6
  - **Blocked By**: Tasks 3 and 4

  **References**:
  - LangChain PGVector docs from `langchain-postgres` - retriever setup and connection configuration.
  - `app/agentic/adapters/storage/models/agentic_chunk_embedding_model.py` - existing pgvector storage schema.
  - `app/agentic/pipeline/retrieval/core.py` - retrieval orchestration and access checks.
  - `tests/unit/ai/test_pgvector_storage.py` - existing vector search test patterns.

  **Acceptance Criteria**:
  - [ ] LangChain PGVector retriever can retrieve semantically similar chunks from existing pgvector data.
  - [ ] Retrieved LangChain Documents include chunk IDs and citation/access metadata.
  - [ ] Retrieval core still applies access checks and citation requirements.

  **QA Scenarios**:
  ```
  Scenario: LangChain PGVector retriever returns semantic matches
    Tool: Bash
    Preconditions: Embeddings present in pgvector
    Steps:
      1. Instantiate LangChain PGVector retriever with project DB connection.
      2. Call retriever.get_relevant_documents("semantically similar query").
      3. Inspect Document metadata for chunk_id and citation fields.
    Expected Result: Top semantic documents are returned with required metadata.
    Evidence: .omo/evidence/task-5-langchain-pgvector.txt

  Scenario: Unauthorized chunk remains filtered out
    Tool: Bash
    Preconditions: Chunk with restricted access exists
    Steps:
      1. Query as unauthorized user.
      2. Inspect returned evidence.
    Expected Result: Restricted chunk is not returned.
    Evidence: .omo/evidence/task-5-access-filter.txt
  ```

- [x] 6. LangChain EnsembleRetriever setup: Combine PGVector retriever and Elasticsearch retriever - expect hybrid ranked documents from one retriever

  **What to do**:
  - Create LangChain `EnsembleRetriever` with two retrievers:
    - LangChain PGVector retriever for semantic similarity.
    - LangChain Elasticsearch retriever for lexical/BM25 search.
  - Configure retriever weights explicitly, default `PGVector=0.5`, `Elasticsearch=0.5`.
  - Use LangChain's ensemble ranking/fusion behavior as the default hybrid ranking.
  - Add deterministic post-processing only for project-specific filtering: dedup by `chunk_id`, access-control filtering, citation validation.

  **Must NOT do**:
  - Do not build a custom fusion/ranking system unless LangChain output lacks required metadata.
  - Do not introduce a second unrelated retrieval system.
  - Do not add query expansion or synonym logic in this plan.

  **Recommended Agent Profile**:
  - **Category**: unspecified-high
    - Reason: LangChain retriever wiring needs careful integration with project metadata and access filtering.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential after Tasks 4 and 5
  - **Blocks**: Task 7.
  - **Blocked By**: Tasks 4 and 5

  **References**:
  - LangChain `EnsembleRetriever` docs - hybrid retrieval behavior and weights.
  - LangChain PGVector retriever docs - semantic retriever input/output contract.
  - LangChain Elasticsearch retriever docs - lexical retriever input/output contract.
  - `app/agentic/pipeline/retrieval/core.py` - current orchestration boundary and access filtering.

  **Acceptance Criteria**:
  - [ ] EnsembleRetriever is constructed with PGVector and Elasticsearch retrievers.
  - [ ] Retriever weights are explicit and configurable.
  - [ ] Output LangChain Documents preserve chunk IDs, citations, and access metadata.
  - [ ] Final evidence list is deterministic after project-specific post-processing.

  **QA Scenarios**:
  ```
  Scenario: EnsembleRetriever returns hybrid results from both sources
    Tool: Bash
    Preconditions: PGVector and ES contain overlapping test chunks
    Steps:
      1. Instantiate EnsembleRetriever with PGVector and ES retrievers.
      2. Query with text that has both semantic and lexical matches.
      3. Inspect returned LangChain Documents.
    Expected Result: Results include candidates sourced from both retrievers and preserve chunk metadata.
    Evidence: .omo/evidence/task-6-ensemble-hybrid.txt

  Scenario: Duplicate chunk IDs are deduped after EnsembleRetriever output
    Tool: Bash
    Preconditions: Same chunk appears from both PGVector and ES retrievers
    Steps:
      1. Run EnsembleRetriever.
      2. Run project post-processing step.
      3. Inspect final evidence list.
    Expected Result: Each chunk_id appears once in final evidence.
    Evidence: .omo/evidence/task-6-ensemble-dedup.txt
  ```

- [x] 7. DI wiring and LangGraph node integration: Wire LangChain EnsembleRetriever into LangGraph retrieve node - expect hybrid retrieval in production flow

  **What to do**:
  - Wire LangChain EnsembleRetriever (from Task 6) into the LangGraph retrieve node via DI in `app/di/agentic.py`.
  - Construct the retriever hierarchy: EnsembleRetriever → [PGVectorRetriever, ElasticsearchRetriever].
  - Keep router thin; no retrieval implementation in endpoint layer.
  - Respect feature flag for ES enable/disable: if ES is off, use PGVector retriever only.
  - Convert LangChain Document output to project `RetrievalCandidate` format for downstream nodes.

  **Must NOT do**:
  - Do not put EnsembleRetriever construction or business logic in the router.
  - Do not hardcode backend selection in endpoint code.
  - Do not bypass the LangGraph orchestration boundary.

  **Recommended Agent Profile**:
  - **Category**: quick
    - Reason: wiring-only change.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: Task 8.
  - **Blocked By**: Task 6

  **References**:
  - `app/di/agentic.py` - current retrieval DI wiring.
  - `app/agentic/orchestration/nodes/retrieve_evidence.py` - LangGraph retrieve node boundary.
  - `app/presentation/api/v1/agentic/router.py` - API graph entrypoint that should NOT own retrieval construction.
  - LangChain EnsembleRetriever docs - construction and usage patterns.

  **Acceptance Criteria**:
  - [ ] EnsembleRetriever is constructed in DI layer, not in router or node code.
  - [ ] LangGraph retrieve node calls EnsembleRetriever and converts output to project evidence format.
  - [ ] Feature flag controls ES enablement; ES-off mode uses PGVector only.
  - [ ] Router remains thin and only invokes the LangGraph graph, not retrieval details.

  **QA Scenarios**:
  ```
  Scenario: LangGraph retrieve node uses EnsembleRetriever and returns hybrid evidence
    Tool: Bash
    Preconditions: Config valid, ES and PGVector running
    Steps:
      1. Start API.
      2. Send a query to the LangGraph chat endpoint.
      3. Inspect retrieved evidence metadata.
    Expected Result: Evidence includes chunks sourced from both semantic and lexical retrievers.
    Evidence: .omo/evidence/task-7-langgraph-ensemble.txt

  Scenario: API falls back to PGVector-only when ES flag is disabled
    Tool: Bash
    Preconditions: ES disabled in config
    Steps:
      1. Start API.
      2. Run a retrieval query via LangGraph node.
      3. Inspect evidence source.
    Expected Result: Only semantic PGVector results are returned, no ES lexical results.
    Evidence: .omo/evidence/task-7-es-disabled-fallback.txt
  ```

- [x] 8. Tests and benchmarks: Add tests for LangChain retrievers, EnsembleRetriever, and integration with LangGraph - expect proof of correctness and quality

  **What to do**:
  - Add unit tests for LangChain PGVector retriever setup and output format.
  - Add unit tests for LangChain Elasticsearch retriever setup and output format.
  - Add unit tests for EnsembleRetriever construction and hybrid ranking behavior.
  - Add integration tests with real ES container and real pgvector data.
  - Benchmark LangChain ES hybrid retrieval against current SQL `contains(...)` baseline.

  **Must NOT do**:
  - Do not rely only on mocks for the final retrieval integration claim.
  - Do not skip negative-path tests (ES down, empty results, malformed metadata).

  **Recommended Agent Profile**:
  - **Category**: unspecified-high
    - Reason: test coverage must validate architecture and failure behavior.
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Final verification prep
  - **Blocks**: Final review wave.
  - **Blocked By**: Tasks 1-7

  **References**:
  - LangChain testing patterns - retriever unit test examples.
  - `tests/unit/ai/test_pgvector_storage.py` - existing retrieval test style.
  - `tests/unit/ai/test_retrieval.py` - orchestration/failure path coverage.
  - Elasticsearch integration test guidance - container-backed verification.

  **Acceptance Criteria**:
  - [ ] LangChain PGVector retriever tests pass.
  - [ ] LangChain Elasticsearch retriever tests pass.
  - [ ] EnsembleRetriever hybrid ranking tests pass.
  - [ ] Integration tests against real ES + pgvector pass.
  - [ ] Benchmark summary shows ES hybrid recall@10 ≥ SQL baseline + 5% AND p95 latency ≤ baseline + 200ms.

  **QA Scenarios**:
  ```
  Scenario: LangChain retriever unit tests pass
    Tool: Bash
    Preconditions: LangChain packages installed, test fixtures in place
    Steps:
      1. Run pytest for LangChain PGVector retriever tests.
      2. Run pytest for LangChain Elasticsearch retriever tests.
      3. Run pytest for EnsembleRetriever tests.
      4. Inspect pass/fail output.
    Expected Result: All LangChain retriever unit tests pass.
    Evidence: .omo/evidence/task-8-langchain-unit-tests.txt

  Scenario: Integration test with real ES and pgvector
    Tool: Bash
    Preconditions: ES container running, pgvector embeddings present, test corpus loaded
    Steps:
      1. Run integration test that exercises EnsembleRetriever end-to-end.
      2. Verify both semantic and lexical results are returned.
      3. Compare recall/latency against SQL baseline.
    Expected Result: Hybrid retrieval works end-to-end and meets benchmark thresholds.
    Evidence: .omo/evidence/task-8-integration-benchmark.txt
  ```

---

## Final Verification Wave

> Run after all implementation tasks. All reviewers must approve before handoff.

- [x] F1. **Plan Compliance Audit** — `oracle`
  Verify every Must Have is implemented, every Must NOT Have is absent, and evidence files exist. Confirm the plan still matches the requested ES hybrid architecture.

  **Acceptance Criteria**:
  - [ ] All Must Have items have matching implementation evidence.
  - [ ] No Must NOT Have item appears in the diff or runtime flow.
  - [ ] Evidence artifacts for Tasks 1-8 exist.

- [~] F2. **Code Quality Review** — `unspecified-high`
  Run typecheck/lint/tests and inspect changed files for slop, dead code, and incorrect wiring.
  > Blocked: current working tree includes broad unrelated branch changes outside this plan, so clean scope-only quality approval requires branch isolation or explicit user decision on what to exclude.

  **Acceptance Criteria**:
  - [ ] Typecheck, lint, and targeted tests pass.
  - [ ] No `as any`, `@ts-ignore`, empty catches, or dead code in changed files.
  - [ ] No unreviewed scope creep outside the plan.

- [x] F3. **Real Integration QA** — `unspecified-high`
  Bring up Elasticsearch and execute the hybrid retrieval scenarios end-to-end, including failure/fallback cases.

  **Acceptance Criteria**:
  - [x] ES container starts and passes healthcheck.
  - [x] Hybrid retrieval returns merged vector + ES candidates.
  - [x] ES-down fallback path still returns vector-only results.

- [~] F4. **Scope Fidelity Check** — `deep`
  Confirm the implementation matches the revised plan exactly and does not drift into unrelated refactors.
  > Blocked: Current working tree includes 87 changed files with massive scope beyond this plan (frontend/admin UI, RBAC, auth, model deletions, docs deletion). Core hybrid retrieval (Tasks 1-8) is complete, but scope isolation requires user decision on what to commit vs. stash/revert.

  **Acceptance Criteria**:
  - [x] Every task maps 1:1 to implemented files/behavior (for Tasks 1-8).
  - [ ] No unrelated files were modified beyond the plan.
  - [x] No extra retrieval/search architecture was introduced beyond pgvector + Elasticsearch + ranking.

---

## Commit Strategy

- **1**: `feat(agentic): add es hybrid retrieval` - config, infra, adapter, retrieval, tests

---

## Success Criteria

### Verification Commands
```bash
pytest tests/unit/ai/test_pgvector_storage.py -q
pytest tests/unit/ai/test_retrieval.py -q
pytest tests/unit/ai/test_embeddings.py -q
# plus ES integration/benchmark commands added in Task 8
```

### Final Checklist
- [ ] Elasticsearch exists as a real lexical backend.
- [ ] pgvector remains the semantic backend.
- [ ] Hybrid fusion merges both sources.
- [ ] Ranking/rerank is deterministic.
- [ ] Fallbacks and tests prove safe behavior.
- [ ] API contract remains stable.
