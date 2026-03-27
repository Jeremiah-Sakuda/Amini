from __future__ import annotations

from typing import Any

from ..client import Amini
from ..context import DecisionContext


class AminiLangChainHandler:
    """LangChain callback handler for Amini tracing."""

    def __init__(self, amini: Amini) -> None:
        self._amini = amini
        self._decisions: dict[str, DecisionContext] = {}

    def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        ctx = self._amini.decision(f"chain:{name}")
        ctx.__enter__()
        ctx.log_input(inputs)
        self._decisions[run_id] = ctx

    def on_chain_end(self, outputs: dict[str, Any], **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.log_output(outputs)
            ctx.__exit__(None, None, None)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.__exit__(type(error), error, error.__traceback__)

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        name = serialized.get("name", "unknown_tool")
        ctx = self._amini.decision(f"tool:{name}")
        ctx.__enter__()
        ctx.log_action("tool_call", {"tool": name, "input": input_str})
        self._decisions[run_id] = ctx

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.log_output({"output": output})
            ctx.__exit__(None, None, None)

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.__exit__(type(error), error, error.__traceback__)

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        ctx = self._amini.decision(f"llm:{name}")
        ctx.__enter__()
        ctx.log_action("llm_call", {"model": name, "prompt_count": len(prompts)})
        self._decisions[run_id] = ctx

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.log_output({"response": str(response)})
            ctx.__exit__(None, None, None)

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        ctx = self._decisions.pop(run_id, None)
        if ctx:
            ctx.__exit__(type(error), error, error.__traceback__)
