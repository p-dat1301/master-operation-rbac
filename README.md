# Master Operation

An operations backend built around an explicit RBAC permission matrix, with a document-QA layer that answers questions **only from documents the asking user is allowed to read**.

Permission is not an afterthought bolted onto endpoints here — it is the thing the system is organised around, and it reaches all the way into retrieval.

---

## What it does

**Operations domain** — users, departments, roles, tasks, attendance, leave requests and leave balances, documents, notifications, and an audit log.

**RBAC** — `User → Role → Permission`, with roles and permissions many-to-many through `role_permissions`. The database is the source of truth; a user is loaded once with their role and permission codes resolved into a domain entity, and every later check is a set membership test in memory rather than another query.

```python
User(role_name="manager", permissions={"approve_leave", "view_attendance_dept"})
```

**Permission-aware RAG** — a LangGraph pipeline ingests, chunks, indexes and retrieves documents, with an access-control stage inside the retrieval path. Two users can ask the same question and correctly receive different answers, because the retriever never surfaces a chunk the caller lacks permission for.

**Admin console sync** — menu and i18n definitions are synchronised to the frontend through dedicated contracts and endpoints, so navigation and translations stay driven by backend permissions instead of being duplicated in the client.

---

## Architecture

Clean Architecture, with dependencies pointing inward:

```
app/
├── domain/           entities, repository interfaces, domain services (RBAC rules)
├── application/      use cases, DTOs, ports
├── infrastructure/   SQLAlchemy repositories, security, storage, notifications
├── presentation/     FastAPI routers, schemas, middleware, dependencies
├── agentic/          RAG pipeline, LangGraph orchestration, contracts, adapters
├── di/               composition root
└── core/             configuration and cross-cutting concerns
```

The domain layer knows nothing about FastAPI, SQLAlchemy, or any LLM provider. Swapping the web framework or the model gateway does not reach past `infrastructure/` and `presentation/`.

The agentic layer is split the same way:

```
agentic/
├── pipeline/         ingestion · parsing · chunking · indexing · retrieval
│                     · access_control · answer_policy
├── orchestration/    rag_graph, session flow, evidence handoff, tracing
├── contracts/        typed boundaries between stages
└── adapters/         model gateway and store adapters
```

---

## Stack

**API** — Python · FastAPI · SQLAlchemy 2.0 · Alembic · Pydantic

**Data** — PostgreSQL · Redis · Elasticsearch · MinIO

**AI** — LangGraph · LiteLLM gateway · Langfuse tracing

**Admin** — Angular 21 · Tailwind · Playwright

**Ops** — Docker Compose · Makefile · Postman collection

---

## Running it

```bash
cp .env.example .env     # fill in your own secrets — never commit this file
make up                  # api, llm gateway, postgres, redis, elasticsearch, minio
make seed                # seed roles, permissions and demo data
```

API docs at `http://localhost:8000/docs`.

```bash
make test                # unit + integration
make lint
make fmt
```

---

## Documentation

| Document | Covers |
| --- | --- |
| `docs/rbac-permission-flow.md` | How a permission check travels from database to decision |
| `docs/erd.md` | Entity relationships |
| `docs/use_case_flows.md` | Use case walkthroughs |
| `docs/admin-coverage-matrix.md` | Admin surface coverage |
| `docs/menu-i18n-sync-contract.md` | Menu and translation sync contract |
| `docs/postman-guide.md` | API collection guide |
