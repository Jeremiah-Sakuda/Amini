# Amini Python SDK

Compliance-aware instrumentation for AI agents. Capture decision chains, enforce policies inline, and map agent behavior to regulatory requirements.

## Installation

```bash
pip install amini

# With LangChain support
pip install amini[langchain]
```

## Quick Start

```python
from amini import Amini

amini = Amini(
    api_key="ak_...",
    agent_id="support-agent-v3",
    environment="production",
    regulations=["eu-ai-act", "sox"],
    framework="langchain",
)

# Auto-instrumentation with @trace
@amini.trace
def handle_request(query: str) -> str:
    return agent.run(query)

# Explicit decision context
with amini.decision("process-query") as ctx:
    ctx.log_input({"query": user_input})
    result = llm.complete(user_input)
    ctx.log_reasoning({"model": "gpt-4", "tokens": 150})
    ctx.log_output({"response": result})
```

## Inline Policy Enforcement

The `@enforce` decorator evaluates deterministic policies before function execution. Policies use a safe condition DSL — no `eval()`.

```python
from amini import PolicyRule, PolicyTier, PolicyEnforcement, PolicySeverity

# Register a policy
amini._policy_cache.register(PolicyRule(
    name="max-transfer-amount",
    tier=PolicyTier.DETERMINISTIC,
    enforcement=PolicyEnforcement.BLOCK,
    severity=PolicySeverity.HIGH,
    conditions={
        "field": "kwargs.amount",
        "operator": "greater_than",
        "value": 10000,
    },
))

@amini.enforce("max-transfer-amount")
def transfer_funds(amount: float, recipient: str):
    ...  # Blocked if amount > 10000
```

Enforcement modes:
- `BLOCK` — Raises `PolicyViolationError`, prevents execution
- `WARN` — Logs warning, allows execution
- `LOG_ONLY` — Emits violation event silently

## Cross-Framework Tracing

Correlation IDs propagate across framework boundaries for unified decision chains:

```python
@amini.trace(framework="langchain")
def langchain_step(query):
    ...

@amini.trace(framework="crewai")
def crewai_step(task):
    ...
```

## LangChain Integration

```python
from amini.integrations.langchain import AminiLangChainHandler

handler = AminiLangChainHandler(amini)

# Use with any LangChain component
chain.invoke({"input": "..."}, config={"callbacks": [handler]})
```

## Configuration

| Parameter | Env Var | Default | Description |
|-----------|---------|---------|-------------|
| `api_key` | `AMINI_API_KEY` | `""` | API key for backend authentication |
| `agent_id` | `AMINI_AGENT_ID` | `""` | Unique agent identifier |
| `environment` | `AMINI_ENVIRONMENT` | `"development"` | Deployment environment |
| `base_url` | `AMINI_BASE_URL` | `"http://localhost:8000"` | Backend API URL |
| `regulations` | `AMINI_REGULATIONS` | `[]` | Comma-separated regulation IDs |
| `framework` | `AMINI_FRAMEWORK` | `""` | Agent framework identifier |

## Sessions

Sessions group related decisions into auditable units:

```python
session = amini.start_session(
    correlation_id="trace-123",  # Optional cross-framework ID
    user_context={"user_id": "u-456"},
    metadata={"request_type": "support"},
)

# ... agent work ...

amini.end_session(status="completed")
```
