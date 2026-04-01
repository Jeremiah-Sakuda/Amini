# Amini

Compliance infrastructure for agentic AI — map agent decisions to regulatory requirements, generate audit-ready documentation, and enforce organizational policies at the decision point.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  Dashboard · Agent Registry · Regulations · Reports     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  Event Ingestion · Chain Builder · Policy Engine        │
│  Regulatory Mapping · Audit Reports · Incidents         │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│                    Python SDK                            │
│  @trace · @enforce · Decision Context · LangChain       │
│  Correlation IDs · Async Event Emission                 │
└─────────────────────────────────────────────────────────┘
```

- **Python SDK** (`packages/sdk`) — Instrument agents with `@trace` and `@enforce` decorators. Supports LangChain, CrewAI, and custom frameworks via correlation ID propagation.
- **Backend** (`packages/backend`) — FastAPI service with event ingestion, decision chain reconstruction, two-tier policy evaluation, regulatory mapping, audit report generation, and incident response.
- **Frontend** (`packages/frontend`) — React dashboard with dual-mode interface: developer replay and compliance audit views. Agent registry, regulatory framework browser, incident tracker, and report generator.

## Quick Start

```bash
# Clone and configure
cp .env.example .env

# Install all packages
make install

# Start development servers
make dev

# Run tests
make test
```

## Development

```bash
# Backend only (port 8000)
make dev-backend

# Frontend only (port 5173)
make dev-frontend

# Database migrations
make migrate

# Seed sample data
make seed

# Lint
make lint
```

## Docker Deployment

```bash
# Build and run all services
docker compose up --build

# Services:
#   PostgreSQL — localhost:5432
#   Backend API — localhost:8000
#   Frontend — localhost:80
```

## SDK Usage

```python
from amini import Amini

amini = Amini(
    api_key="ak_...",
    agent_id="support-agent-v3",
    regulations=["eu-ai-act", "sox"],
)

# Auto-instrumentation
@amini.trace
def handle_request(query: str) -> str:
    return agent.run(query)

# Inline policy enforcement
@amini.enforce("customer-data-handling")
def process_data(action: str, data: dict):
    ...

# Cross-framework tracing
@amini.trace(framework="langchain")
def langchain_agent(query):
    ...
```

## Project Structure

```
packages/
  sdk/          Python SDK — decorators, policy enforcement, event emission
  backend/      FastAPI — ingestion, chain builder, policy engine, API
  frontend/     React — compliance dashboard, agent registry, reports
policies/
  examples/     Starter policy pack (YAML)
  schema.yaml   Policy validation schema
.github/
  workflows/    CI pipeline (lint, test, build)
```

## API Authentication

All event ingestion endpoints require a Bearer token:

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "decision.start", ...}'
```

Configure API keys via the `API_KEYS` environment variable.

## Testing

```bash
# All tests
make test

# SDK tests only
make test-sdk

# Backend tests only
make test-backend
```
