from __future__ import annotations

from typing import Any

try:
    from langchain_core.callbacks import BaseCallbackHandler

    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

from ..client import Amini
from ..context import DecisionContext

# Use BaseCallbackHandler as the base class when langchain is installed,
# otherwise fall back to a plain object so the module can still be imported.
_Base: type = BaseCallbackHandler if _HAS_LANGCHAIN else object


class AminiLangChainHandler(_Base):  # type: ignore[misc]
    """LangChain callback handler for Amini tracing.

    Inherits from ``langchain_core.callbacks.BaseCallbackHandler`` when
    langchain-core is installed, ensuring full compatibility with
    LangChain's ``callbacks=[handler]`` pattern.
    """

    def __init__(self, amini: Amini) -> None:
        if _HAS_LANGCHAIN:
            super().__init__()
        self._amini = amini
        self._decisions: dict[str, DecisionContext] = {}

    def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], **kwargs: Any) -> None:
        run_id = str(kwargs.get("run_id", ""))
        parent_run_id = str(kwargs.get("parent_run_id", "")) if kwargs.get("parent_run_id") else None
        name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        ctx = self._amini.decision(f"chain:{name}", parent_decision_id=parent_run_id)
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
        parent_run_id = str(kwargs.get("parent_run_id", "")) if kwargs.get("parent_run_id") else None
        name = serialized.get("name", "unknown_tool")
        ctx = self._amini.decision(f"tool:{name}", parent_decision_id=parent_run_id)
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
        parent_run_id = str(kwargs.get("parent_run_id", "")) if kwargs.get("parent_run_id") else None
        name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        ctx = self._amini.decision(f"llm:{name}", parent_decision_id=parent_run_id)
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
