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

## Authentication

**All API endpoints** (except `/health` and `/ready`) require a Bearer token in the `Authorization` header:

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer dev-key"

curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "decision.start", ...}'
```

Configure accepted API keys via the `API_KEYS` environment variable. The default `dev-key` is for local development only — a warning is logged if used in non-debug mode.

## API Endpoints

### Core (no auth required)
- `GET /health` — Health check
- `GET /ready` — Readiness check

### Admin
- `POST /api/v1/admin/cleanup` — Trigger data retention cleanup (deletes data older than configured retention period, respects FK ordering)

### Event Ingestion
- `POST /api/v1/events` — Ingest single event
- `POST /api/v1/events/batch` — Ingest event batch (bulk insert, rate-limited)

### Sessions & Decisions
- `GET /api/v1/sessions` — List sessions (filterable by agent_id, status)
- `GET /api/v1/sessions/{id}` — Session detail with decision chain
- `GET /api/v1/decisions/{id}` — Decision node detail

### Policy Engine
- `GET /api/v1/policies` — List policies with latest versions
- `POST /api/v1/policies` — Create policy with initial version (name, YAML rules, tier, enforcement, severity, optional regulation linking)
- `GET /api/v1/violations` — List violations (paginated)

### Agent Registry
- `GET /api/v1/registry` — List registered agents
- `GET /api/v1/registry/{agent_id}` — Agent detail
- `PATCH /api/v1/registry/{agent_id}` — Update agent metadata (risk classification, data access patterns, deployment status)

### Regulatory Mapping
- `GET /api/v1/regulations` — List regulatory frameworks
- `GET /api/v1/regulations/{id}` — Framework detail with requirements and gap analysis
- `POST /api/v1/regulations/seed` — Seed pre-built templates (EU AI Act, SOC 2)

### Audit Reports
- `POST /api/v1/reports` — Create report (returns **202 Accepted**, generation runs in background)
- `GET /api/v1/reports` — List reports (paginated, filterable by framework)
- `GET /api/v1/reports/{id}` — Report detail (check `status` field: `pending` → `completed` or `failed`)

### Incident Response
- `GET /api/v1/incidents` — List incidents (filterable by status, severity; paginated)
- `GET /api/v1/incidents/{id}` — Incident detail with decision chain snapshot
- `PATCH /api/v1/incidents/{id}` — Update incident (status, remediation_path, resolution_notes)

## Background Processing

- **Event processing**: Ingested events are processed asynchronously — chain reconstruction, policy evaluation, and violation/incident creation happen in a background worker with database-level locking to prevent duplicate processing across workers.
- **Report generation**: `POST /api/v1/reports` returns immediately with a `pending` report. Generation runs as an async background task with its own database session, so the HTTP request is not blocked.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./amini.db` | Database connection string (SQLite for dev, PostgreSQL for prod) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `DEBUG` | `true` | Enable debug mode (auto-creates tables, seeds regulations on startup) |
| `API_KEYS` | `["dev-key"]` | Accepted Bearer tokens for API authentication |
| `RETENTION_DAYS` | `90` | Data retention period in days |
| `PAYLOAD_STORAGE_MODE` | `local` | Payload storage mode (local / external) |
| `POOL_SIZE` | `5` | SQLAlchemy connection pool size |
| `MAX_OVERFLOW` | `10` | SQLAlchemy max pool overflow connections |
| `POOL_RECYCLE` | `3600` | SQLAlchemy connection recycle time (seconds) |

## Data Retention

The retention cleanup endpoint (`POST /api/v1/admin/cleanup`) deletes data older than `RETENTION_DAYS` in FK-safe order:

1. Raw events
2. Audit reports
3. Incidents
4. Policy violations
5. Decision nodes
6. Sessions

Returns a summary of deleted record counts per table.
