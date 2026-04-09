# Amini — Venture Capital Due Diligence Report

**Date:** April 1, 2026
**Prepared by:** Independent Technical & Business Review
**Stage:** Pre-Seed / Accelerator Application
**Sector:** AI Governance & Compliance Infrastructure

---

## EXECUTIVE SUMMARY

Amini is positioning itself as **compliance infrastructure for agentic AI** — a regulatory governance layer that sits between AI agent observability platforms (Langsmith, Arize, Braintrust) and enterprise GRC platforms (OneTrust, Collibra, ServiceNow). The thesis: as AI agents proliferate in regulated industries, enterprises will need purpose-built infrastructure to prove regulatory compliance — and existing tools on both sides of the market don't solve this.

**The thesis is strong. The timing is excellent. The execution is early but technically sound.**

| Dimension | Rating | Summary |
|-----------|--------|---------|
| **Market Thesis** | A | Real regulatory deadlines, clear buyer pain, underserved gap |
| **Technical Execution** | B+ | Solid architecture, ~8,400 LOC, 83 tests, 3 critical bugs |
| **Product Completeness** | B | Core features implemented, semantic tier stubbed, Shadow AI incomplete |
| **Business Model** | B+ | Smart buyer repositioning, realistic pricing, pricing gap in mid-market |
| **Team & Execution Risk** | C+ | Early-stage team, no co-founder, no domain validation |
| **Competitive Moat** | B- | First-mover in niche, but defensibility is speed + domain depth, not IP |

**Verdict: Conditionally fundable at pre-seed. High-conviction thesis with addressable execution risks.**

---

## 1. MARKET THESIS & TIMING

### 1.1 The Regulatory Cliff Is Real

This is not a speculative market. Enforcement is active and accelerating:

| Regulation | Status | Enforcement |
|-----------|--------|-------------|
| **EU AI Act** | Full applicability **August 2026** | Fines up to 7% global revenue |
| **Texas TRAIGA** | Effective **January 2026** | State enforcement |
| **Colorado AI Act** | **Live** | Active |
| **SEC 2026 Exam Priorities** | AI risk elevated **above crypto** for first time | Examination-based |
| **Italy vs. OpenAI** | **€15M fine** levied | Demonstrated |
| **FTC "Operation AI Comply"** | **Active** | Federal enforcement |

Key datapoints from the PRD:
- **69%** of regulatory leaders expect AI compliance issues within 12 months
- Only **16%** have fully implemented governance
- The gap between awareness (69%) and infrastructure (16%) is the market

**Assessment:** The regulatory tailwind is not hypothetical. External deadlines (August 2026 EU AI Act enforcement) create urgency that cannot be postponed. This is one of the strongest market-timing arguments we've seen in the AI infrastructure space.

### 1.2 The Positioning Wedge

Amini occupies a genuinely underserved gap:

```
┌─────────────────────┐     ┌─────────────────────┐
│  OBSERVABILITY TOOLS │     │    GRC PLATFORMS     │
│  Langsmith, Arize,   │     │  OneTrust, Collibra, │
│  Braintrust, Maxim   │     │  ServiceNow, Archer  │
│                      │     │                      │
│  ✓ Agent data/traces │     │  ✓ Compliance logic  │
│  ✗ No regulatory     │     │  ✗ No agent data     │
│    mapping           │     │  ✗ Slow to adapt     │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
           │    ┌─────────────────┐     │
           └───►│     AMINI       │◄────┘
                │                 │
                │  ✓ Agent data   │
                │  ✓ Regulatory   │
                │    mapping      │
                │  ✓ Audit-ready  │
                │    evidence     │
                └─────────────────┘
```

The v1→v2 pivot (from "agentic workflow auditor for platform engineers" to "compliance infrastructure for GRC teams") is strategically excellent. Compliance budgets are 3-5x developer tooling budgets for equivalent risk surface.

### 1.3 Competitive Landscape

| Competitor | Core Strength | Why Amini Wins |
|-----------|--------------|----------------|
| **Langsmith** | Prompt tracing, evals | No policy mapping, no audit reports |
| **Arize** | ML monitoring, drift | Model-focused, not regulatory |
| **Braintrust** | Agent evals, quality | Dev-first, no compliance buyer |
| **Fiddler** | Guardrails, audit traces | Reactive (block/flag), not evidentiary |
| **Maxim** | Full lifecycle, gateway | Access control ≠ compliance documentation |
| **OneTrust/Collibra** | Enterprise GRC | Not built for agentic AI, slow to adapt |

**Key insight:** Every competitor starts from either developer experience or traditional data governance. None start from "here is a regulatory requirement; here is how we prove an agent satisfies it."

---

## 2. TECHNICAL DEEP DIVE

### 2.1 Architecture Overview

**Monorepo structure** with three well-separated packages:

| Package | Stack | LOC | Tests | Maturity |
|---------|-------|-----|-------|----------|
| **SDK** (Python) | httpx, Pydantic, background threads | ~1,500 | 57 | Production-ready beta |
| **Backend** (FastAPI) | SQLAlchemy async, Alembic, PostgreSQL | ~2,500 | 26+ | Production-ready with critical fixes |
| **Frontend** (React/TS) | TanStack Query, Tailwind, Vite | ~2,200 | 0 | Production-ready UI |
| **Total** | | **~8,400** | **83** | |

CI/CD pipeline via GitHub Actions. Docker Compose for multi-service deployment. Makefile with 12 development targets.

### 2.2 SDK Assessment (7.4/10)

**Strengths (impressive for early-stage):**
- Decorator-first design (`@amini.trace`, `@amini.enforce`) — excellent developer experience
- Thread-safe background event emission via daemon thread + queue
- Safe policy DSL with recursive descent (no `eval()`)
- Exponential backoff with jitter on transport failures
- Comprehensive condition evaluation (12 operators including regex, in_list)
- Minimal dependencies (httpx + pydantic only)
- 57 unit tests covering core functionality

**Weaknesses:**
- Async decorator support implemented but **untested** (no pytest-asyncio tests exist)
- LangChain integration handler has **zero tests**
- At-most-once delivery semantics — events lost on crash/queue overflow
- Silent failures on queue overflow (logged but not observable to developers)
- Policy registration requires accessing private `_policy_cache` (DX issue)
- No policy hot-reload from backend

**Verdict:** Solid for MVP. Core tracing and enforcement work well. Needs hardening for mission-critical compliance auditing (delivery guarantees, observability API).

### 2.3 Backend Assessment (7.2/10)

**Strengths:**
- Clean async/await patterns throughout
- Excellent schema design with metadata/payload tier separation
- Zero raw SQL — all parameterized via SQLAlchemy ORM
- Pre-seeded regulatory templates (EU AI Act: 8 requirements, SOC 2: 6 criteria)
- Comprehensive API surface (26+ endpoints across v1 and v2)
- Proper pagination with bounds checking
- No TODO/FIXME comments (high discipline)

**Critical Bugs Found (3):**

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | **CRITICAL** | `retention_service.py` | References non-existent model `Violation` (should be `PolicyViolation`) and non-existent fields (`RawEvent.server_timestamp`, `AgentSession.started_at`). **Entire retention feature is broken.** |
| 2 | **CRITICAL** | `chain_builder.py:49` | Sets session status as raw string instead of `SessionStatus` enum. Causes downstream validation failures. |
| 3 | **HIGH** | `registry.py:37-40` | Fetches ALL agents then iterates to find one — O(n) instead of indexed lookup. Won't scale past ~1000 agents. |

**Additional Issues:**
- No connection pool configuration (SQLAlchemy defaults)
- No rate limiting on batch ingestion (500 events/request, unlimited frequency)
- No caching layer (regulations queried fresh on every call)
- YAML policy parsing is CPU-bound in async context (blocks event loop)
- Semantic policy tier is stubbed (always returns non-violated)
- No request size limits on event payloads

**Verdict:** Good architecture with addressable bugs. The 3 critical issues must be fixed before any production deployment, but they're straightforward fixes (~2 hours of work).

### 2.4 Frontend Assessment (8.5/10)

**Strengths (the standout package):**
- **Zero `any` usage** — strict TypeScript throughout
- 9 fully functional pages with dual-view mode (Developer vs. Compliance)
- Clean component architecture (16 components, all well-sized)
- TanStack Query for all data fetching with proper pagination
- Custom Tailwind theme with Amini brand colors
- Production build passes (282 KB JS, 17 KB CSS gzipped)
- No XSS vectors (no `dangerouslySetInnerHTML`)

**Feature Surface:**
- Dashboard with compliance/developer toggle
- Session browser with decision replay timeline
- Policy management with tier/severity badges
- Regulatory framework tracking with expandable requirements
- Violation monitoring with severity filtering
- Incident management with remediation tracking
- Agent registry with risk classification
- Audit report generation and viewing

**Weaknesses:**
- No frontend tests (expected for MVP but notable)
- Export JSON/PDF buttons are no-ops
- No authentication layer (backend responsibility)
- Error states not displayed to users (only loading states)

**Verdict:** Impressively complete UI for an early-stage product. This is the most polished package in the monorepo.

### 2.5 Repository Health

| Metric | Value | Assessment |
|--------|-------|------------|
| **Commits** | 23 (all from one contributor) | Active, consistent velocity |
| **LOC** | 8,353 | Right-sized for scope |
| **Test count** | 83 across 14 files | Good breadth, some gaps |
| **CI/CD** | GitHub Actions (3 jobs) | Functional but minimal |
| **Docker** | Multi-service compose | Production-ready |
| **Dependencies** | All stable, recent versions | No supply chain concerns |
| **Code quality** | Ruff (Python), ESLint (TS) | Standards enforced |
| **Documentation** | 371 lines across READMEs | Adequate, not comprehensive |

---

## 3. BUSINESS MODEL ANALYSIS

### 3.1 Pricing Architecture

| Tier | Price | Sessions/mo | Retention | Target | ACV |
|------|-------|------------|-----------|--------|-----|
| **Developer** | Free | 500 | 7 days | Adoption | $0 |
| **Growth** | $1,200/mo | 25,000 | 90 days | Mid-market | $14,400/yr |
| **Enterprise** | Custom | Unlimited | 1 year+ | Regulated enterprise | $80K-$250K/yr |

**Strengths:**
- Usage-based (sessions/month) aligns cost with compliance risk surface
- Freemium enables bottom-up adoption → enterprise upsell
- Enterprise ACV ($80K-$250K) is realistic for compliance infrastructure
- Recurring model matches annual audit cycles

**Concerns:**
- **Pricing gap**: Jump from $14.4K/yr (Growth) to $80K/yr (Enterprise) leaves a $15K-$80K dead zone. Many mid-market finserv firms would find Growth insufficient but Enterprise unaffordable for an unproven vendor.
- 90-day retention on Growth tier may be insufficient for regulatory audits (auditors often need 12+ months)
- Shadow AI detection not segmented into pricing
- No stated strategy for GRC platform integration licensing

### 3.2 Go-to-Market

**Beachhead:** Financial services, mid-market (500-5,000 employees)

**Rationale (sound):**
- SEC 2026 exam priorities explicitly target AI risk
- Highest-penalty regulatory exposure + largest compliance budgets
- SOC 2/SOX/SEC reporting creates recurring documentation requirements
- Small enough to lack dedicated AI governance teams

**Launch Timeline:**

| Phase | Dates | Milestone |
|-------|-------|-----------|
| Core MVP | Apr 1-14 | SDK + policy engine + demo agent + 3-5 discovery calls |
| Dashboard MVP | Apr 15-30 | Compliance dashboard + audit reports + waitlist |
| Multi-framework | May 1-25 | 2nd regulatory template + design partners + YC application |
| Continued Development | May 26+ | Regulatory mapping engine focus, design partner feedback |
| Regulatory event | Aug 2026 | EU AI Act enforcement creates demand spike |
| Validation | Dec 2026 | 3-5 paying customers, 2-3 Enterprise pipeline |

**GTM Risk:** The plan is well-reasoned but the execution window is extremely compressed. The PRD acknowledges "enterprise sales cycles exceed early-stage runway" and mitigates with "regulatory urgency compresses sales cycles" — this is an assumption, not a proven fact.

---

## 4. RISK MATRIX

### Critical Risks (Must Address)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | **Regulatory template validation gap** — Core value prop (audit-ready reports) has NOT been validated with actual SOC 2 auditors or EU regulators | HIGH | CRITICAL | Must validate with audit firms by April 15 (stated goal) |
| 2 | **Small team execution** — Enterprise compliance sales + product development + accelerator applications simultaneously | HIGH | HIGH | Co-founder recruitment (profile still undefined) |
| 3 | **Bandwidth constraint** — Limited capacity during critical growth phase | HIGH | HIGH | Design partner relationships carry momentum; co-founder recruitment |

### High Risks (Monitor Closely)

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 4 | **Competitive response** — Fiddler/Maxim add regulatory mapping in Q2-Q3 2026 | MEDIUM | HIGH | Speed + domain depth; but this is a ticking clock, not a moat |
| 5 | **Design partner acquisition** — Recruiting 2-3 finserv firms as an unfunded startup | HIGH | MEDIUM | Regulatory urgency may help; but no stated strategy |
| 6 | **3 critical backend bugs** — Retention service broken, session status type error, registry O(n) scan | CERTAIN | MEDIUM | ~2 hours of straightforward fixes |
| 7 | **Enterprise pricing credibility** — $80K-$250K ACV for a 2-month-old product | HIGH | MEDIUM | Design partner → case study → paid conversion path |

### Moderate Risks

| # | Risk | Likelihood | Impact |
|---|------|-----------|--------|
| 8 | Regulatory template maintenance velocity vs. regulation fragmentation | MEDIUM | MEDIUM |
| 9 | Shadow AI detection incomplete + privacy concerns | MEDIUM | MEDIUM |
| 10 | At-most-once event delivery — potential audit trail gaps | LOW | HIGH |
| 11 | No async test coverage on SDK (async path untested) | MEDIUM | LOW |
| 12 | Beachhead TAM not quantified | MEDIUM | MEDIUM |

---

## 5. WHAT'S WORKING WELL

1. **Market positioning is exceptional.** The v1→v2 pivot from platform engineer buyer to compliance buyer is one of the smartest repositioning decisions I've seen at this stage. Compliance budgets are larger, competition is lower, and the buyer pain is more acute.

2. **The PRD is VC-grade.** The level of market analysis, competitive mapping, and self-aware risk assessment in the PRD exceeds what we typically see at pre-seed. The founder has done real homework.

3. **Technical architecture is sound.** Metadata/payload tier separation, deterministic vs. semantic policy tiers, middleware (not proxy) enforcement, cross-framework correlation IDs — these are the right architectural decisions.

4. **The frontend is surprisingly complete.** 9 fully functional pages with dual-view mode, zero TypeScript `any` usage, and a polished compliance dashboard. For an early-stage team, this is impressive output.

5. **Regulatory templates are the wedge.** Pre-built EU AI Act (8 requirements) and SOC 2 (6 criteria) templates with policy binding is the feature that separates Amini from every observability tool. This is the moat (if validated).

6. **Code quality is professional.** Zero TODO/FIXME comments, comprehensive type hints, proper async patterns, and 83 tests across the stack. This reads like a larger, more mature team.

---

## 6. WHAT NEEDS IMPROVEMENT

### 6.1 Critical Fixes (Before Any Deployment)

| Fix | Effort | Impact |
|-----|--------|--------|
| Fix retention_service.py broken model/field references | 30 min | Retention feature non-functional |
| Fix chain_builder.py session status enum assignment | 15 min | Session processing breaks |
| Fix registry.py O(n) agent lookup → indexed query | 30 min | Won't scale past 1000 agents |

### 6.2 Product Improvements (Before Design Partner Deployment)

| Improvement | Effort | Rationale |
|-------------|--------|-----------|
| Add rate limiting to batch ingestion endpoint | 2 hrs | DOS vulnerability; 500 events/request unlimited |
| Add connection pool configuration | 1 hr | Production stability |
| Implement caching for regulations/policies | 4 hrs | Performance; these rarely change |
| Validate SDK async path (add tests) | 4 hrs | Untested code path that customers will use |
| Test LangChain integration handler | 4 hrs | Zero tests on advertised integration |
| Add frontend error states | 3 hrs | Users see loading spinners on failure |
| Expose public policy registration API | 1 hr | `_policy_cache.register()` is awkward DX |
| Add atexit hook for SDK shutdown | 30 min | Developers forget to call `shutdown()` |

### 6.3 Business Improvements (Before Fundraise)

| Improvement | Effort | Rationale |
|-------------|--------|-----------|
| **Validate regulatory templates with SOC 2 auditors** | 2-4 weeks | Core value prop is unvalidated; this is make-or-break |
| **Quantify beachhead TAM** | 1 week | How many mid-market finserv firms deploy AI agents? |
| **Add mid-market pricing tier ($25K-$50K)** | 1 day | Bridges Growth→Enterprise gap |
| **Define co-founder profile** | 1 week | "Compliance domain expert" vs. "second technical founder" — pick one |
| **Develop design partner acquisition strategy** | 2 weeks | How to recruit finserv firms; what's the value exchange? |
| **Create a demo environment** | 1 week | VCs and prospects need to see it working |

### 6.4 Architecture Improvements (Post-Funding)

| Improvement | Rationale |
|-------------|-----------|
| Add message queue for event processing reliability | Move beyond at-most-once delivery |
| Implement semantic policy tier (currently stubbed) | Complete the policy engine vision |
| Add distributed tracing with OpenTelemetry | Production observability |
| PostgreSQL migration with proper connection pooling | Scale beyond SQLite |
| Implement audit trail immutability (append-only, signed) | Compliance credibility |
| Add SDK delivery observability API | Developers need to know events arrived |
| Policy hot-reload from backend | Eliminate client restart requirement |
| Multi-jurisdictional routing in data model | Support agents serving EU + US |

---

## 7. INVESTMENT DECISION FRAMEWORK

### Would I Fund This?

**Yes, conditionally.** Here's the framework:

### The Bull Case (Why This Could Be a $100M+ Company)

1. **Regulatory tailwinds are structural, not cyclical.** AI regulation is only expanding. Every new regulation (EU AI Act → state laws → SEC priorities → sector-specific rules) expands Amini's addressable market.

2. **Compliance is a recurring, non-discretionary spend.** Unlike developer tools (which get cut in downturns), compliance infrastructure is mandated by regulation. Amini's revenue would be structurally resilient.

3. **The wedge is genuine.** No one else is starting from "regulatory requirement → agent evidence." Observability tools would need to build an entire compliance layer. GRC platforms would need to build agent instrumentation. Both are 12-18 month efforts.

4. **Enterprise ACV potential is high.** At $80K-$250K per enterprise customer, 100 customers = $8M-$25M ARR. The finserv beachhead alone could sustain a $50M+ company.

5. **Platform potential.** If Amini becomes the compliance layer, it becomes the system of record for AI governance. That's a platform position with network effects (regulatory templates improve with more customers → more data → better templates).

### The Bear Case (Why This Could Fail)

1. **Audit validation is the existential risk.** If SOC 2 auditors and EU regulators don't accept Amini-generated reports as sufficient evidence, the entire product collapses to "another observability tool." This has not been validated.

2. **Small team + enterprise sales = stretched thin.** Enterprise compliance sales cycles are 6-12 months with legal review, security questionnaires, board approval, and procurement processes. A small team cannot simultaneously build product, sell enterprise, and apply to accelerators without additional headcount.

3. **Competitive moat is thin.** The defensibility is domain expertise + speed, not technology. If Fiddler hires a compliance expert and ships regulatory mapping in Q3 2026, Amini's 6-month head start evaporates.

4. **Bandwidth is a real constraint.** Limited development capacity from May 26+ means the product may slow during the critical pre-August-2026 period (EU AI Act enforcement). Part-time development is not a viable scaling strategy.

5. **Shadow AI detection is vaporware.** The PRD positions it as a key differentiator, but the implementation is acknowledged as "not production-grade." Selling an incomplete feature to compliance teams is a credibility risk.

### Investment Terms I'd Consider

| Scenario | Investment | Conditions |
|----------|-----------|------------|
| **Pre-Seed** ($150K-$300K) | **Yes** | Milestone-based: (1) Fix critical bugs, (2) Validate with 2 SOC 2 auditors, (3) Sign 1 design partner by June 2026 |
| **Seed** ($1M-$2M) | **Not yet** | Requires: (1) Auditor validation complete, (2) 2-3 design partners with SDK installed, (3) Co-founder recruited, (4) 1 paying customer |
| **Accelerator** (YC/Techstars) | **Strong fit** | Regulatory timing + clear wedge + technical quality make this a compelling accelerator candidate |

### Key Milestones to De-Risk

```
April 15 ──► Regulatory template validated with 2 SOC 2 auditors
             (If NO: product thesis is unproven — pause investment)
             (If YES: proceed to design partner stage)

May 25 ────► 2-3 finserv design partners with SDK installed
             (If NO: GTM thesis is unproven — consider pivot to PLG)
             (If YES: strong signal; accelerate to seed)

Aug 2026 ──► EU AI Act enforcement creates demand spike
             (If demand materializes: raise seed aggressively)
             (If demand is muted: thesis was wrong on timing)

Dec 2026 ──► 3-5 paying customers (Growth tier)
             (If YES: seed-ready with proven PMF)
             (If NO: reassess market fit and pricing)
```

---

## 8. QUESTIONS FOR THE FOUNDER

### Must-Answer (Before Any Investment)

1. **Have you spoken with SOC 2 auditors about what evidence they would accept?** What specific feedback did you receive on the regulatory templates? (This is the single most important validation question.)

2. **How will you maintain development velocity after May 26+?** Is there a realistic plan for maintaining momentum, or does the product effectively pause?

3. **What is your co-founder strategy?** Do you have candidates? What's the profile — compliance domain expert or second technical founder?

4. **How do you plan to recruit design partners?** Do you have any warm introductions to finserv compliance teams? What's the value exchange?

### Important (Before Seed)

5. What is the quantified TAM for your beachhead (mid-market finserv, 500-5,000 employees, deploying AI agents)?

6. How do you respond if Fiddler or Maxim ships a "regulatory compliance" feature in Q3 2026?

7. Why the pricing gap between Growth ($14.4K/yr) and Enterprise ($80K+)? Would a $30K-$50K mid-market tier accelerate adoption?

8. How do you plan to make audit trails tamper-proof? Compliance teams will ask about immutability.

### Nice-to-Know

9. What's your view on the semantic policy tier? When does it become production-ready?

10. How do you handle multi-jurisdictional compliance (agents serving both EU and US customers)?

---

## 9. COMPARABLE COMPANIES & EXITS

For context on market potential:

| Company | Category | Stage | Valuation/Exit | Relevance |
|---------|----------|-------|----------------|-----------|
| **Vanta** | Compliance automation (SOC 2) | Series C | $2.45B (2025) | Proved compliance infrastructure can reach unicorn status |
| **Drata** | Compliance automation | Series C | $2B+ (2024) | Same market dynamic — regulatory mandate → infrastructure |
| **OneTrust** | Privacy/GRC platform | Series C | $5.3B (2021) | Incumbent that Amini could partner with or compete against |
| **Langsmith** | LLM observability | Seed→Series A | ~$25M+ | Dev-focused; shows agent tooling market is real |
| **Fiddler** | AI observability | Series B | ~$100M+ | Closest competitive overlap |

**Amini's path:** If regulatory templates are validated and the compliance buyer thesis holds, this follows the **Vanta/Drata playbook** — regulation-driven infrastructure that becomes mandatory for audits. Vanta reached $100M ARR in ~4 years with SOC 2 automation. AI governance is a larger, faster-moving regulatory surface.

---

## 10. FINAL VERDICT

### Score Card

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Market Timing & Thesis | 25% | 9/10 | 2.25 |
| Technical Execution | 20% | 7.5/10 | 1.50 |
| Product Completeness | 15% | 7/10 | 1.05 |
| Business Model & Pricing | 15% | 7.5/10 | 1.13 |
| Team & Execution Capacity | 15% | 5/10 | 0.75 |
| Competitive Defensibility | 10% | 6/10 | 0.60 |
| **TOTAL** | **100%** | | **7.28/10** |

The frontend is a shell. Export JSON/PDF buttons don't do anything. The SessionTimeline component renders decisions but there's no actual visual replay — no step-through, no diff view, no timeline scrubber. For the "developer debugging tool that creates pull" thesis in the PRD, this is the gap that matters most. LangSmith's trace viewer is the bar, and right now you're far from it.
The PolicyCache in the SDK has no fetch mechanism. It's a local dict with register() — meaning the developer has to manually hydrate policies. The PRD describes server-synced policies, but there's no polling or push path from backend to SDK. This is the missing link between "SDK installed" and "policies enforced at the edge."
No authentication beyond a static API key in docker-compose (dev-key). The backend checks Authorization: Bearer headers but the key validation is a simple list match. For an enterprise governance product, auth is load-bearing — multi-tenant isolation, RBAC for compliance vs. developer roles, audit trail of who changed what policy. None of that exists yet.
The process_pending_events worker is invoked ad-hoc (no scheduler, no background loop). In production you'd need a cron/celery/arq worker to continuously drain the event queue. The asyncio lock is fine for preventing double-processing but doesn't solve "who calls this function repeatedly."
The semantic judge is registered via a module-level register_semantic_judge(fn) global. This works for a single-process demo but breaks under multi-worker deployments (each worker needs its own registration). More practically, there's no default LLM judge implementation — the hook exists but nothing plugs into it.
Retention service exists but isn't wired into any scheduler. Data growth will be unbounded until someone manually invokes cleanup.
The LangChain integration (integrations/langchain.py) inherits BaseCallbackHandler — I'd want to verify it handles the full callback lifecycle (on_llm_start, on_tool_start, on_chain_error, etc.) and not just a subset.
PRD vs. reality gap:
The PRD is a 37KB, 536-line document that describes a mature product. The implementation covers maybe 30% of what's specified. Regulatory mapping (EU AI Act Article 14 linkage, NIST AI RMF), the agent registry with risk classification, incident management workflows, audit report generation with PDF export — these have backend models and routers scaffolded, but the service logic is skeletal. The frontend pages exist but several are essentially empty CRUD shells.