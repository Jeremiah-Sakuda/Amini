# Amini — PRD vs. Implementation Compliance Scan

**Date:** April 9, 2026
**Scope:** Full codebase audit against PRD v2.0 (536-line Product Requirements Document)
**Method:** Automated traversal of all source files in `packages/sdk`, `packages/backend`, `packages/frontend`, plus infra configs

---

## EXECUTIVE SUMMARY

The implementation covers approximately **35% of the PRD's specified functionality**. The SDK and backend scaffolding are structurally sound, but the majority of the PRD's differentiating features — regulatory mapping, shadow AI discovery, incident automation, audit evidence, and semantic policy evaluation — are either stubbed, disconnected, or entirely absent.

| PRD Section | Coverage | Verdict |
|-------------|----------|---------|
| 6.1 Agent Registry & Shadow AI | 25% | Schema exists; shadow AI is vaporware |
| 6.2 Decision Chain Capture | 50% | Core works; regulatory relevance + escalation missing |
| 6.3 Policy Engine | 55% | Deterministic tier works; semantic tier is a stub |
| 6.4 Regulatory Mapping Engine | 30% | Templates seeded; mapping engine doesn't exist |
| 6.5 Audit Report Generator | 40% | Basic stats work; evidence + PDF + gaps are skeletal |
| 6.6 Incident Response Toolkit | 20% | Model complete; creation function never called |
| 7.1 SDK Design | 70% | Core decorators + transport work; env config + LangChain tests missing |
| 7.2 Infrastructure | 60% | FastAPI + auth + DB work; retention unwired, auth bypassed if no keys |
| 7.3 Deployment | 80% | Docker + CI work; healthcheck has dependency bug |
| 7.4 Performance Requirements | 0% | Zero benchmarks, zero SLA enforcement |
| 9.3 Pricing/Tier Enforcement | 0% | No session limits, no retention tiers, no feature gating |

---

## DETAILED FINDINGS

---

### PRD 6.1 — Agent Registry & Shadow AI Discovery

**PRD promises:** Automated inventory of all AI agent deployments. SDK instrumentation for managed agents. Network-level detection heuristics for shadow AI (API call patterns, browser fingerprints, data egress). Living catalog with framework, provider, data access patterns, deployment status.

| Requirement | Status | Details |
|-------------|--------|---------|
| Automated inventory of all deployments | **PARTIAL** | Agents are created reactively via `get_or_create_agent()` when events arrive — not a proactive inventory scan |
| SDK instrumentation for managed agents | **PARTIAL** | SDK sends `framework` and `regulations` on events, but these are never copied back to the `Agent` model columns |
| Network-level shadow AI detection | **NO** | Zero implementation. No network heuristics, no API pattern matching, no browser fingerprinting |
| Shadow AI status assignment | **STUB** | Frontend has `shadow` status colors and `network` discovery colors, but nothing in the backend ever sets these values |
| Living catalog (framework, provider, data access, status) | **PARTIAL** | Model has all columns (`framework`, `provider`, `risk_class`, `tags`, `data_access_patterns`, `deployment_status`, `discovery_method`, `regulations`). All remain at defaults unless manually PATCHed via API |

**Bugs found:**
1. `get_agent_detail` and `update_agent` call `list_agents(db)` with no filters then linear-search for one ID — O(n) per request
2. `Agent.tags` is `dict | None` in ORM but `list[str] | None` in Pydantic schema — type mismatch risk
3. N+1 queries in `list_agents`: two COUNT queries per agent row

**Files:** `models/agent.py`, `services/registry_service.py`, `routers/registry.py`, `schemas/registry.py`, `pages/RegistryPage.tsx`

---

### PRD 6.2 — Decision Chain Capture

**PRD promises:** Structured logging of decision sequences (inputs, reasoning, tool calls, branching, outputs). Per-node metadata (agent ID, session ID, timestamp, environment, user context). Regulatory relevance flag at ingestion. Auto-escalation to compliance review queues.

| Requirement | Status | Details |
|-------------|--------|---------|
| Structured logging of decision sequences | **PARTIAL** | Event types cover the lifecycle (`decision.start/input/reasoning/action/output/error/end`). Chain builder maps to `DecisionNode` fields. However, reasoning is stored as `str(payload)` — loses structure |
| Per-node metadata (agent, env, user) | **PARTIAL** | `session_id` and `timestamp` are on each node. Agent ID, environment, and user context are only on the parent `AgentSession`, not denormalized onto `DecisionNode` |
| Correlation IDs / cross-framework tracing | **YES** | `correlation_id` and `framework` propagated through SDK → events → sessions |
| Regulatory relevance flag at ingestion | **NO** | No such field exists on `RawEvent` or `DecisionNode`. No computation step at ingest time |
| Auto-escalation to compliance review queues | **NO** | `human_review_required` exists on `PolicyVersion` but nothing reads it. No review queue, no routing logic |

**Bugs found:**
1. Late/split batches lose decision detail — if `DecisionNode` already exists, builder skips the entire group for that decision
2. `parent_decision_id` stores SDK's external UUID but the FK targets internal `decision_nodes.id` — parent links never resolve in tree assembly
3. Sequence numbers reset per processor run — can collide on repeated processing of the same session

**Files:** `models/decision.py`, `models/event.py`, `services/chain_builder.py`, `services/event_service.py`, `workers/processor.py`, `sdk/context.py`, `sdk/events.py`

---

### PRD 6.3 — Policy Engine

**PRD promises:** Declarative YAML policies mapped to regulations. Versioned and auditable. Two-tier evaluation: deterministic (12 operators, compound conditions, < 50ms, block/warn/log_only) and semantic (LLM-judge async advisory). SDK middleware enforcement.

| Requirement | Status | Details |
|-------------|--------|---------|
| Declarative YAML policy definitions | **PARTIAL** | YAML parsing + `parsed_rule` extraction works. `scope` filtering by `environments` and `agents` implemented. `agent_tags` field exists but is never checked in `_match_scope` |
| Versioned, auditable policies | **YES** | New `PolicyVersion` on create/update with monotonic version numbers. Timestamps via mixin. Regulatory linkage fields present |
| Deterministic tier: recursive descent evaluator | **YES** | Safe recursive descent with `and`/`or`/`not` compound conditions. Works in both backend and SDK |
| Deterministic tier: 12 comparison operators | **PARTIAL** | **11 operators** implemented (missing one vs. PRD's claim of 12): `equals`, `not_equals`, `greater_than`, `less_than`, `gte`, `lte`, `contains`, `not_contains`, `matches_regex`, `in_list`, `not_in_list` |
| Deterministic tier: enforcement modes | **PARTIAL** | SDK enforces `block` (raises exception) and `warn` (logs). Backend ignores enforcement mode entirely — all violations become `PolicyViolation` rows regardless |
| Deterministic tier: < 50ms latency | **NO** | No timing budgets, no benchmarks, no enforcement |
| Semantic tier: LLM-judge async evaluation | **STUB** | Hard-coded to return `violated=False` with message "Semantic evaluation not implemented (stub)" |
| SDK middleware enforcement (not proxy) | **PARTIAL** | `Amini.enforce()` decorator works client-side. But policies must be manually registered via `_policy_cache.register()` — no fetch/sync from backend |

**Bugs found:**
1. `_match_scope` compares `scope["agents"]` to internal UUID `session.agent_id`, not the SDK's `agent_external_id` — policies scoped to agents likely never match
2. `POST /policies/{id}/evaluate` is a stub — returns `evaluation_queued` but does nothing
3. No deduplication on violations — processor re-evaluates entire session history on every batch, creating duplicate `PolicyViolation` rows
4. Backend condition evaluation runs `str(decision.input_context)` — regex/contains operate on Python dict repr strings, not structured field paths

**Files:** `models/policy.py`, `services/policy_engine.py`, `routers/policies.py`, `sdk/policy.py`, `sdk/client.py`, `policies/schema.yaml`, `policies/examples/`

---

### PRD 6.4 — Regulatory Mapping Engine

**PRD promises:** Pre-built templates for EU AI Act (8 articles) and SOC 2 (6 criteria). Extensible for NIST AI RMF, Texas TRAIGA, Colorado AI Act, SEC. Required evidence types, documentation formats, review cadences. Maps agent activity to template requirements. Auto gap analysis.

| Requirement | Status | Details |
|-------------|--------|---------|
| EU AI Act templates (8 articles) | **YES** | 8 requirements seeded in `regulation_service.py` |
| SOC 2 templates (6 criteria) | **YES** | 6 requirements seeded |
| Extensible for additional frameworks | **PARTIAL** | Generic `Regulation`/`RegulatoryRequirement` tables support it. No templates for NIST, TRAIGA, Colorado, or SEC exist |
| Evidence types per requirement | **PARTIAL** | `evidence_types` JSON field exists and is populated per requirement. `review_cadence_days` present |
| Documentation formats | **NO** | No field for documentation format exists in the data model |
| Maps agent activity to requirements | **NO** | `ComplianceMapping` model exists but has **zero writers** in the entire codebase. No service/job derives mappings from sessions or decisions |
| Automatic gap analysis | **PARTIAL** | `get_compliance_overview` builds per-requirement gap lists. `_identify_gaps` checks policy coverage. But "automatic" mapping from live activity is absent |

**Bugs found:**
1. `ComplianceMapping` is a read-only model — nothing in the backend ever creates rows
2. Compliance percentage only counts `compliant` status, ignoring `partially_compliant` in the numerator

**Files:** `models/regulation.py`, `services/regulation_service.py`, `routers/regulations.py`, `schemas/regulations.py`, `pages/RegulationsPage.tsx`

---

### PRD 6.5 — Audit Report Generator

**PRD promises:** One-click generation per framework. Executive summary with stats. Decision chain evidence. Policy evaluation results. Violation breakdown by severity. Compliance gap analysis. JSON export. PDF export (roadmap). GRC integrations (roadmap).

| Requirement | Status | Details |
|-------------|--------|---------|
| One-click report generation | **PARTIAL** | Backend `POST /api/v1/reports` + frontend form. Not literally one-click (requires date range + framework selection) |
| Executive summary with session/violation stats | **YES** | `_build_executive_summary` provides session counts, violation counts, period info |
| Decision chain evidence | **NO** | `evidence_log` only contains aggregate counts (`decision_chains_captured`). No per-session or per-chain payloads. `DecisionNode` is imported but never used (dead import) |
| Policy evaluation results | **PARTIAL** | `policy_evaluations_performed` equals total violation count — semantically wrong (should count all evaluations, not just violations) |
| Violation breakdown by severity | **YES** | Aggregation by severity implemented and displayed in UI |
| Compliance gap analysis | **PARTIAL** | `_identify_gaps` checks policy coverage against hardcoded article sets. Sensitive to exact `regulation_article` string format |
| Structured JSON export | **YES** | API returns full report as JSON. No dedicated download endpoint |
| PDF export | **NO** | Not implemented (roadmap item) |
| GRC integrations | **NO** | Not implemented (roadmap item) |

**Bugs found:**
1. `period_start`/`period_end` passed as plain strings from frontend date inputs, compared against timezone-aware `DateTime` — portability risk
2. Gap detection requires exact `regulation_article` values ("6", "9") — if policies store "Art. 6" or "Article 6", gaps are false positives
3. Dead import: `DecisionNode` imported in `report_service.py` but never used

**Files:** `models/audit_report.py`, `services/report_service.py`, `routers/reports.py`, `schemas/reports.py`, `pages/ReportsPage.tsx`

---

### PRD 6.6 — Incident Response Toolkit

**PRD promises:** Full incident package (decision chain, policy, regulation, affected subjects, remediation). Lifecycle: open → investigating → remediated → closed. Severity: critical/high/medium/low.

| Requirement | Status | Details |
|-------------|--------|---------|
| Full incident package generation | **PARTIAL** | `create_incident_from_violation` exists with decision chain snapshot, policy/regulation info, and generated remediation. **But it is never called anywhere in the codebase** |
| Affected data subjects | **NO** | Field exists on model but is never populated (always `None`) |
| Remediation path generation | **YES** | `_generate_remediation` produces text-based remediation based on violation severity |
| Lifecycle management | **PARTIAL** | Backend supports full lifecycle + `false_positive` via PATCH. Frontend has no actions to transition status — read-only display |
| Severity classification | **YES** | Four levels implemented with mapping from violation severity |

**Critical issue:** The entire incident system is **disconnected**. `record_violation` in `violation_service.py` does not call `create_incident_from_violation`. Incidents will only exist if inserted manually or via future code. The PRD's "when an agent violates policy, Amini generates an incident package" does not happen.

**Bugs found:**
1. `create_incident_from_violation` is dead code — defined but never invoked
2. Frontend `IncidentsPage` has no PATCH capability — `api/incidents.ts` only exports `useIncidents` (read-only)
3. Frontend filter omits `false_positive` status despite backend support
4. Pagination edge case: `disabled={incidents.length < 20}` fails when last page has exactly 20 items

**Files:** `models/incident.py`, `services/incident_service.py`, `routers/incidents.py`, `schemas/incidents.py`, `pages/IncidentsPage.tsx`

---

### PRD 7.1 — SDK Design

**PRD promises:** `@amini.trace` and `@amini.enforce` decorators. Cross-framework correlation IDs. Async background emission (< 5ms). Transport retry (3 retries, exponential backoff, jitter). LangChain `BaseCallbackHandler`. Client-side policy evaluation. Env var + constructor config.

| Requirement | Status | Details |
|-------------|--------|---------|
| `@amini.trace` decorator | **YES** | Instance method `Amini.trace` works as decorator. Supports both sync and async |
| `@amini.enforce` decorator | **YES** | Instance method `Amini.enforce` works with `block`/`warn`/`log_only` modes |
| Cross-framework correlation IDs | **PARTIAL** | IDs generated and propagated. No incoming propagation (W3C traceparent / HTTP headers) |
| Async background emission | **YES** | `put_nowait` + daemon thread flush loop. Non-blocking to caller |
| < 5ms overhead | **NO** | No benchmarks or timing enforcement |
| Transport retry (3 retries, backoff, jitter) | **YES** | `MAX_RETRIES=3`, exponential backoff with `random.uniform(0, 0.5)` jitter. Tested |
| LangChain `BaseCallbackHandler` | **YES** | Subclasses `BaseCallbackHandler`. Maps chains/tools/LLM calls to decision events |
| LangChain integration tests | **NO** | Zero test coverage for `integrations/langchain.py` |
| Client-side condition evaluation | **YES** | Safe recursive evaluator with 11 operators. Well-tested |
| Configurable via env vars | **PARTIAL** | `from_env` maps only 6 of ~10 config fields. `flush_interval_seconds`, `flush_batch_size`, `max_queue_size`, `enabled` not env-configurable |
| Policy sync from backend | **NO** | Policies must be manually registered via `_policy_cache.register()`. No fetch/poll/push mechanism |

**Test coverage:** 57 tests across 6 files. Gaps: no LangChain handler tests, no dedicated async decorator tests.

**Files:** `sdk/client.py`, `sdk/config.py`, `sdk/context.py`, `sdk/emitter.py`, `sdk/events.py`, `sdk/policy.py`, `sdk/transport.py`, `sdk/integrations/langchain.py`

---

### PRD 7.2 — Infrastructure

**PRD promises:** FastAPI async. API key auth on ingest. PostgreSQL (prod) / SQLite (dev). Metadata/payload tier separation. Async workers + concurrency locking. Bearer token auth. React + Tailwind. Configurable retention (90-day default) + cleanup.

| Requirement | Status | Details |
|-------------|--------|---------|
| FastAPI with async processing | **YES** | Async routes, `BackgroundTasks`, async SQLAlchemy |
| API key auth on ingest endpoints | **YES** | `Depends(verify_api_key)` on ingest router. **Caveat:** if `api_keys` list is empty, auth is bypassed entirely |
| PostgreSQL (prod) / SQLite (dev) | **YES** | SQLite default, `asyncpg` for Postgres, docker-compose provides Postgres |
| Metadata/payload tier separation | **PARTIAL** | `DecisionNode` explicitly splits tiers. `RawEvent` stores single `payload` blob. `payload_storage_mode` config exists but is marked "future" |
| Async workers + concurrency locking | **YES** | `asyncio.Lock()` prevents concurrent processing. `BackgroundTasks` triggers |
| Bearer token auth | **YES** | Expects `Authorization: Bearer ...` |
| React + Tailwind frontend | **YES** | React 18, Tailwind CSS, Vite, TanStack Query |
| Configurable retention (90 days) + cleanup | **PARTIAL** | Default 90 days. `cleanup_expired_data` implemented. **Not wired to any scheduler** — only accessible via `POST /api/v1/admin/cleanup` which has **no authentication** |

**Bugs found:**
1. Auth bypass: if `settings.api_keys` is empty, `verify_api_key` returns `""` without validation
2. Admin cleanup endpoint (`/api/v1/admin/cleanup`) has no authentication
3. No connection pool configuration (SQLAlchemy defaults)
4. No rate limiting on individual event payloads (batch limited to 500 events, but no size limits)
5. YAML policy parsing is CPU-bound in async context (blocks event loop)

**Files:** `config.py`, `database.py`, `main.py`, `dependencies.py`, `workers/processor.py`, `services/retention_service.py`, `routers/health.py`

---

### PRD 7.3 — Deployment

| Requirement | Status | Details |
|-------------|--------|---------|
| SQLite dev mode with `make dev` | **YES** | Makefile starts backend + frontend with SQLite default |
| Multi-stage Dockerfiles | **YES** | Builder + runtime stages for both backend and frontend |
| docker-compose with Postgres + healthchecks | **PARTIAL** | Postgres healthcheck works. Backend healthcheck uses `httpx` but Dockerfile only installs main deps — `httpx` may not be available in the production image |
| GitHub Actions CI (3 parallel jobs) | **YES** | `sdk`, `backend`, `frontend` jobs run in parallel |

**Bug found:** Backend Docker healthcheck runs `python -c "import httpx; ..."` but `httpx` is listed as a dev dependency, not a main dependency. Healthcheck may fail in production containers.

**Files:** `Makefile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `packages/backend/Dockerfile`, `packages/frontend/Dockerfile`

---

### PRD 7.4 — Performance Requirements

| Requirement | Target | Status |
|-------------|--------|--------|
| SDK overhead per decision node | < 5ms | **NO** — No benchmarks |
| Inline policy evaluation | < 50ms | **NO** — No benchmarks |
| Event ingestion throughput | 10K events/sec/tenant | **NO** — Rate limiter (10 batch reqs/60s) conflicts with this target |
| Decision chain reconstruction | < 2s for 100+ nodes | **NO** — No benchmarks, parent FK bug affects trees |
| Audit report generation | < 30s for 90-day report | **NO** — No benchmarks |
| System availability | 99.9% uptime | **NO** — No SLO, no redundancy, no status reporting |

**None of the 6 performance requirements have any implementation, measurement, or enforcement.**

---

### PRD 9.3 — Pricing Model / Tier Enforcement

| Tier Feature | Status | Details |
|--------------|--------|---------|
| Developer: 500 sessions/mo limit | **NO** | No session counting, no enforcement |
| Developer: 7-day retention | **NO** | Single retention config (default 90 days), no per-tier logic |
| Growth: 25,000 sessions/mo limit | **NO** | No tier logic anywhere |
| Growth: 90-day retention | **NO** | Default happens to be 90 days but not tier-aware |
| Growth: 3 regulatory templates | **NO** | No template limits |
| Enterprise: Unlimited sessions | **NO** | No enforcement needed, but no tier system exists |
| Enterprise: SSO/SAML | **NO** | No SSO implementation |
| Enterprise: On-prem deployment | **NO** | Docker exists but no on-prem config tooling |
| Any tier: Feature gating | **NO** | All features available to all users |

---

## BUG SUMMARY

### Critical (blocks production)

| # | Location | Issue |
|---|----------|-------|
| 1 | `retention_service.py` | References non-existent model `Violation` (should be `PolicyViolation`) and non-existent fields |
| 2 | `chain_builder.py:49` | Sets session status as raw string instead of `SessionStatus` enum |
| 3 | `chain_builder.py` → `decision.py` | `parent_decision_id` stores SDK external UUID but FK targets internal `decision_nodes.id` — parent links never resolve |
| 4 | `incident_service.py` | `create_incident_from_violation` is defined but never called — entire incident system disconnected |
| 5 | `dependencies.py:17-18` | Auth bypassed entirely if `api_keys` list is empty |

### High (functionality broken)

| # | Location | Issue |
|---|----------|-------|
| 6 | `policy_engine.py:131-133` | `_match_scope` compares agent scope to internal UUID, not external ID — scoped policies never match |
| 7 | `registry.py:32-41` | O(n) agent lookup — fetches ALL agents then iterates |
| 8 | `processor.py:66-77` | No violation deduplication — duplicate rows created on re-processing |
| 9 | `report_service.py:148` | `policy_evaluations_performed` = violation count (semantically wrong) |
| 10 | `routers/health.py:20-24` | Admin cleanup endpoint has no authentication |

### Medium (data quality / edge cases)

| # | Location | Issue |
|---|----------|-------|
| 11 | `chain_builder.py:61-64` | Sequence numbers reset per processor run — collision risk |
| 12 | `chain_builder.py:115-116` | Reasoning stored as `str(payload)` — loses JSON structure |
| 13 | `report_service.py` | Date strings compared to timezone-aware DateTime — portability risk |
| 14 | `report_service.py:187-195` | Gap detection requires exact article strings — fragile matching |
| 15 | `docker-compose.yml:34-35` | Backend healthcheck uses `httpx` but it's a dev dependency |
| 16 | `schemas/registry.py` | `tags` type mismatch: ORM `dict | None` vs schema `list[str] | None` |
| 17 | `ingest.py` | Rate limiter (10 batch/60s) conflicts with PRD's 10K events/sec target |

---

## COVERAGE HEATMAP

```
PRD Feature                              Implementation Depth
──────────────────────────────────────── ─────────────────────
SDK: @trace/@enforce decorators          ████████████████░░░░ 80%
SDK: Background emission + transport     ██████████████████░░ 90%
SDK: LangChain integration               ████████████░░░░░░░░ 60% (no tests)
SDK: Policy sync from backend            ░░░░░░░░░░░░░░░░░░░░  0%
Backend: Event ingestion pipeline        ████████████████░░░░ 80%
Backend: Decision chain builder          ██████████░░░░░░░░░░ 50% (parent bug)
Backend: Policy engine (deterministic)   ████████████████░░░░ 75%
Backend: Policy engine (semantic)        ██░░░░░░░░░░░░░░░░░░  5% (stub)
Backend: Regulatory templates            ████████████████░░░░ 80%
Backend: Regulatory mapping engine       ██░░░░░░░░░░░░░░░░░░ 10% (model only)
Backend: Audit report generation         ██████░░░░░░░░░░░░░░ 35%
Backend: Incident system                 ████░░░░░░░░░░░░░░░░ 20% (disconnected)
Backend: Retention/cleanup               ████░░░░░░░░░░░░░░░░ 20% (unwired)
Backend: Auth & multi-tenancy            ████████░░░░░░░░░░░░ 40%
Frontend: Dashboard + pages              ████████████████░░░░ 80%
Frontend: Interactive features           ██████░░░░░░░░░░░░░░ 30% (read-only)
Frontend: Export (JSON/PDF)              ░░░░░░░░░░░░░░░░░░░░  0% (no-ops)
Infrastructure: Docker + CI              ████████████████░░░░ 80%
Performance: Any requirement             ░░░░░░░░░░░░░░░░░░░░  0%
Pricing: Tier enforcement                ░░░░░░░░░░░░░░░░░░░░  0%
Shadow AI: Detection                     ░░░░░░░░░░░░░░░░░░░░  0%
```

---

## PRIORITY REMEDIATION ROADMAP

### P0 — Fix Before Any Demo (< 4 hours)

1. Fix `retention_service.py` broken model/field references
2. Fix `chain_builder.py` session status enum assignment
3. Fix `parent_decision_id` external→internal UUID mismatch in chain builder
4. Wire `create_incident_from_violation` into `record_violation`
5. Fix auth bypass when `api_keys` is empty

### P1 — Fix Before Design Partner Deployment (< 2 days)

6. Fix `_match_scope` agent ID comparison (external vs internal)
7. Add violation deduplication in processor
8. Fix O(n) registry lookup → indexed query
9. Add auth to admin cleanup endpoint
10. Fix Docker healthcheck `httpx` dependency
11. Add SDK policy sync from backend (poll or push)
12. Fix report `policy_evaluations_performed` semantics

### P2 — Required for PRD Parity (1-2 weeks)

13. Implement regulatory relevance flag at event ingestion
14. Implement compliance review queue / escalation routing
15. Connect `ComplianceMapping` — write mappings from agent activity
16. Add decision chain evidence to audit reports (not just counts)
17. Implement incident lifecycle transitions in frontend
18. Add PDF export for audit reports
19. Add frontend error states (not just loading spinners)
20. Implement env var config for all SDK settings

### P3 — Feature Completions (3-4 weeks)

21. Implement semantic policy tier (LLM judge integration)
22. Build shadow AI detection (network heuristics)
23. Add pricing tier enforcement (session limits, retention, feature gates)
24. Add performance benchmarks for all 6 PRD targets
25. Add additional regulatory templates (NIST, TRAIGA, Colorado, SEC)
26. Build GRC platform integrations (OneTrust, ServiceNow)
27. Implement SSO/SAML for enterprise tier

---

## CONCLUSION

The codebase demonstrates strong architectural decisions and clean code quality for a solo founder, but the **PRD describes a product roughly 3x more mature than what exists**. The most critical gap is not any single missing feature — it's the **disconnect between the systems**. The incident system doesn't fire. The regulatory mapping engine doesn't map. The policy engine doesn't sync to the SDK. The audit reports don't include evidence. Each subsystem works in isolation at 40-80% depth, but the end-to-end compliance story the PRD sells — "agent violates policy → incident created → regulatory requirement flagged → audit report generated with evidence" — has no working path through the code today.

The DD report's assessment of "~30% of what's specified" is accurate. Fixing the P0 bugs (~4 hours) and completing P1 items (~2 days) would bring the product to a credible demo state. Reaching true PRD parity requires 4-6 weeks of focused development.
