# Amini

Compliance infrastructure for agentic AI — map agent decisions to regulatory requirements, generate audit-ready documentation, and enforce organizational policies at the decision point.

## Why Amini

AI agents are proliferating in regulated industries (financial services, healthcare, legal), but existing tools don't bridge the gap between **agent observability** (Langsmith, Arize, Braintrust) and **enterprise GRC** (OneTrust, Collibra, ServiceNow). Amini sits in the middle:

- **Observability tools** capture agent traces but have no regulatory mapping
- **GRC platforms** manage compliance logic but can't instrument AI agents
- **Amini** captures agent decision chains, evaluates them against regulatory requirements, and generates audit-ready evidence

Enforcement deadlines are real and approaching: EU AI Act (August 2026), SEC AI examination priorities, Texas TRAIGA, Colorado AI Act, and FTC "Operation AI Comply."

## Key Features

- **Decision chain capture** — Structured logging of every agent decision: inputs, reasoning, tool calls, outputs, errors. Metadata/payload tier separation keeps audit data queryable while storing full payloads separately
- **Two-tier policy engine** — Deterministic rules (13 operators including `is_empty`/`is_not_empty`, compound AND/OR/NOT conditions, < 50ms) with block/warn/log enforcement modes. ReDoS-safe regex evaluation
- **Pre-built regulatory templates** — EU AI Act (8 articles) and SOC 2 (6 criteria) mapped to specific policy requirements, with one-click seeding from the Settings page
- **Agent registry** — Catalog of all AI agent deployments with framework, risk classification, and regulation tagging. Auto-registered from SDK events
- **Audit report generation** — Async background generation (HTTP 202) with compliance reports containing session summaries, violation breakdowns, and gap analysis
- **Incident response** — Automated incident creation from violations with severity classification, remediation paths, resolution notes, and full lifecycle tracking (open → investigating → remediated → closed)
- **Policy management UI** — Create and manage policies directly from the dashboard with YAML rule editor, tier/enforcement/severity configuration, and regulation linking
- **Cross-framework support** — LangChain (with hierarchical parent tracking), CrewAI, and custom frameworks via correlation ID propagation
- **Dual-mode dashboard** — Developer replay view and compliance audit view in a single interface across 10 pages

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React/TS)                   │
│  Dashboard · Agent Registry · Sessions · Policies       │
│  Regulations · Violations · Incidents · Reports         │
│  Settings · Session Detail                              │
└────────────────────────┬────────────────────────────────┘
                         │ TanStack Query + Bearer Auth
┌────────────────────────┴────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  Event Ingestion · Chain Builder · Policy Engine        │
│  Regulatory Mapping · Audit Reports · Incidents         │
│  SQLAlchemy Async · Alembic · Background Tasks          │
└────────────────────────┬────────────────────────────────┘
                         │ Authenticated REST API
┌────────────────────────┴────────────────────────────────┐
│                    Python SDK                            │
│  @trace · @enforce · Decision Context · LangChain       │
│  Correlation IDs · Async Event Emission · Policy DSL    │
└─────────────────────────────────────────────────────────┘
```

| Package | Stack | Description |
|---------|-------|-------------|
| **SDK** (`packages/sdk`) | Python 3.10+, httpx, Pydantic | Instrument agents with `@trace` and `@enforce` decorators. Background event emission, safe policy DSL, exponential backoff transport |
| **Backend** (`packages/backend`) | FastAPI, SQLAlchemy async, Alembic | Event ingestion, decision chain reconstruction, two-tier policy evaluation, regulatory mapping, async audit reports, incident response. All endpoints authenticated |
| **Frontend** (`packages/frontend`) | React 18, TypeScript, Tailwind, Vite | 10 pages with dual-mode interface. Policy creation, incident management, settings configuration. TanStack Query data fetching with Bearer auth |

## Quick Start

```bash
# Clone and configure
cp .env.example .env

# Install all packages
make install

# Start development servers (backend :8000, frontend :5173)
make dev

# Run tests
make test
```

## SDK Usage

```python
from amini import Amini
from amini.policy import PolicyRule, PolicyTier, PolicyEnforcement, PolicySeverity

amini = Amini(
    api_key="ak_...",
    agent_id="support-agent-v3",
    regulations=["eu-ai-act", "sox"],
)

# Auto-instrumentation — captures inputs, outputs, reasoning, errors
@amini.trace
def handle_request(query: str) -> str:
    return agent.run(query)

# Inline policy enforcement — block, warn, or log violations
@amini.enforce("customer-data-handling")
def process_data(action: str, data: dict):
    ...

# Register policies for client-side enforcement
amini.register_policy(PolicyRule(
    name="pii-external-call-block",
    tier=PolicyTier.DETERMINISTIC,
    enforcement=PolicyEnforcement.BLOCK,
    severity=PolicySeverity.CRITICAL,
    regulation="eu-ai-act",
    conditions={"field": "action_type", "operator": "equals", "value": "external_api_call"},
))

# Cross-framework correlation
@amini.trace(framework="langchain")
def langchain_agent(query):
    ...

# Sessions for grouping related decisions
session = amini.start_session(user_context={"user_id": "u123"})
# ... agent work ...
amini.end_session(status="completed")

# SDK flushes automatically on interpreter exit via atexit hook
```

## Development

```bash
make dev-backend     # Backend only (port 8000)
make dev-frontend    # Frontend only (port 5173)
make migrate         # Run database migrations
make seed            # Seed sample data
make demo            # Run demo agent with sample traces
make lint            # Lint all packages (Ruff + ESLint)
```

## Docker Deployment

```bash
docker compose up --build

# Services:
#   PostgreSQL — localhost:5432
#   Backend API — localhost:8000
#   Frontend — localhost:80
```

## Project Structure

```
packages/
  sdk/                Python SDK
    src/amini/          Core client, decorators, policy engine, transport
    tests/              57 unit tests
  backend/            FastAPI backend
    src/amini_server/   Models, routers, services, workers
    tests/              26+ integration tests
  frontend/           React dashboard
    src/pages/          10 page components
    src/components/     8 reusable components
    src/api/            TanStack Query hooks with Bearer auth
policies/
  examples/           Starter policy pack (6 YAML policies)
  schema.yaml         Policy validation schema
.github/
  workflows/          CI pipeline (lint, test, build — 3 parallel jobs)
```

## API Authentication

**All API endpoints** require a Bearer token:

```bash
curl -X GET http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer dev-key"

curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer dev-key" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "decision.start", "agent_id": "my-agent", ...}'
```

Configure API keys via the `API_KEYS` environment variable (comma-separated list). The default `dev-key` is intended for local development only — a warning is logged if used in non-debug mode.

The frontend sends the API key automatically via the `VITE_API_KEY` environment variable.

## Regulatory Templates

Amini ships with pre-built templates for:

| Framework | Requirements | Key Articles |
|-----------|-------------|--------------|
| **EU AI Act** | 8 | Art. 9 (Risk Management), Art. 13 (Transparency), Art. 14 (Human Oversight), Art. 15 (Accuracy/Robustness) |
| **SOC 2 Type II** | 6 | CC6.1 (Access Controls), CC7.2 (System Monitoring), CC8.1 (Change Management) |

Templates map regulatory requirements to specific policy conditions, evidence types, and review cadences. Additional frameworks (NIST AI RMF, SEC, state laws) can be added via the extensible regulation model. Templates can be seeded from the Settings page or via `POST /api/v1/regulations/seed`.

## Policy Engine

The deterministic policy engine supports 13 comparison operators:

| Operator | Description |
|----------|-------------|
| `equals`, `not_equals` | Exact match |
| `contains`, `not_contains` | Substring / collection membership |
| `greater_than`, `less_than` | Numeric comparison |
| `greater_than_or_equal`, `less_than_or_equal` | Numeric comparison |
| `in_list`, `not_in_list` | Value in array |
| `matches_regex` | Regex match (ReDoS-safe, input truncated to 10k chars) |
| `is_empty`, `is_not_empty` | Null / empty string / empty collection check |

Policies support compound conditions with `AND`, `OR`, and `NOT` logical operators, and three enforcement modes: `BLOCK` (prevents execution), `WARN` (logs warning, allows execution), and `LOG_ONLY` (silent audit trail).

## Testing

```bash
make test            # All tests (SDK + backend)
make test-sdk        # SDK tests only (57 tests)
make test-backend    # Backend tests only (26+ tests)
```
