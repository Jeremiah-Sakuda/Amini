.PHONY: install dev dev-backend dev-frontend test migrate seed demo

install:
	cd packages/sdk && poetry install
	cd packages/backend && poetry install
	cd packages/frontend && npm install

dev-backend:
	cd packages/backend && poetry run uvicorn amini_server.main:app --reload --port 8000

dev-frontend:
	cd packages/frontend && npm run dev

dev:
	$(MAKE) dev-backend &
	$(MAKE) dev-frontend

test:
	cd packages/sdk && poetry run pytest
	cd packages/backend && poetry run pytest

test-sdk:
	cd packages/sdk && poetry run pytest -v

test-backend:
	cd packages/backend && poetry run pytest -v

migrate:
	cd packages/backend && poetry run alembic upgrade head

migrate-create:
	cd packages/backend && poetry run alembic revision --autogenerate -m "$(msg)"

seed:
	cd packages/backend && poetry run python -m scripts.seed_db

demo:
	cd packages/sdk && poetry run python -m scripts.demo_agent

lint:
	cd packages/sdk && poetry run ruff check .
	cd packages/backend && poetry run ruff check .
	cd packages/frontend && npm run lint
