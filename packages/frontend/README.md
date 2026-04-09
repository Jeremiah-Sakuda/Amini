# Amini Frontend

React dashboard for Amini — compliance infrastructure for agentic AI. Provides a dual-mode interface for developers (session replay, decision chains) and compliance teams (violations, incidents, audit reports).

## Development

```bash
# Install dependencies
npm install

# Start development server (port 5173)
npm run dev

# Type check
npx tsc --noEmit

# Build for production
npm run build
```

## Stack

- **React 18** with TypeScript (strict mode, zero `any` usage)
- **Tailwind CSS** for styling
- **TanStack Query** for server state management and caching
- **React Router** for client-side routing
- **Vite** for build tooling
- **date-fns** for date formatting
- **Lucide React** for icons

## Authentication

The frontend sends a Bearer token with every API request via the `VITE_API_KEY` environment variable:

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=dev-key
```

The API client (`src/api/client.ts`) automatically attaches the `Authorization: Bearer <key>` header to all requests.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | Overview stats, recent sessions, violation trends. Dual-mode toggle (developer/compliance) |
| **Agent Registry** | `/registry` | List of all registered AI agents with risk classification, framework, and regulation tags |
| **Sessions** | `/sessions` | Paginated session list with status filtering and agent grouping |
| **Session Detail** | `/sessions/:id` | Decision chain timeline with event-level detail (inputs, outputs, reasoning, errors) |
| **Policies** | `/policies` | Policy list with inline creation form. YAML rule editor, tier/enforcement/severity config, regulation linking |
| **Regulations** | `/regulations` | Regulatory frameworks with requirement breakdowns and gap analysis |
| **Violations** | `/violations` | Policy violation log with severity badges and pagination |
| **Incidents** | `/incidents` | Incident list with inline management panel (status updates, remediation paths, resolution notes) |
| **Audit Reports** | `/reports` | Report generation form and report list. JSON export |
| **Settings** | `/settings` | Configuration display, backend health check, retention cleanup trigger, regulatory template seeding |

## Components

| Component | Description |
|-----------|-------------|
| `Layout` | App shell with sidebar and content area |
| `Sidebar` | Navigation with active state highlighting |
| `LoadingSpinner` | Centered loading indicator |
| `ErrorBanner` | Error message display |
| `PolicyBadge` | Severity and tier badge components |
| `SessionList` | Reusable session table |
| `SessionTimeline` | Decision chain timeline visualization |
| `DecisionNode` | Individual decision node card |

## Project Structure

```
src/
  api/              TanStack Query hooks and API client
    client.ts         Base fetch wrapper with auth headers
    sessions.ts       Session queries
    policies.ts       Policy queries and mutations
    violations.ts     Violation queries
    incidents.ts      Incident queries and mutations
    reports.ts        Report queries and mutations
    registry.ts       Agent registry queries
    regulations.ts    Regulation queries
  components/       Reusable UI components
  pages/            Route-level page components
  App.tsx           Route definitions
  main.tsx          App entry point with providers
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_API_KEY` | `dev-key` | API key sent as Bearer token |
