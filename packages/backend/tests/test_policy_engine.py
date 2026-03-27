import pytest

from amini_server.services.policy_engine import (
    _compare,
    _evaluate_condition,
    _resolve_field,
    load_policy,
)


def test_load_policy_valid():
    yaml_str = """
name: test-policy
tier: deterministic
enforcement: warn
severity: high
message: Test message
condition:
  field: action_type
  operator: equals
  value: external_api_call
"""
    parsed = load_policy(yaml_str)
    assert parsed["name"] == "test-policy"
    assert parsed["tier"] == "deterministic"


def test_load_policy_missing_fields():
    with pytest.raises(ValueError, match="Missing required fields"):
        load_policy("name: incomplete\ntier: deterministic")


def test_resolve_field_nested():
    ctx = {"session": {"error_count": 5, "status": "active"}}
    assert _resolve_field("session.error_count", ctx) == 5
    assert _resolve_field("session.status", ctx) == "active"
    assert _resolve_field("session.missing", ctx) is None


def test_compare_operators():
    assert _compare(5, "equals", 5)
    assert _compare(5, "not_equals", 3)
    assert _compare(10, "greater_than", 5)
    assert _compare(3, "less_than", 5)
    assert _compare("hello@example.com", "matches_regex", r"@example\.com")
    assert _compare("abc", "contains", "b")
    assert _compare("abc", "not_contains", "z")
    assert _compare("x", "in_list", ["x", "y"])
    assert _compare("z", "not_in_list", ["x", "y"])


def test_evaluate_condition_and():
    cond = {
        "and": [
            {"field": "a", "operator": "equals", "value": 1},
            {"field": "b", "operator": "greater_than", "value": 5},
        ]
    }
    assert _evaluate_condition(cond, {"a": 1, "b": 10})
    assert not _evaluate_condition(cond, {"a": 1, "b": 3})


def test_evaluate_condition_or():
    cond = {
        "or": [
            {"field": "a", "operator": "equals", "value": 1},
            {"field": "b", "operator": "equals", "value": 2},
        ]
    }
    assert _evaluate_condition(cond, {"a": 1, "b": 0})
    assert _evaluate_condition(cond, {"a": 0, "b": 2})
    assert not _evaluate_condition(cond, {"a": 0, "b": 0})


def test_evaluate_condition_not():
    cond = {"not": {"field": "x", "operator": "equals", "value": "bad"}}
    assert _evaluate_condition(cond, {"x": "good"})
    assert not _evaluate_condition(cond, {"x": "bad"})
