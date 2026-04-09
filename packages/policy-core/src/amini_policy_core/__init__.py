"""Shared policy evaluation core used by both the Amini SDK and backend.

This module is the single source of truth for the condition evaluation DSL.
Both client-side (SDK) and server-side (backend) import from here to guarantee
identical evaluation semantics.
"""

from __future__ import annotations

import re
from typing import Any


def evaluate_condition(condition: dict, context: dict[str, Any]) -> bool:
    """Evaluate a condition dict against a context using safe recursive descent.

    Supports ``and``, ``or``, ``not`` combinators and leaf comparisons with
    ``field``, ``operator``, ``value`` keys.
    """
    if not condition:
        return True
    if "and" in condition:
        return all(evaluate_condition(c, context) for c in condition["and"])
    if "or" in condition:
        return any(evaluate_condition(c, context) for c in condition["or"])
    if "not" in condition:
        return not evaluate_condition(condition["not"], context)

    field = condition.get("field", "")
    operator = condition.get("operator", "")
    expected = condition.get("value")

    actual = resolve_field(field, context)
    return compare(actual, operator, expected)


def resolve_field(field: str, context: dict[str, Any]) -> Any:
    """Resolve a dotted field path against a context dict."""
    parts = field.split(".")
    current: Any = context
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def compare(actual: Any, operator: str, expected: Any) -> bool:
    """Safe comparison without eval()."""
    if actual is None:
        return False
    try:
        if operator == "equals":
            return actual == expected
        elif operator == "not_equals":
            return actual != expected
        elif operator == "greater_than":
            return float(actual) > float(expected)
        elif operator == "less_than":
            return float(actual) < float(expected)
        elif operator == "greater_than_or_equal":
            return float(actual) >= float(expected)
        elif operator == "less_than_or_equal":
            return float(actual) <= float(expected)
        elif operator == "contains":
            return str(expected) in str(actual)
        elif operator == "not_contains":
            return str(expected) not in str(actual)
        elif operator == "matches_regex":
            return bool(re.search(str(expected), str(actual)))
        elif operator == "in_list":
            return actual in (expected if isinstance(expected, list) else [expected])
        elif operator == "not_in_list":
            return actual not in (expected if isinstance(expected, list) else [expected])
    except (ValueError, TypeError):
        return False
    return False
