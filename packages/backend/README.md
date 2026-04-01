# Amini Backend

FastAPI backend for Amini — compliance infrastructure for agentic AI. Handles event ingestion, decision chain reconstruction, policy evaluation, regulatory mapping, audit report generation, and incident response.

## Development

```bash
# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn amini_server.main:app --reload --port 8000
```

## Testing

```bash
poetry run pytest -v
```

## Docker

```bash
docker build -t amini-backend .
docker run -p 8000:8000 -e DATABASE_URL=sqlite+aiosqlite:///./amini.db amini-backend
```

## API Endpoints

### Core
- `GET /health` — Health check
- `GET /ready` — Readiness check
- `POST /api/v1/admin/cleanup` — Trigger data retention cleanup

### Event Ingestion (requires API key)
- `POST /api/v1/events` — Ingest single event
- `POST /api/v1/events/batch` — Ingest event batch

### Sessions & Decisions
- `GET /api/v1/sessions` — List sessions
- `GET /api/v1/sessions/{id}` — Session detail with decision chain
- `GET /api/v1/decisions/{id}` — Decision node detail

### Policy Engine
- `GET /api/v1/policies` — List policy versions
- `POST /api/v1/policies` — Create policy version
- `GET /api/v1/violations` — List violations

### Agent Registry
- `GET /api/v1/registry` — List registered agents
- `GET /api/v1/registry/{agent_id}` — Agent detail
- `PATCH /api/v1/registry/{agent_id}` — Update agent metadata

### Regulatory Mapping
- `GET /api/v1/regulations` — List regulatory frameworks
- `GET /api/v1/regulations/{id}` — Framework detail with requirements

### Audit Reports
- `POST /api/v1/reports` — Generate compliance report
- `GET /api/v1/reports` — List reports
- `GET /api/v1/reports/{id}` — Report detail

### Incident Response
- `GET /api/v1/incidents` — List incidents (filterable by status/severity)
- `GET /api/v1/incidents/{id}` — Incident detail
- `PATCH /api/v1/incidents/{id}` — Update incident status

## Authentication

Event ingestion endpoints require a Bearer token:

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "decision.start", ...}'
```

Configure API keys via the `API_KEYS` environment variable.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./amini.db` | Database connection string |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `DEBUG` | `true` | Enable debug mode (auto-creates tables) |
| `API_KEYS` | `["dev-key"]` | Accepted API keys for ingestion |
| `RETENTION_DAYS` | `90` | Data retention period in days |
| `PAYLOAD_STORAGE_MODE` | `local` | Payload storage mode (local/external) |
