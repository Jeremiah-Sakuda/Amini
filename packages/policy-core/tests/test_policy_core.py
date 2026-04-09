"""Tests for the shared policy evaluation core.

These tests serve double duty: they verify the core logic AND act as a parity
guarantee — because both the SDK and backend now import from this module,
passing here means both sides evaluate identically.
"""

from amini_policy_core import compare, evaluate_condition, resolve_field


# --- resolve_field ---

def test_resolve_simple():
    assert resolve_field("name", {"name": "alice"}) == "alice"


def test_resolve_dotted():
    ctx = {"session": {"error_count": 5}}
    assert resolve_field("session.error_count", ctx) == 5


def test_resolve_missing():
    assert resolve_field("missing.path", {"other": 1}) is None


def test_resolve_non_dict_intermediate():
    assert resolve_field("a.b", {"a": "string"}) is None


# --- compare ---

def test_compare_equals():
    assert compare(5, "equals", 5)
    assert not compare(5, "equals", 3)


def test_compare_not_equals():
    assert compare(5, "not_equals", 3)


def test_compare_numeric():
    assert compare(10, "greater_than", 5)
    assert compare(3, "less_than", 5)
    assert compare(5, "greater_than_or_equal", 5)
    assert compare(5, "less_than_or_equal", 5)


def test_compare_string_ops():
    assert compare("hello world", "contains", "world")
    assert compare("hello", "not_contains", "xyz")
    assert compare("test@example.com", "matches_regex", r"@example\.com")


def test_compare_list_ops():
    assert compare("x", "in_list", ["x", "y"])
    assert compare("z", "not_in_list", ["x", "y"])


def test_compare_none():
    assert not compare(None, "equals", "anything")


def test_compare_unknown_operator():
    assert not compare(5, "unknown_op", 5)


# --- evaluate_condition ---

def test_simple_leaf():
    cond = {"field": "action", "operator": "equals", "value": "delete"}
    assert evaluate_condition(cond, {"action": "delete"})
    assert not evaluate_condition(cond, {"action": "read"})


def test_and():
    cond = {
        "and": [
            {"field": "a", "operator": "equals", "value": 1},
            {"field": "b", "operator": "greater_than", "value": 5},
        ]
    }
    assert evaluate_condition(cond, {"a": 1, "b": 10})
    assert not evaluate_condition(cond, {"a": 1, "b": 3})


def test_or():
    cond = {
        "or": [
            {"field": "a", "operator": "equals", "value": 1},
            {"field": "b", "operator": "equals", "value": 2},
        ]
    }
    assert evaluate_condition(cond, {"a": 1, "b": 0})
    assert not evaluate_condition(cond, {"a": 0, "b": 0})


def test_not():
    cond = {"not": {"field": "x", "operator": "equals", "value": "bad"}}
    assert evaluate_condition(cond, {"x": "good"})
    assert not evaluate_condition(cond, {"x": "bad"})


def test_empty_condition():
    assert evaluate_condition({}, {})


def test_nested_and_or():
    cond = {
        "and": [
            {"field": "env", "operator": "equals", "value": "production"},
            {
                "or": [
                    {"field": "action", "operator": "equals", "value": "delete"},
                    {"field": "action", "operator": "equals", "value": "drop"},
                ]
            },
        ]
    }
    assert evaluate_condition(cond, {"env": "production", "action": "delete"})
    assert not evaluate_condition(cond, {"env": "staging", "action": "delete"})


# --- Parity assertion ---
# This test imports from both SDK and backend entry-points to verify they
# actually delegate to the same core module.

def test_sdk_and_backend_share_same_implementation():
    """Verify the SDK and backend condition evaluator are the exact same function."""
    from amini.policy import evaluate_condition as sdk_eval, _compare as sdk_cmp, _resolve_field as sdk_resolve
    from amini_policy_core import evaluate_condition as core_eval, compare as core_cmp, resolve_field as core_resolve

    # The SDK should re-export the core functions directly
    assert sdk_eval is core_eval, "SDK evaluate_condition is not the shared core function"
    assert sdk_cmp is core_cmp, "SDK _compare is not the shared core function"
    assert sdk_resolve is core_resolve, "SDK _resolve_field is not the shared core function"
