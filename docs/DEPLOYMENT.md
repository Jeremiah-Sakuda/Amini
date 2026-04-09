# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Poetry (Python)
- npm (Node)

### Setup

```bash
# Clone the repository
git clone https://github.com/Jeremiah-Sakuda/Amini.git
cd Amini

# Copy environment template
cp .env.example .env

# Install all packages
make install

# Run database migrations
cd packages/backend && poetry run alembic upgrade head && cd ../..

# Start both servers
make dev
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Seeding Data

Regulatory templates (EU AI Act, SOC 2) auto-seed when `DEBUG=true`. To seed manually:

```bash
curl -X POST http://localhost:8000/api/v1/regulations/seed \
  -H "Authorization: Bearer dev-key"
```

Or use the Settings page in the dashboard.

## Docker Deployment

```bash
docker compose up --build
```

This starts three services:
- **PostgreSQL** on port 5432
- **Backend API** on port 8000
- **Frontend** (nginx) on port 80

### Production Docker Configuration

Update `docker-compose.yml` environment variables:

```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/amini
      DEBUG: "false"
      API_KEYS: '["your-production-key-here"]'
      CORS_ORIGINS: '["https://your-domain.com"]'
      RETENTION_DAYS: "90"
```

## Environment Variables

### Backend

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./amini.db` | No | Database connection string. Use `postgresql+asyncpg://...` for production |
| `DEBUG` | `true` | No | Enables auto-table creation and regulation seeding. Set to `false` in production |
| `API_KEYS` | `["dev-key"]` | **Yes (prod)** | JSON array of accepted Bearer tokens. Must change from default for production |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | No | JSON array of allowed CORS origins |
| `RETENTION_DAYS` | `90` | No | Data retention period in days |
| `PAYLOAD_STORAGE_MODE` | `local` | No | Payload storage mode |
| `POOL_SIZE` | `5` | No | Database connection pool size |
| `MAX_OVERFLOW` | `10` | No | Max overflow connections beyond pool size |
| `POOL_RECYCLE` | `3600` | No | Connection recycle time in seconds |

### Frontend

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | No | Backend API URL |
| `VITE_API_KEY` | `dev-key` | **Yes (prod)** | API key sent as Bearer token. Must match a key in backend's `API_KEYS` |

### SDK

| Variable | Default | Description |
|----------|---------|-------------|
| `AMINI_API_KEY` | `""` | API key for backend authentication |
| `AMINI_AGENT_ID` | `""` | Unique agent identifier |
| `AMINI_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `AMINI_ENVIRONMENT` | `development` | Deployment environment label |
| `AMINI_REGULATIONS` | `""` | Comma-separated regulation IDs |
| `AMINI_FRAMEWORK` | `""` | Agent framework identifier |

## Database

### Development (SQLite)
Default. No setup required. Database file created automatically at `./amini.db`.

### Production (PostgreSQL)

```bash
# Create database
createdb amini

# Run migrations
cd packages/backend
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/amini \
  poetry run alembic upgrade head
```

### Migrations

```bash
cd packages/backend

# Create a new migration after model changes
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1
```

Note: In `DEBUG=true` mode, tables are auto-created via `create_all()` which may drift from Alembic migrations. Always run migrations in production.

## Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Set `API_KEYS` to strong, unique tokens (not `dev-key`)
- [ ] Set `VITE_API_KEY` to match one of the backend API keys
- [ ] Configure `CORS_ORIGINS` to your frontend domain only
- [ ] Use PostgreSQL (not SQLite) via `DATABASE_URL`
- [ ] Run Alembic migrations (`alembic upgrade head`)
- [ ] Configure `RETENTION_DAYS` per your compliance requirements
- [ ] Set up database backups
- [ ] Place behind a reverse proxy (nginx/Caddy) with TLS
- [ ] Monitor `/health` and `/ready` endpoints
