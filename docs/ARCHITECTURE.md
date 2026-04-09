# Amini Architecture

This document describes the internal architecture of Amini's three packages and how they interact.

## System Overview

```
Agent Code (Python)
    │
    ├── @amini.trace / @amini.enforce decorators
    │   └── Amini SDK client
    │       ├── Decision context (inputs, reasoning, outputs, errors)
    │       ├── Local policy evaluation (deterministic tier, <50ms)
    │       └── Background event emission (async thread, batch transport)
    │
    ▼
Backend API (FastAPI)
    │
    ├── Event Ingestion (/api/v1/events)
    │   └── Rate-limited, bulk insert, writes to RawEvent table
    │
    ├── Background Processor (async worker)
    │   ├── Chain reconstruction (groups events → sessions → decision nodes)
    │   ├── Policy evaluation (server-side deterministic rules)
    │   ├── Violation creation (with severity, regulation mapping)
    │   └── Incident auto-creation (from violations exceeding thresholds)
    │
    ├── Query APIs (sessions, decisions, violations, incidents, reports)
    │   └── All authenticated via Bearer token
    │
    └── Async Report Generation (background task, separate DB session)
    │
    ▼
Frontend Dashboard (React)
    │
    ├── TanStack Query (data fetching, caching, mutations)
    ├── 10 route-level pages
    └── Bearer auth on all API requests
```

## Package Details

### SDK (`packages/sdk`)

The SDK is the primary integration point for agent developers.

**Core client** (`client.py`):
- `Amini` class: main entry point, manages sessions, decisions, and policy registration
- Background `EventEmitter` thread: batches events and ships them via HTTP with exponential backoff
- `_safe_repr`: safely serializes arbitrary Python objects for event payloads (depth-limited to 32 levels)
- `atexit` hook: ensures all queued events flush on interpreter shutdown

**Decorators** (`decorators.py`):
- `@trace`: wraps a function to capture inputs, outputs, errors, and timing as decision events
- `@enforce`: evaluates registered policies against function arguments before execution

**Policy engine** (`policy.py` / `policy-core`):
- 13 comparison operators (equals, contains, regex, numeric comparisons, empty checks)
- Compound conditions with AND/OR/NOT
- Three enforcement modes: BLOCK (raises `PolicyViolationError`), WARN, LOG_ONLY
- ReDoS protection: regex inputs truncated to 10k characters, `re.error` caught

**Sessions** (`session.py`):
- Thread-local session management (note: not coroutine-safe for async code)
- Correlation ID propagation for cross-framework tracing
- User context and metadata attachment

**LangChain integration** (`integrations/langchain.py`):
- `AminiLangChainHandler` implements LangChain's `BaseCallbackHandler`
- Tracks `parent_run_id` for hierarchical decision chains
- Maps LLM starts, chain starts, and tool starts to Amini decision events

### Backend (`packages/backend`)

**Models** (`models/`):
- `Session`: groups related decisions with status tracking
- `DecisionNode`: individual agent decisions with parent references for tree structure
- `RawEvent`: ingested events awaiting processing
- `PolicyVersion`: versioned policy rules with YAML content
- `PolicyViolation`: recorded policy violations with severity and regulation mapping
- `Incident`: lifecycle-tracked incidents created from violations
- `AuditReport`: generated compliance reports with JSON content
- `AgentRegistration`: registry of known AI agents
- `Regulation` / `RegulatoryRequirement` / `ComplianceMapping`: regulatory framework model

**Event processing pipeline**:
1. Events arrive via `POST /api/v1/events/batch`
2. Bulk-inserted into `RawEvent` table
3. Background processor acquires lock (prevents duplicate processing across workers)
4. Groups events by session, reconstructs decision chains
5. Evaluates policies against new decisions (batch dedup via pre-loaded existing IDs)
6. Creates violations and auto-creates incidents
7. Marks events as processed via bulk UPDATE

**Report generation**:
- `POST /api/v1/reports` creates a `pending` report record and returns HTTP 202
- Background `asyncio.Task` with its own database session generates the report content
- Report status transitions: `pending` → `completed` or `failed`

**Data retention**:
- `POST /api/v1/admin/cleanup` deletes data older than `RETENTION_DAYS`
- FK-safe deletion order: events → reports → incidents → violations → decision_nodes → sessions

### Frontend (`packages/frontend`)

**API layer** (`src/api/`):
- `client.ts`: base `apiFetch` wrapper that attaches `Authorization: Bearer` header
- Per-resource query hooks using TanStack Query (`useQuery`, `useMutation`)
- Automatic cache invalidation on mutations via `queryClient.invalidateQueries`

**Pages**:
- `DashboardPage`: overview stats with dual-mode toggle (developer/compliance view)
- `SessionsPage` / `SessionDetailPage`: session list and decision chain timeline
- `PoliciesPage`: policy list with inline create form (YAML editor, tier/enforcement/severity selects)
- `IncidentsPage`: incident list with per-incident management panel (status, remediation, resolution)
- `ViolationsPage`: violation log with severity badges and pagination
- `SettingsPage`: configuration display, health check, cleanup trigger, regulation seeding

## Data Flow: End-to-End Example

1. **Agent code** calls `@amini.trace`-decorated function
2. **SDK** captures inputs, starts timer, executes function, captures output/error
3. **SDK** emits `decision.start` and `decision.end` events to background thread
4. **EventEmitter** batches events, POSTs to backend `/api/v1/events/batch`
5. **Backend** bulk-inserts events into `RawEvent` table
6. **Processor** picks up unprocessed events, creates/updates `Session` and `DecisionNode` records
7. **Processor** evaluates active policies against new decisions
8. **Processor** creates `PolicyViolation` if rules are breached
9. **Processor** auto-creates `Incident` from violation (with severity, regulation mapping)
10. **Frontend** queries backend APIs to display sessions, violations, incidents in dashboard

## Security Model

- All API endpoints (except `/health`, `/ready`) require Bearer token authentication
- API keys configured via `API_KEYS` environment variable
- Frontend sends key via `VITE_API_KEY` env var, attached automatically to all requests
- CORS restricted to configured origins with specific allowed methods and headers
- Policy regex evaluation is ReDoS-safe (input truncation + error handling)
- Default `dev-key` triggers a warning in non-debug mode
- Object serialization depth-limited to prevent stack overflow
