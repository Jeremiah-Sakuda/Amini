# Amini Backend

FastAPI backend for the Amini agentic workflow auditor.

## Development

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn amini_server.main:app --reload --port 8000
```

## Testing

```bash
poetry run pytest -v
```
