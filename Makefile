.PHONY: up down seed test test-unit test-integration lint fmt help

help:
	@echo "Available targets:"
	@echo "  up           - Build and start Docker services (api + db)"
	@echo "  down         - Stop and remove Docker services"
	@echo "  seed         - Seed database with roles, permissions, demo users"
	@echo "  test         - Run all tests (unit + integration)"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint         - Run ruff linter"
	@echo "  fmt          - Run ruff formatter"

up:
	docker compose up --build -d

down:
	docker compose down -v

seed:
	export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/masterop" && \
	.venv/bin/python -m app.infrastructure.database.seed

test: test-unit test-integration

test-unit:
	.venv/bin/pytest tests/unit/ -v

test-integration:
	export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/masterop" && \
	.venv/bin/pytest tests/integration/ -v

lint:
	.venv/bin/ruff check app/ tests/

fmt:
	.venv/bin/ruff format app/ tests/
