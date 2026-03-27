# Amini Python SDK

Instrument your AI agents with decision chain tracing.

## Quick Start

```python
from amini import Amini

amini = Amini(api_key="your-key", agent_id="my-agent")

# Auto-instrumentation with decorator
@amini.trace
def handle_request(user_input: str) -> str:
    return agent.run(user_input)

# Explicit instrumentation with context manager
with amini.decision("process-query") as ctx:
    ctx.log_input({"query": user_input})
    result = llm.complete(user_input)
    ctx.log_reasoning({"model": "gpt-4", "tokens": 150})
    ctx.log_output({"response": result})
```

## Installation

```bash
pip install amini
```
