# Amini

Agentic workflow auditor — trust infrastructure for AI agents.

Amini provides decision chain replay for debugging agent behavior and compliance auditing built on the same data.

## Architecture

- **Python SDK** (`packages/sdk`) — Single-decorator auto-instrumentation for AI agents
- **Backend** (`packages/backend`) — FastAPI service with event ingestion, chain reconstruction, and policy evaluation
- **Frontend** (`packages/frontend`) — React dashboard with dual-mode interface (Developer replay + Compliance audit)

## Quick Start

```bash
# Install dependencies
make install

# Start development servers
make dev

# Run tests
make test
```

## Development

```bash
# Copy environment variables
cp .env.example .env

# Install all packages
make install

# Run database migrations
make migrate

# Start backend (port 8000)
make dev-backend

# Start frontend (port 5173)
make dev-frontend

# Seed sample data
make seed

# Run demo agent
make demo
```

## Project Structure

```
packages/
  sdk/          Python SDK for agent instrumentation
  backend/      FastAPI backend service
  frontend/     React frontend dashboard
policies/
  examples/     Starter policy pack (YAML)
  schema.yaml   Policy validation schema
scripts/
  seed_db.py    Database seeder
  demo_agent.py Demo agent script
```
